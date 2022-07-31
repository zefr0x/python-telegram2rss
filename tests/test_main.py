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

    with pytest.raises(telegram2rss.channel.FeedEnd):
        for _ in range(10):  # TO make sure that the test will not brake in the future.
            assert channel.fetch_to_python(1)


def test_photos():
    """Test photos messages."""
    channel = telegram2rss.TGChannel(
        "wallpapers"
    )  # A channel with wallpapers images and files.
    assert channel.fetch_to_rss(1)

    assert channel.channel_photos_count > 0
    assert channel.channel_files_count > 0


def test_polls():
    """Test polls."""
    channel = telegram2rss.TGChannel(
        "Polls_ar"
    )  # A channel with polls and some random things.
    assert channel.fetch_to_rss(2)


def test_voice():
    """Test voice messages."""
    # TODO
    ...


def test_documents():
    """Test documents messages."""
    channel = telegram2rss.TGChannel(
        "TAndroidAPK"
    )  # A channel with documents and links messages.
    assert channel.fetch_to_rss(1)

    assert channel.channel_files_count > 0
    assert channel.channel_links_count > 0


def test_locations():
    """Test maps or geo location messages."""
    # TODO
    ...


def test_stickers():
    """Test normal stickers with are just a photos in another form."""
    channel = telegram2rss.TGChannel(
        "tstickers"
    )  # A channel with normal telegram stickers.
    assert channel.fetch_to_rss(2)


def test_unsupported_media():
    """Test unsupported media that can be only displayed from the telegram website."""
    channel = telegram2rss.TGChannel(
        "premium"
    )  # A channel with moving stickers messages.
    assert channel.fetch_to_rss(1)


def test_counter_value_to_int():
    """Test the counter_value_to_int function."""
    with pytest.raises(ValueError):
        telegram2rss.channel.counter_value_to_int("15Xx")

    with pytest.raises(ValueError):
        telegram2rss.channel.counter_value_to_int("")

    assert telegram2rss.channel.counter_value_to_int("6.2Go") == 6.2 * 1e100
    assert telegram2rss.channel.counter_value_to_int("67Un") == 67 * 1e36
    assert telegram2rss.channel.counter_value_to_int("45T") == 45 * 1e12
    assert telegram2rss.channel.counter_value_to_int("2.7B") == 2700000000
    assert telegram2rss.channel.counter_value_to_int("2467.246M") == 2467246000
    assert telegram2rss.channel.counter_value_to_int("1.57M") == 1570000
    assert telegram2rss.channel.counter_value_to_int("34.2K") == 34200
    assert telegram2rss.channel.counter_value_to_int("872") == 872
    assert telegram2rss.channel.counter_value_to_int("0") == 0
