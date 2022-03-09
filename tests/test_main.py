"""Unit testing with pytest."""
import pytest

import telegram2rss


def test_TGChannel():
    """Create object and use fetch_to_python method."""
    channel = telegram2rss.TGChannel(input("Test channel id: "))

    data = channel.fetch_to_python(13)

    print(data)

    assert channel.channel_title
    assert channel.channel_description
    assert channel.channel_image_url is not None
    assert channel.channel_subscribers_count is not None
    assert channel.channel_photos_count is not None
    assert channel.channel_videos_count is not None
    assert channel.channel_files_count is not None
    assert channel.channel_url.startswith(telegram2rss.TELEGRAM_URL)
