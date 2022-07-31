"""Fetch and work with data from Telegram channels."""
from .channel import TELEGRAM_URL, TGChannel


__name__ = "telegram2rss"
__version__ = "0.1.0.alpha.0"
__author__ = "zer0-x"
__maintainer__ = __author__
__license__ = "GPL-3.0"
__url__ = "https://github.com/zer0-x/python-telegram2rss"

__all__ = [
    "TELEGRAM_URL",
    "TGChannel",
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__"
]
