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

        fe.description("")

        # TODO Write in the title if the message was forwarded.
        for content in message["contents"]:
            content_type = content.get("type")
            if content_type == telegram_types.TEXT.name:
                fe.title(content.get("content"))
                fe.description(fe.description() + f'<p>{content.get("content")}</p>')
            elif content_type == telegram_types.PHOTO.name:
                if not fe.title():
                    fe.title(f"{telegram_types.PHOTO.name} {fe.id()}")
                fe.description(
                    fe.description()
                    + f'<img src="{content.get("url")}" style="max-width: 400px;"/>'
                )
            elif content_type == telegram_types.VIDEO.name:
                if not fe.title():
                    fe.title(f"{telegram_types.VIDEO.name} {fe.id()}")
                fe.description(
                    fe.description()
                    + "<div>"
                    + f'<a href="{content.get("url")}">'
                    + f'<img src="{content.get(telegram_types.VIDEO_THUMB.name)}"'
                    + 'style="display: inline;"/>'
                    + f"<sup>{content.get(telegram_types.VIDEO_DURATION.name)}</sup>"
                    + "</a>"
                    + "</div>"
                )
            elif content_type == telegram_types.VOICE.name:
                if not fe.title():
                    fe.title(f"{telegram_types.VOICE.name} {fe.id()}")
                fe.description(
                    fe.description()
                    + "<div>"
                    + f'<audio src="{content.get("url")}">'
                    + "</div>"
                    + "<div>"
                    + f'<a href="{content.get("url")}">{telegram_types.VOICE.name} </a>'
                    + f"<sub>{content.get(telegram_types.VOICE_DURATION.name)}</sub>"
                    + "</div>"
                )
            elif content_type == telegram_types.DOCUMENT.name:
                if not fe.title():
                    fe.title(f"{telegram_types.DOCUMENT.name} {fe.id()}")
                fe.description(
                    fe.description()
                    + "<div>"
                    + f'<a href="{content.get("url")}">'
                    + f"{content.get(telegram_types.DOCUMENT_TITLE.name)} </a>"
                    + f"<sub>{content.get(telegram_types.DOCUMENT_SIZE.name)}</sub>"
                    + "<div>"
                )
            elif content_type == telegram_types.LOCATION.name:
                if not fe.title():
                    fe.title(f"{telegram_types.LOCATION.name} {fe.id()}")
                fe.description(
                    fe.description()
                    + "<div>"
                    + f'<a href="{content.get("url")}">{telegram_types.LOCATION.name} </a>'
                    + f'<sub>({content.get("latitude")}, {content.get("longitude")})</sub>'
                    + "</div>"
                )
            elif content_type == telegram_types.POLL.name:
                if not fe.title():
                    fe.title(f"{telegram_types.POLL.name} {fe.id()}")
                    # TODO Support polls.
                fe.description(
                    fe.description()
                    + content.get(telegram_types.POLL_QUESTION.name)
                    + content.get(telegram_types.POLL_TYPE.name)
                    + str(content.get(telegram_types.POLL_OPTIONS.name))
                    + message.get(telegram_types.MESSAGE_VOTERS.name)
                )
            elif content_type == telegram_types.STICKER.name:
                if not fe.title():
                    fe.title(f"{telegram_types.STICKER.name} {fe.id()}")
                fe.description(
                    fe.description()
                    + f'<img src="{content.get("sticker_image")}" style="max-width: 400px;"/>'
                )
            elif content_type == telegram_types.UNSUPPORTED_MEDIA.name:
                if not fe.title():
                    fe.title(f"{telegram_types.UNSUPPORTED_MEDIA.name} {fe.id()}")
                fe.description(
                    fe.description()
                    + "<b>"
                    + f'<a href="{content.get("url")}">{telegram_types.UNSUPPORTED_MEDIA.name}</a>'
                    + "</b>"
                )

        if not fe.description():
            fe.description("<b>No Content</b>")

    return fg
