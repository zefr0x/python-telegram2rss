"""Telegram channel class."""
from typing import Optional
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from requests import session as requests_session, sessions as requests_sessions

from .telegram_types import (
    TEXT,
    PHOTO,
    VIDEO,
    VOICE,
    DOCUMENT,
    LOCATION,
    LOCATION_LATITUDE,
    LOCATION_LONGITUDE,
    POLL,
    STICKER,
    # STICKER_PACKS,
    UNSUPPORTED_MEDIA,
    CHANNEL_TITLE,
    CHANNEL_DESCRIPTION,
    CHANNEL_IMAGE,
    CHANNEL_COUNTERS_VALUES,
    CHANNEL_COUNTERS_TYPES,
    MESSAGE_OWNER,
    MESSAGE_AUTHOR,
    MESSAGE_DATE,
    MESSAGE_VIEWS,
    MESSAGE_VOTERS,
    MESSAGE_NUMBER,
    MESSAGE_FORWARDED_FROM_NAME,
    VIDEO_ELEMENT,
    VIDEO_DURATION,
    VIDEO_THUMB,
    VOICE_URL,
    VOICE_DURATION,
    DOCUMENT_TITLE,
    DOCUMENT_SIZE,
    POLL_QUESTION,
    POLL_TYPE,
    POLL_OPTIONS,
    POLL_OPTION_PERCENT,
    POLL_OPTION_VALUE,
    UNSUPPORTED_MEDIA_URL,
    STICKER_SHAPE,
    STICKER_IMAGE,
)

from . import conversions


TELEGRAM_URL = "https://t.me"
TELEGRAM_ICON = "https://telegram.org/img/apple-touch-icon.png"


class FeedEnd(Exception):
    """Error to be raised after pulling all the messages from the channel."""


