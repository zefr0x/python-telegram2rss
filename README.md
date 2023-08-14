# telegram2rss

[![Downloads count all](https://static.pepy.tech/personalized-badge/telegram2rss?period=total&units=international_system&left_color=grey&right_color=green&left_text=Downloads)](https://pepy.tech/project/telegram2rss)
[![Downloads count per month](https://static.pepy.tech/personalized-badge/telegram2rss?period=month&units=international_system&left_color=grey&right_color=green&left_text=Downloads/Month)](https://pepy.tech/project/telegram2rss)
[![Downloads count per week](https://static.pepy.tech/personalized-badge/telegram2rss?period=week&units=international_system&left_color=grey&right_color=green&left_text=Downloads/Week)](https://pepy.tech/project/telegram2rss)

![PyPI](https://img.shields.io/pypi/v/telegram2rss)

A python library to fetch data from public Telegram channels to use them as a python object or RSS feed.

## Installation

### From the git repo
```shell
git clone https://github.com/zefr0x/python-telegram2rss.git

cd python-telegram2rss

python3 setup.py install
```

> It is recommended to use a virtual environment.

### pypi
```shell
python3 -m pip install telegram2rss
```

> It is recommended to use a virtual environment.

### AUR
Not available yet...

## Usage
### Fetch to python
```python
import telegram2rss

channel_id = "telegramtips"

channel = telegram2rss.TGChannel(channel_id)

number_of_pages = 3
messages = channel.fetch_to_python(number_of_pages)

# Get some data about the channel after the fetch
print(channel.channel_subscribers_count)
print(channel.channel_title)

# You can also fetch again beginning from the last position
messages2 = channel.fetch_to_python(number_of_pages)
```
#### Using a tor or any other proxy
```python
import telegram2rss
import requests

channel_id = "example"

s = requests.Session()
s.proxies = {'http': "socks5://127.0.0.1:9050",
             'https': "socks5://127.0.0.1:9050"}

channel = telegram2rss.TGChannel(channel_id, session_object=s)
```

> **Warning**
> Images will be included as links, so they will not be proxied unless you are using a proxy in your RSS reader.
> Anyway there is a plan to implement a way to download them and included them as bash64 rather then links.

### Fetch to [RSS](https://en.wikipedia.org/wiki/RSS)
```python
import telegram2rss

channel_id = "example"

channel = telegram2rss.TGChannel("telegramtips")
rss = messages = channel.fetch_to_python(3)

# Decode the text then write it to a rss file:
with open("telegramtips_feed.rss", "w") as f:
    f.writelines(rss.docode()
```

> Some rss readers support reading from a file with a uri like: `file:////path/to/telegramtips_feed.rss`

> You can create a cron job or a systemd timer to run a script every while to update the file.

#### Creating a [flask](https://flask.palletsprojects.com) web app
```python
"""A simple web app to create RSS feed from a telegram channel."""
from flask import Flask
from flask import request

import telegram2rss


app = Flask(__name__)


@app.route('/<channel_id>', methods=['GET'])
def feed(channel_id):
    """Create a channel object then fetch data to rss and return it."""
    channel = telegram2rss.TGChannel(channel_id)
    return channel.fetch_to_rss(int(request.args.get("pages")) or 1).decode()


if __name__ == '__main__':
    app.run()
```
Now you can use `http://127.0.0.1:5000/<channel_id>?pages=<number_or_pages_to_fetch>` in you RSS reader.
