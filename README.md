# telegram2rss
A python library to fetch data from public Telegram channels to use them as a python object or RSS feed.

## Requirements
- python-requests
- python-beautifulsoup4
- python-lxml
- python-feedgen
## Installation
To be added later...

## Usage
### Fetch to python
```python
import telegram2rss

channel_id = "example"

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

### Fetch to python
To be added soon, after this feature is implemented...