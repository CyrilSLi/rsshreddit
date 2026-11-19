# rsshreddit

Restore subreddit RSS feeds with a simple local server

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py > /dev/null 2>&1 & disown
```

This starts a server on `localhost:12866`. The process name is `rsshreddit` if you want to kill it later.

Access the feeds using the same structure as before, e.g. `http://localhost:12866/r/AskReddit/.rss`

## Troubleshooting

- Sometimes feeds will not load properly (likely due to web security measures), refreshing usually fixes the issue. 
- View debug screenshots per subreddit in the `debug_screenshots` folder.