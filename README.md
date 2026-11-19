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

Access the feeds using the same URL structure as before, e.g. `http://localhost:12866/r/AskReddit/.rss`

You can add this alias to your shell configuration file to start the server with a single command (replace the placeholders with your local paths):

```bash
alias rsshreddit='(source <virtualenv_path>/bin/activate; cd <path_to_rsshreddit>/rsshreddit; python main.py > /dev/null 2>&1 & disown)'
```

**Note:** Always start the server from the same directory as the `main.py` file.

## Troubleshooting

- Sometimes feeds will not load properly (likely due to web security measures), refreshing usually fixes the issue. 
- View debug screenshots per subreddit in the `debug_screenshots` folder.