"""Unit testing with pytest."""
from xml.etree import ElementTree

import pytest
from requests import Session

import telegram2rss


def test_channel_meta_data():
    """Create a TGChannel object and call fetch_to_python method then test channel meta data.

    This test also covers text and videos parsing.
    """
    channel = telegram2rss.TGChannel(
        "TelegramTips"
    )  # A huge channel that contain texts and videos messages.

    # This also test fetching multiple pages.
    assert channel.fetch_to_python(2)
    # Check if it is a will formed XML.
    # TODO Test it against XML shame (XSD).
    assert ElementTree.fromstring(channel.fetch_to_rss(1))

    assert channel.channel_title
    assert channel.channel_description
    assert (
        channel.channel_image_url.startswith("https://cdn4.telegram-cdn.org/file/")
        and channel.channel_image_url.endswith(".jpg")
    ) or channel.channel_image_url == telegram2rss.channel.TELEGRAM_ICON
    assert channel.channel_subscribers_count >= 0
    assert channel.channel_photos_count >= 0
    assert channel.channel_videos_count >= 0
    assert channel.channel_files_count >= 0
    assert channel.channel_links_count >= 0
    assert channel.channel_url.startswith(telegram2rss.TELEGRAM_URL)


def test_custom_requests_session():
    """Create a custom requests session and use it in TGChannel."""
    assert telegram2rss.TGChannel("TelegramTips", Session()).fetch_to_python(1)


def test_fetching_when_feed_ends():
    """Test if it will raise an exception when there is no more messages in the channel."""
    channel = telegram2rss.TGChannel("username")  # A Channel with only tow messages.

    assert channel.fetch_to_python(1)

    with pytest.raises(telegram2rss.channel.FeedEnd):
        assert channel.fetch_to_python(1)


def test_photos():
    """Test photos messages."""
    # TODO
    ...


def test_polls():
    """Test polls."""
    # TODO
    ...


def test_voice():
    """Test voice messages."""
    # TODO
    ...


def test_documents():
    """Test documents messages."""
    # TODO
    ...


def test_locations():
    """Test maps or geo location messages."""
    # TODO
    ...


def test_stickers():
    """Test normal stickers with are just a photos in another form."""
    # TODO Add a channel with normal stickers messages.
    ...


def test_unsupported_media():
    """Test unsupported media that can be only displayed from the telegram website."""
    channel = telegram2rss.TGChannel(
        "premium"
    )  # A channel with moving stickers messages.
    assert channel.fetch_to_rss(1)
