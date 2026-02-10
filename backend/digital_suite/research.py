"""
Research (Oracle / Phase 3): Factual lookups via DuckDuckGo and Wikipedia.
For queries like 'density of Inconel 718' or 'carbon fiber density' without opening a browser.
"""

from typing import Optional


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using DuckDuckGo (no API key). Returns list of {title, snippet, link}.
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return [
            {"title": r.get("title", ""), "snippet": r.get("body", ""), "link": r.get("href", "")}
            for r in results
        ]
    except ImportError:
        return [{"error": "duckduckgo-search not installed. pip install duckduckgo-search"}]
    except Exception as e:
        return [{"error": str(e)}]


def wikipedia_summary(query: str, sentences: int = 3) -> dict:
    """
    Get a short Wikipedia summary for a topic. Returns {title, summary, url} or {error}.
    """
    try:
        import wikipedia
        wikipedia.set_lang("en")
        # search first to get page title, then summary
        titles = wikipedia.search(query, results=1)
        if not titles:
            return {"error": f"No Wikipedia article found for '{query}'"}
        title = titles[0]
        summary = wikipedia.summary(title, sentences=sentences, auto_suggest=False)
        url = wikipedia.page(title).url
        return {"title": title, "summary": summary, "url": url}
    except ImportError:
        return {"error": "wikipedia library not installed. pip install wikipedia"}
    except Exception as e:
        return {"error": str(e)}
