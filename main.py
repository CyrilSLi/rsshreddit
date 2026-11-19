# Set process title
from setproctitle import setproctitle
setproctitle ("rsshreddit")

# Built-in modules

# Third-party modules
from domonic import domonic
from feedgen.ext.base import BaseEntryExtension, BaseExtension
from feedgen.feed import FeedGenerator
from flask import Flask, Response
from lxml import etree
from seleniumbase import SB
from dotenv import load_dotenv

load_dotenv()
domonic.set_default_parser("html.parser")

class MediaExtension(BaseExtension):
    def extend_ns(self):
        return {"media": MEDIA_NS}

class MediaEntryExtension(BaseEntryExtension):
    def __init__(self):
        self.__url = None
    def thumbnail(self, url=None):
        if url is not None:
            self.__url = url
        return self.__url
    def extend_atom(self, entry):
        if self.__url is not None:
            etree.SubElement(entry, f"{{{MEDIA_NS}}}thumbnail", url=self.__url)

MEDIA_NS = "http://search.yahoo.com/mrss/"
header_template = "<table> <tr><td>"
media_template = ' <a href="{link}"> <img src="{media_thumbnail}" alt="{title}" title="{title}" /> </a> </td><td>'
footer_template = '&#32; submitted by &#32; <a href="{author_url}"> {author_name} </a> <br/> <span><a href="{media_link}">[link]</a></span> &#32; <span><a href="{link}">[comments]</a></span> </td></tr></table>'

app = Flask(__name__)

@app.route("/r/<subreddit>/.rss")
def generate_rss(subreddit):
    target = f"https://www.reddit.com/svc/shreddit/community-more-posts/new/?name={subreddit}"

    with SB(uc=True, headless=True, use_chromium=True) as sb:
        sb.activate_cdp_mode()
        sb.goto("https://www.reddit.com")
        sb.refresh()
        sb.wait_for_element("body")

        sb.goto(target)
        sb.wait_for_element("body")
        sb.save_screenshot(f"{subreddit}.png", folder="debug_screenshots")
        doc = domonic.parseString(sb.get_page_source())

    fg = FeedGenerator()
    fg.register_extension("media", extension_class_feed=MediaExtension, extension_class_entry=MediaEntryExtension)

    fg.category(term=subreddit, label=f"r/{subreddit}")
    # fg.updated(datetime.now(timezone.utc))
    fg.icon("https://www.redditstatic.com/icon.png/")
    fg.id(f"r/{subreddit}/.rss")
    fg.link(rel="self", href=f"https://www.reddit.com/r/{subreddit}/.rss")
    fg.link(rel="alternate", href=f"https://www.reddit.com/r/{subreddit}/")
    # fg.logo("LOGO_URL")
    # fg.subtitle("SUBTITLE")
    fg.title(f"r/{subreddit.lower()}")

    for article in doc.getElementsByTagName("article"):
        content = {
            "author_name": "/" +article.querySelector('span[data-testid="nameplate"]').textContent.strip(),
            "author_url": article.querySelector('span[data-testid="nameplate"]').closest("a").getAttribute("href"),
            "content": header_template,
            "id": article.getAttribute("data-post-id"),
            "link": article.querySelector('a[slot="full-post-link"]').getAttribute("href"),
            "title": article.querySelector('a[slot="title"]').textContent.strip(),
            "updated": article.querySelector("faceplate-timeago").getAttribute("ts"),
        }

        post_el = article.querySelector('div[id$="-post-rtjson-content"]')
        if post_el:
            content["content"] += post_el.innerHTML.strip()

        media = article.querySelector('img[src*="preview.redd.it"]')
        if media:
            content.update({
                "media_link": media.parentElement.getAttribute("href") if media.parentElement.tagName == "A" else content["link"],
                "media_thumbnail": media.getAttribute("src")
            })
            content["content"] += media_template.format(**content)
        else:
            content["media_link"] = content["link"] # for footer_template formatting when no media is present

        content["content"] += footer_template.format(**content)

        fe = fg.add_entry()
        fe.author(name=content["author_name"], uri=content["author_url"])
        fe.category(term=subreddit, label=f"r/{subreddit}")
        fe.content(content["content"], type="html")
        fe.id(content["id"])
        if media:
            fe.media.thumbnail(url=content["media_thumbnail"])
        fe.link(href=content["link"])
        fe.updated(content["updated"])
        fe.title(content["title"])

    return Response(fg.atom_str(), 200, {"Content-Type": "application/atom+xml"})

if __name__ == "__main__":
    app.run(port=12866)