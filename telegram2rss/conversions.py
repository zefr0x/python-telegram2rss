"""Conversions from python."""
from typing import Optional

from feedgen.feed import FeedGenerator

from . import telegram_types

TELEGRAM_URL = "https://t.me"


def python_to_feed_generator(
    channel_id: str,
    channel_title: Optional[str],
    channel_description: Optional[str],
    channel_image_url: Optional[str],
    messages: tuple,
):
    """From python to rss."""
    fg = FeedGenerator()
    fg.title(channel_title or channel_id)
    fg.link(href=f"{TELEGRAM_URL}/s/{channel_id}", rel="via")
    fg.description(channel_description or channel_id)
    fg.image(channel_image_url)

    for message in messages:
        fe = fg.add_entry()

        fe.id(message.get(telegram_types.MESSAGE_NUMBER.name))
        fe.author({"name": message.get(telegram_types.MESSAGE_AUTHOR.name)})
        fe.published(message.get(telegram_types.MESSAGE_DATE.name))
        fe.link(href=f"{TELEGRAM_URL}/{channel_id}/{fe.id()}", rel="alternate")
        fe.summary()

        # TODO Support multible contents.
        # TODO Write in the title if the message was forwarded.
        for content in message["contents"]:
            content_type = content.get("type")
            if content_type == telegram_types.TEXT.name:
                fe.title(content.get("content"))
                fe.content(content.get("content"))
            elif content_type == telegram_types.PHOTO.name:
                if not fe.title():
                    fe.title(telegram_types.PHOTO.name)
                fe.content(content.get("url"))
            elif content_type == telegram_types.VIDEO.name:
                if not fe.title():
                    fe.title(telegram_types.VIDEO.name)
                fe.content(
                    content.get("url")
                    + content.get("thumbnail")
                    + content.get("duration")
                )
            elif content_type == telegram_types.VOICE.name:
                if not fe.title():
                    fe.title(telegram_types.VOICE.name)
                fe.content(content.get("url") + content.get("duration"))
            elif content_type == telegram_types.DOCUMENT.name:
                if not fe.title():
                    fe.title(telegram_types.DOCUMENT.name)
                fe.content(
                    content.get("url") + content.get("title") + content.get("size")
                )
            elif content_type == telegram_types.LOCATION.name:
                if not fe.title():
                    fe.title(telegram_types.LOCATION.name)
                fe.content(
                    content.get("url")
                    + content.get("latitude")
                    + content.get("longitude")
                )
            elif content_type == telegram_types.POLL.name:
                if not fe.title():
                    fe.title(telegram_types.POLL.name)
                fe.content(
                    content.get("poll_question")
                    + content_type.get("poll_type")
                    + str(content.get("poll_options"))
                    + message.get(telegram_types.MESSAGE_VOTERS.name)
                )
            elif content_type == telegram_types.STICKER.name:
                if not fe.title():
                    fe.title(telegram_types.STICKER.name)
                fe.content(content.get("sticker_shape" + content.get("sticker_image")))
            elif content_type == telegram_types.UNSUPPORTED_MEDIA.name:
                if not fe.title():
                    fe.title(telegram_types.UNSUPPORTED_MEDIA.name)
                fe.content(content.get("url"))

    return fg
