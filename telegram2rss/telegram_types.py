"""Telegram messages types and how to scrape them."""


class Type:
    """Type class to make messages types objects."""

    def __init__(self, name: str, html_class: str, emoji: str):
        """Get type information."""
        self.name = name
        self.html_class = html_class
        self.emoji = emoji


TEXT = Type("text", ".tgme_widget_message_text", "📃")
PHOTO = Type("image", ".tgme_widget_message_photo_wrap", "📷")
VIDEO = Type("video", ".tgme_widget_message_video", "📹")
VOICE = Type("voice", ".tgme_widget_message_voice", "🎤")
DOCUMENT = Type("document", ".tgme_widget_message_document", "📎")
LOCATION = Type("location", ".tgme_widget_message_location", "📍")
POLL = Type("poll", ".tgme_widget_message_poll", "📊")
STICKER = Type("sticker", ".tgme_widget_message_sticker", "🖼️️")