class TGChannel:
    """
    Telegram channel class.

    ...

    Attributes
    ----------
    channel_id : str
        The Telegram channel id.
    session_object : requests.sessions.Session
        Session object from the requests library for the ability of using proxy for example.

    Methods
    -------
    fetch_to_python()
        Fetch data from telegram to python list.
    """

    def __init__(
        self, channel_id: str, session_object: requests_sessions.Session = None
    ):
        """Init method for the Telegram channel class."""
        self.channel_id = channel_id
        # Where we stopped at the last fetch process.
        self.position: Optional[str] = None

        if not session_object:
            self.session_object = requests_session()
        else:
            self.session_object = session_object

        self.channel_url = f"{TELEGRAM_URL}/s/{self.channel_id}"

        self.channel_title: Optional[str] = None
        self.channel_description: Optional[str] = None
        self.channel_image_url: Optional[str] = None
        self.channel_subscribers_count: int = 0
        self.channel_photos_count: int = 0
        self.channel_videos_count: int = 0
        self.channel_files_count: int = 0
        self.channel_links_count: int = 0

    def fetch_to_python(self, pages_to_fetch=1) -> tuple:
        """
        Get html code using requests then get the data from it.

        Parameters
        ----------
        pages_to_fetch : str
            The number of pages to fetch from the telegram channel.
        """
        if self.position == "0":
            raise FeedEnd("All the pages were already fetched from the channel.")

        all_bubbles = []

        for _ in range(pages_to_fetch):
            params = {"before": self.position}
            # TODO: Get data directly with a request like in the javascript,
            # rather then downaloding the whole page.
            source = self.session_object.get(self.channel_url, params=params).text
            soup = BeautifulSoup(source, "lxml")

            bubbles = soup.select(".tgme_widget_message_bubble")
            bubbles.reverse()
            all_bubbles += bubbles
            try:
                self.position = urlparse(
                    soup.find("link", {"rel": "prev"})["href"]
                ).query.split("=")[1]
            except (TypeError, KeyError):
                self.position = "0"
                break

        # Get channel meta data if they were not fetched before.
        if self.channel_title is None:
            # We can access the soup for the last page in the previous for loop.
            self.channel_title = soup.select_one(CHANNEL_TITLE.selector).text
        if self.channel_description is None:
            self.channel_description = soup.select_one(
                CHANNEL_DESCRIPTION.selector
            ).text
        if self.channel_image_url is None:
            try:
                self.channel_image_url = soup.select_one(CHANNEL_IMAGE.selector)["src"]
            except TypeError:
                self.channel_image_url = TELEGRAM_ICON

        # Get channel counters and covert there values to integers.
        for counter_type, counter_value in [
            (type_.text, counter_value_to_int(count.text))
            for type_, count in zip(
                soup.select(CHANNEL_COUNTERS_TYPES.selector),
                soup.select(CHANNEL_COUNTERS_VALUES.selector),
            )
        ]:
            if counter_type in ("subscriber", "subscribers"):
                self.channel_subscribers_count = counter_value
            elif counter_type in ("photo", "photos"):
                self.channel_photos_count = counter_value
            elif counter_type in ("video", "videos"):
                self.channel_videos_count = counter_value
            elif counter_type in ("file", "files"):
                self.channel_files_count = counter_value
            elif counter_type in ("link", "links"):
                self.channel_links_count = counter_value

        all_messages: list = []

        for bubble in all_bubbles:
            message = {}

            # Get message meta data.
            number = bubble.select_one(MESSAGE_NUMBER.selector)["href"].split("/")[4]
            owner = bubble.select_one(MESSAGE_OWNER.selector).text
            date = bubble.select_one(MESSAGE_DATE.selector)["datetime"]
            try:
                author = bubble.select_one(MESSAGE_AUTHOR.selector).text
            except AttributeError:
                author = None
            try:
                views = bubble.select_one(MESSAGE_VIEWS.selector).text
            except AttributeError:
                views = None
            try:
                votes = bubble.select_one(MESSAGE_VOTERS.selector).text
            except AttributeError:
                votes = None
            try:
                forwarded_from_name = bubble.select_one(MESSAGE_FORWARDED_FROM_NAME.selector).text
            except AttributeError:
                forwarded_from_name = None
            message.update(
                {
                    MESSAGE_NUMBER.name: number,
                    MESSAGE_OWNER.name: owner,
                    MESSAGE_AUTHOR.name: author,
                    MESSAGE_DATE.name: date,
                    MESSAGE_VIEWS.name: views,
                    MESSAGE_VOTERS.name: votes,
                    MESSAGE_FORWARDED_FROM_NAME.name: forwarded_from_name,
                }
            )

            contents = []

            # Get text.
            texts = bubble.select(TEXT.selector)
            for text in texts:
                contents.append({"type": TEXT.name, "content": text.text})

            # Get photos urls.
            photos = bubble.select(PHOTO.selector)
            for photo in photos:
                # TODO: proxy photons and sava them as base64.
                photo = photo["style"].split("'")[1]
                contents.append({"type": PHOTO.name, "url": photo})

            # Get videos urls, thumbnails and durations.
            videos = bubble.select(VIDEO.selector)
            for video in videos:
                video_url = video.select_one(VIDEO_ELEMENT.selector)["src"]
                # TODO: proxy video thumbnail and sava it as base64.
                video_thumb_url = video.select_one(VIDEO_THUMB.selector)["style"].split(
                    "'"
                )[1]
                video_duration = video.select_one(VIDEO_DURATION.selector).text
                contents.append(
                    {
                        "type": VIDEO.name,
                        "url": video_url,
                        VIDEO_THUMB.name: video_thumb_url,
                        VIDEO_DURATION.name: video_duration,
                    }
                )

            # Get voices urls and durations.
            voices = bubble.select(VOICE.selector)
            for voice in voices:
                voice_url = voice.select_one(VOICE_URL.selector)["src"]
                voice_duration = voice.select_one(VOICE_DURATION.selector).text

                contents.append(
                    {
                        "type": VOICE.name,
                        "url": voice_url,
                        VOICE_DURATION.name: voice_duration,
                    }
                )

            # Get documents urls and sizes.
            documents = bubble.select(DOCUMENT.selector)
            for document in documents:
                document_url = document["href"]
                document_title = document.select_one(DOCUMENT_TITLE.selector).text
                document_size = document.select_one(DOCUMENT_SIZE.selector).text
                contents.append(
                    {
                        "type": DOCUMENT.name,
                        "url": document_url,
                        DOCUMENT_TITLE.name: document_title,
                        DOCUMENT_SIZE.name: document_size,
                    }
                )

            # Get locations.
            locations = bubble.select(LOCATION.selector)
            for location in locations:
                url = location["href"]
                # Convert URL from google maps to openstreet map and get longuitude and latitude.
                query = parse_qs(urlparse(url).query)
                q = query["q"][0]
                zoom = query["z"][0]
                latitude, longitude = tuple(q.split(","))
                url = (
                    "https://www.openstreetmap.org/"
                    + f"?lat={latitude}&lon={longitude}&zoom={zoom}&layers=M"
                )
                contents.append(
                    {
                        "type": LOCATION.name,
                        "url": url,
                        LOCATION_LATITUDE.name: latitude,
                        LOCATION_LONGITUDE.name: longitude,
                    }
                )

            # Get polls.
            polls = bubble.select(POLL.selector)
            for poll in polls:
                poll_question = poll.select_one(POLL_QUESTION.selector).text
                poll_type = poll.select_one(POLL_TYPE.selector).text

                poll_options = []

                options = poll.select(POLL_OPTIONS.selector)
                for option in options:
                    option_percent = option.select_one(
                        POLL_OPTION_PERCENT.selector
                    ).text
                    option_value = option.select_one(POLL_OPTION_VALUE.selector).text
                    poll_options.append(
                        {
                            POLL_OPTION_PERCENT.name: option_percent,
                            POLL_OPTION_VALUE.name: option_value,
                        }
                    )

                contents.append(
                    {
                        "type": POLL.name,
                        POLL_QUESTION.name: poll_question,
                        POLL_TYPE.name: poll_type,
                        POLL_OPTIONS.name: poll_options,
                    }
                )

            # Get stickers
            stickers = bubble.select(STICKER.selector)
            for sticker in stickers:
                sticker_shape = sticker["style"].split("'")[1]  # base64 svg image
                # TODO: proxy image
                sticker_image = sticker["data-webp"]
                contents.append(
                    {
                        "type": STICKER.name,
                        STICKER_SHAPE.name: sticker_shape,
                        STICKER_IMAGE.name: sticker_image,
                    }
                )

            # Get stickers packs
            # stickers = bubble.select(STICKER.selector)
            # for sticker in stickers:
            #     # Can't be implemented since we cant access them via the web interface.
            #     pass

            # TODO: Improve selector since it work with normal stickers also.
            unsupported_medias = bubble.select(UNSUPPORTED_MEDIA.selector)
            for media in unsupported_medias:
                try:
                    url = media.select_one(UNSUPPORTED_MEDIA_URL.selector)["href"]
                except KeyError:
                    continue
                contents.append(
                    {
                        "type": UNSUPPORTED_MEDIA.name,
                        "url": url,
                    }
                )

            message.update({"contents": contents})
            all_messages.append(message)
        return tuple(all_messages)

    def fetch_to_rss(self, pages_to_fetch: int = 1, pretty: bool = False):
        """Fetch channel to python then convert them to rss feed."""
        messages = self.fetch_to_python(pages_to_fetch)
        return conversions.python_to_feed_generator(
            self.channel_id,
            self.channel_title,
            self.channel_description,
            self.channel_image_url,
            messages,
        ).rss_str(pretty=pretty)

    # def fetch_to_atom(self, pages_to_fetch: int = 1):
    #     """Fetch channel to python then convert them to atom feed."""
    #     messages = self.fetch_to_python(pages_to_fetch)
    #     return conversions.python_to_feed_generator(
    #         self.channel_id,
    #         self.channel_title,
    #         self.channel_description,
    #         self.channel_image_url,
    #         messages,
    #     ).atom_str()


counter_values_prefixes = (
    ("CEN", 1e303),
    ("GO", 1e100),
    ("QIT", 1e48),
    ("QAT", 1e45),
    ("TE", 1e42),
    ("DU", 1e39),
    ("UN", 1e36),
    ("DE", 1e33),
    ("NO", 1e30),
    ("OC", 1e27),
    ("SP", 1e24),
    ("SX", 1e21),
    ("QI", 1e18),
    ("QA", 1e15),
    ("T", 1e12),
    ("B", 1e9),
    ("M", 1e6),
    ("K", 1e3),
)


def counter_value_to_int(x: str) -> int:
    """Convert a string from 3.4M or 1M or 3K or 2B to an integer."""
    x = x.upper()

    for prefix, expression in counter_values_prefixes:
        if prefix in x:
            return int(float(x.replace(prefix, "")) * expression)

    return int(x)
