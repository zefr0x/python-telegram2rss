"""Telegram channel class."""
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from requests import session as requests_session
from requests import sessions as requests_sessions

from . import conversions
from . import telegram_types


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
        self,
        channel_id: str,
        session_object: Optional[requests_sessions.Session] = None,
    ) -> None:
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

    def fetch_to_python(self, pages_to_fetch: int = 1) -> tuple:
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
                self.position = parse_qs(
                    urlsplit(soup.find("link", {"rel": "prev"})["href"]).query
                )["before"][0]
            except (TypeError, KeyError):
                self.position = "0"
                break

        # Get channel meta data if they were not fetched before.
        if self.channel_title is None:
            # We can access the soup for the last page in the previous for loop.
            self.channel_title = soup.select_one(
                telegram_types.CHANNEL_TITLE.selector
            ).text
        if self.channel_description is None:
            self.channel_description = soup.select_one(
                telegram_types.CHANNEL_DESCRIPTION.selector
            ).text
        if self.channel_image_url is None:
            try:
                self.channel_image_url = soup.select_one(
                    telegram_types.CHANNEL_IMAGE.selector
                )["src"]
            except TypeError:
                self.channel_image_url = TELEGRAM_ICON

        # Get channel counters and covert there values to integers.
        for counter_type, counter_value in [
            (type_.text, counter_value_to_int(count.text))
            for type_, count in zip(
                soup.select(telegram_types.CHANNEL_COUNTERS_TYPES.selector),
                soup.select(telegram_types.CHANNEL_COUNTERS_VALUES.selector),
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
            number = bubble.select_one(telegram_types.MESSAGE_NUMBER.selector)[
                "href"
            ].split("/")[4]
            owner = bubble.select_one(telegram_types.MESSAGE_OWNER.selector).text
            date = bubble.select_one(telegram_types.MESSAGE_DATE.selector)["datetime"]
            try:
                author = bubble.select_one(telegram_types.MESSAGE_AUTHOR.selector).text
            except AttributeError:
                author = None
            try:
                views = bubble.select_one(telegram_types.MESSAGE_VIEWS.selector).text
            except AttributeError:
                views = None
            try:
                votes = bubble.select_one(telegram_types.MESSAGE_VOTERS.selector).text
            except AttributeError:
                votes = None
            try:
                forwarded_from_name = bubble.select_one(
                    telegram_types.MESSAGE_FORWARDED_FROM_NAME.selector
                ).text
            except AttributeError:
                forwarded_from_name = None
            message.update(
                {
                    telegram_types.MESSAGE_NUMBER.name: number,
                    telegram_types.MESSAGE_OWNER.name: owner,
                    telegram_types.MESSAGE_AUTHOR.name: author,
                    telegram_types.MESSAGE_DATE.name: date,
                    telegram_types.MESSAGE_VIEWS.name: views,
                    telegram_types.MESSAGE_VOTERS.name: votes,
                    telegram_types.MESSAGE_FORWARDED_FROM_NAME.name: forwarded_from_name,
                }
            )

            contents = []

            # Get text.
            texts = bubble.select(telegram_types.TEXT.selector)
            for text in texts:
                contents.append(
                    {"type": telegram_types.TEXT.name, "content": text.text}
                )

            # Get photos urls.
            photos = bubble.select(telegram_types.PHOTO.selector)
            for photo in photos:
                # TODO: proxy photons and sava them as base64.
                photo = photo["style"].split("'")[1]
                contents.append({"type": telegram_types.PHOTO.name, "url": photo})

            # Get videos urls, thumbnails and durations.
            videos = bubble.select(telegram_types.VIDEO.selector)
            for video in videos:
                video_url = video.select_one(telegram_types.VIDEO_ELEMENT.selector)[
                    "src"
                ]
                # TODO: proxy video thumbnail and sava it as base64.
                video_thumb_url = video.select_one(telegram_types.VIDEO_THUMB.selector)[
                    "style"
                ].split("'")[1]
                video_duration = video.select_one(
                    telegram_types.VIDEO_DURATION.selector
                ).text
                contents.append(
                    {
                        "type": telegram_types.VIDEO.name,
                        "url": video_url,
                        telegram_types.VIDEO_THUMB.name: video_thumb_url,
                        telegram_types.VIDEO_DURATION.name: video_duration,
                    }
                )

            # Get voices urls and durations.
            voices = bubble.select(telegram_types.VOICE.selector)
            for voice in voices:
                voice_url = voice.select_one(telegram_types.VOICE_URL.selector)["src"]
                voice_duration = voice.select_one(
                    telegram_types.VOICE_DURATION.selector
                ).text

                contents.append(
                    {
                        "type": telegram_types.VOICE.name,
                        "url": voice_url,
                        telegram_types.VOICE_DURATION.name: voice_duration,
                    }
                )

            # Get documents urls and sizes.
            documents = bubble.select(telegram_types.DOCUMENT.selector)
            for document in documents:
                document_url = document["href"]
                document_title = document.select_one(
                    telegram_types.DOCUMENT_TITLE.selector
                ).text
                document_size = document.select_one(
                    telegram_types.DOCUMENT_SIZE.selector
                ).text
                contents.append(
                    {
                        "type": telegram_types.DOCUMENT.name,
                        "url": document_url,
                        telegram_types.DOCUMENT_TITLE.name: document_title,
                        telegram_types.DOCUMENT_SIZE.name: document_size,
                    }
                )

            # Get locations.
            locations = bubble.select(telegram_types.LOCATION.selector)
            for location in locations:
                url = location["href"]
                # Convert URL from google maps to openstreet map and get longuitude and latitude.
                query = parse_qs(urlsplit(url).query)
                q = query["q"][0]
                zoom = query["z"][0]
                latitude, longitude = tuple(q.split(","))
                url = (
                    "https://www.openstreetmap.org/"
                    + f"?lat={latitude}&lon={longitude}&zoom={zoom}&layers=M"
                )
                contents.append(
                    {
                        "type": telegram_types.LOCATION.name,
                        "url": url,
                        telegram_types.LOCATION_LATITUDE.name: latitude,
                        telegram_types.LOCATION_LONGITUDE.name: longitude,
                    }
                )

            # Get polls.
            polls = bubble.select(telegram_types.POLL.selector)
            for poll in polls:
                poll_question = poll.select_one(
                    telegram_types.POLL_QUESTION.selector
                ).text
                poll_type = poll.select_one(telegram_types.POLL_TYPE.selector).text

                poll_options = []

                options = poll.select(telegram_types.POLL_OPTIONS.selector)
                for option in options:
                    option_percent = option.select_one(
                        telegram_types.POLL_OPTION_PERCENT.selector
                    ).text
                    option_value = option.select_one(
                        telegram_types.POLL_OPTION_VALUE.selector
                    ).text
                    poll_options.append(
                        {
                            telegram_types.POLL_OPTION_PERCENT.name: option_percent,
                            telegram_types.POLL_OPTION_VALUE.name: option_value,
                        }
                    )

                contents.append(
                    {
                        "type": telegram_types.POLL.name,
                        telegram_types.POLL_QUESTION.name: poll_question,
                        telegram_types.POLL_TYPE.name: poll_type,
                        telegram_types.POLL_OPTIONS.name: poll_options,
                    }
                )

            # Get stickers
            stickers = bubble.select(telegram_types.STICKER.selector)
            for sticker in stickers:
                sticker_shape = sticker["style"].split("'")[1]  # base64 svg image
                # TODO: proxy image
                sticker_image = sticker["data-webp"]
                contents.append(
                    {
                        "type": telegram_types.STICKER.name,
                        telegram_types.STICKER_SHAPE.name: sticker_shape,
                        telegram_types.STICKER_IMAGE.name: sticker_image,
                    }
                )

            # Get stickers packs
            # stickers = bubble.select(STICKER.selector)
            # for sticker in stickers:
            #     # Can't be implemented since we cant access them via the web interface.
            #     pass

            # TODO: Improve selector since it work with normal stickers also.
            unsupported_medias = bubble.select(
                telegram_types.UNSUPPORTED_MEDIA.selector
            )
            for media in unsupported_medias:
                try:
                    url = media.select_one(
                        telegram_types.UNSUPPORTED_MEDIA_URL.selector
                    )["href"]
                except KeyError:
                    continue
                contents.append(
                    {
                        "type": telegram_types.UNSUPPORTED_MEDIA.name,
                        "url": url,
                    }
                )

            message.update({"contents": contents})
            all_messages.append(message)
        return tuple(all_messages)

    def fetch_to_rss(self, pages_to_fetch: int = 1, pretty: bool = False) -> str:
        """Fetch channel to python then convert them to rss feed."""
        messages = self.fetch_to_python(pages_to_fetch)
        return conversions.python_to_feed_generator(
            self.channel_id,
            self.channel_title,
            self.channel_description,
            self.channel_image_url,
            messages,
        ).rss_str(pretty=pretty)

    # TODO: Enable atom feed.
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
