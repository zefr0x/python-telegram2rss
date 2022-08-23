# telegram2rss
A python library to fetch data from public Telegram channels to use them as a python object or RSS feed.

## Installation
To be added later...

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

#### Creating a flask web app
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

