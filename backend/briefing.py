"""
Daily briefing: fetch news headlines for Technology, Science, and Top Stories.
Uses RSS feeds (no API key). Optional: headlines can be sent to Gemini for summary later.
"""

import re
import requests
from xml.etree import ElementTree

# RSS feeds for headlines (free, no key)
FEEDS = {
    "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "top": "https://feeds.bbci.co.uk/news/rss.xml",
}

MAX_ITEMS_PER_FEED = 5


def _parse_rss_items(url, limit=MAX_ITEMS_PER_FEED):
    """Fetch RSS URL and return list of {title, link, published, source}."""
    items = []
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        root = ElementTree.fromstring(r.content)
        # Handle both RSS 2.0 and Atom-style
        channel = root.find("channel")
        if channel is not None:
            for item in channel.findall("item")[:limit]:
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                title = title_el.text if title_el is not None and title_el.text else ""
                link = link_el.text if link_el is not None and link_el.text else ""
                published = pub_el.text if pub_el is not None and pub_el.text else ""
                if title:
                    # Strip HTML tags from title
                    title = re.sub(r"<[^>]+>", "", title)
                    items.append(
                        {"title": title, "link": link, "published": published, "source": "BBC"}
                    )
    except Exception:
        pass
    return items


def get_briefing():
    """
    Fetch headlines from Technology, Science, and Top Stories.
    :return: dict with ok, headlines { technology: [], science: [], top: [] }, and optional summary (empty until Gemini integration)
    """
    result = {
        "ok": True,
        "headlines": {
            "technology": [],
            "science": [],
            "top": [],
        },
        "summary": "",
    }
    try:
        for category, url in FEEDS.items():
            result["headlines"][category] = _parse_rss_items(url)
    except Exception as e:
        result["ok"] = False
        result["error"] = str(e)
    return result
