"""Setup file for the library."""
from pathlib import Path
from setuptools import setup, find_packages

from telegram2rss import (
    __name__,
    __version__,
    __author__,
    __maintainer__,
    __license__,
    __url__,
)

HERE = Path(__file__).parent

README = (HERE / "README.md").read_text()

ISSUES = "https://github.com/ZER0-X/python-telegram2rss/issues"
CHANGELOG = "https://github.com/ZER0-X/python-telegram2rss/blob/main/CHANGELOG.md"


DESCRIPTION = (
    "A python library to fetch data from public Telegram channels"
    + " to use them as a python object or RSS feed."
)


setup(
    name=__name__,
    version=__version__,
    author=__author__,
    maintainer=__maintainer__,
    license=__license__,
    url=__url__,
    project_urls={
        "Issues": ISSUES,
        "Changelog": CHANGELOG,
    },
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=README,
    packages=find_packages(),
    install_requires=["requests", "beautifulsoup4", "lxml", "feedgen"],
    tests_require=["pytest"],
    test_suite="tests",
    keywords=["Python", "Telegram", "RSS"],
)
