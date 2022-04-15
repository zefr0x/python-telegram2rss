"""Telegram data types and how to scrape them."""
from dataclasses import dataclass


@dataclass
class MessageType:
    """Type class to make messages types objects."""

    name: str
    selector: str
    emoji: str


@dataclass
class MetaType:
    """Type class to make meta data types objects."""

    name: str
    selector: str


TEXT = MessageType("text", ".tgme_widget_message_text", "📃")
PHOTO = MessageType("image", ".tgme_widget_message_photo_wrap", "📷")
VIDEO = MessageType("video", ".tgme_widget_message_video_player", "📹")
VOICE = MessageType("voice", ".tgme_widget_message_voice_player", "🎤")
DOCUMENT = MessageType("document", ".tgme_widget_message_document_wrap", "📎")
LOCATION = MessageType("location", ".tgme_widget_message_location_wrap", "📍")
POLL = MessageType("poll", ".tgme_widget_message_poll", "📊")
STICKER = MessageType(
    "sticker", ".tgme_widget_message_sticker_wrap .tgme_widget_message_sticker", "🖼️️"
)
# STICKER_PACKS = MessageType("sticker_packs", "", "📦")
UNSUPPORTED_MEDIA = MessageType(
    "not_supported_media", ".message_media_not_supported", "❔"
)


CHANNEL_TITLE = MetaType("channel_title", ".tgme_channel_info_header_title")
CHANNEL_DESCRIPTION = MetaType("channel_description", ".tgme_channel_info_description")
CHANNEL_IMAGE = MetaType("channel_description", ".tgme_page_photo_image img")
CHANNEL_COUNTERS_VALUES = MetaType(
    "channel_counters_values",
    ".tgme_channel_info_counters .tgme_channel_info_counter .counter_value",
)
CHANNEL_COUNTERS_TYPES = MetaType(
    "channel_counters_type",
    ".tgme_channel_info_counters .tgme_channel_info_counter .counter_type",
)

MESSAGE_AUTHOR = MetaType("author", ".tgme_widget_message_author")
MESSAGE_DATE = MetaType("date", ".tgme_widget_message_date time")
MESSAGE_VIEWS = MetaType("views", ".tgme_widget_message_views")
MESSAGE_VOTERS = MetaType("votes", ".tgme_widget_message_voters")
MESSAGE_NUMBER = MetaType("url", ".tgme_widget_message_date")

VIDEO_DURATION = MetaType("video_duration", ".tgme_widget_message_video_player time")
VIDEO_THUMB = MetaType("video_thumbnail", ".tgme_widget_message_video_thumb")

VOICE_URL = MetaType("voice_url", ".tgme_widget_message_voice audio")
VOICE_DURATION = MetaType(
    "voice_duration",
    ".tgme_widget_message_voice_duration",
)

DOCUMENT_TITLE = MetaType("document_title", ".tgme_widget_message_document_title")
DOCUMENT_SIZE = MetaType("document_size", ".tgme_widget_message_document_extra")

POLL_QUESTION = MetaType("poll_question", ".tgme_widget_message_poll_question")
POLL_TYPE = MetaType("poll_type", ".tgme_widget_message_poll_type")
POLL_OPTIONS = MetaType("poll_options", ".tgme_widget_message_poll_option")
POLL_OPTION_PERCENT = MetaType(
    "poll_option_percent", ".tgme_widget_message_poll_option_percent"
)
POLL_OPTION_VALUE = MetaType(
    "poll_option_value",
    ".tgme_widget_message_poll_option_value .tgme_widget_message_poll_option_text",
)

UNSUPPORTED_MEDIA_URL = MetaType(
    "unsupported_media_url", ".message_media_view_in_telegram"
)
