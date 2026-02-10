"""
Briefing (Module B – Oracle): Morning Briefing = weather + system + optional news/stocks.
Weather via Open-Meteo (no API key). System via digital_suite.system_ops.
"""

import requests
from typing import Optional
from .system_ops import get_system_status, format_system_status_for_speech

# Default location (Blacksburg, VA – PRD example)
DEFAULT_LAT = 37.2296
DEFAULT_LON = -80.4139

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON) -> dict:
    """Fetch current weather from Open-Meteo (no key required)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
    }
    try:
        r = requests.get(OPEN_METEO_URL, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        current = data.get("current", {})
        # weather_code: WMO codes; 0=clear, 1-3=mainly clear/cloudy, 80=rain, etc.
        code = current.get("weather_code", 0)
        desc = _weather_code_to_desc(code)
        return {
            "temperature_c": current.get("temperature_2m"),
            "temperature_f": round(current.get("temperature_2m", 0) * 9 / 5 + 32, 1),
            "humidity": current.get("relative_humidity_2m"),
            "weather_desc": desc,
            "wind_speed_kmh": current.get("wind_speed_10m"),
        }
    except Exception as e:
        return {"error": str(e)}


def _weather_code_to_desc(code: int) -> str:
    """Map WMO weather code to short description."""
    if code == 0:
        return "clear"
    if code in (1, 2, 3):
        return "mainly clear to cloudy"
    if code in (45, 48):
        return "foggy"
    if code in (51, 53, 55, 56, 57):
        return "drizzle"
    if code in (61, 63, 65, 66, 67):
        return "rain"
    if code in (71, 73, 75, 77):
        return "snow"
    if code in (80, 81, 82):
        return "rain showers"
    if code in (85, 86):
        return "snow showers"
    if code in (95, 96, 99):
        return "thunderstorm"
    return "variable"


def get_news_rss(max_items: int = 3) -> list[dict]:
    """Fetch top headlines from a couple of RSS feeds (e.g. BBC, TechCrunch)."""
    try:
        import feedparser
    except ImportError:
        return []

    feeds = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://techcrunch.com/feed/",
    ]
    entries = []
    for url in feeds:
        try:
            feed = feedparser.parse(url, request_headers={"User-Agent": "Jarvis-Briefing/1.0"})
            for e in feed.entries[:2]:
                entries.append({"title": e.get("title", ""), "link": e.get("link", "")})
        except Exception:
            continue
    return entries[:max_items]


def get_stocks(symbols: list[str] = None) -> list[dict]:
    """Fetch quick stock info for given symbols (e.g. NVDA). Default: NVDA."""
    if symbols is None:
        symbols = ["NVDA"]
    try:
        import yfinance as yf
    except ImportError:
        return []

    result = []
    for sym in symbols[:5]:
        try:
            ticker = yf.Ticker(sym)
            info = ticker.info
            prev = info.get("previousClose")
            current = info.get("currentPrice") or info.get("regularMarketPrice")
            if prev and current:
                pct = ((current - prev) / prev) * 100
                result.append({
                    "symbol": sym,
                    "price": round(current, 2),
                    "change_pct": round(pct, 2),
                })
            else:
                result.append({"symbol": sym, "price": current, "change_pct": None})
        except Exception:
            result.append({"symbol": sym, "error": "Could not fetch"})
    return result


def get_briefing(
    lat: float = DEFAULT_LAT,
    lon: float = DEFAULT_LON,
    include_weather: bool = True,
    include_system: bool = True,
    include_news: bool = False,
    include_stocks: bool = False,
    include_calendar: bool = True,
) -> dict:
    """
    Build a single briefing payload: weather, system, optional news/stocks/calendar.
    Returns a dict with keys: weather, system, system_speech, news, stocks, calendar_speech.
    Orchestrator can format this for the model or TTS.
    """
    out = {
        "weather": None,
        "system": None,
        "system_speech": None,
        "news": None,
        "stocks": None,
        "calendar_speech": None,
    }

    if include_weather:
        out["weather"] = get_weather(lat, lon)

    if include_system:
        status = get_system_status()
        out["system"] = status
        out["system_speech"] = format_system_status_for_speech(status)

    if include_calendar:
        try:
            from .productivity import get_today_schedule, format_schedule_for_speech
            schedule = get_today_schedule()
            out["calendar_speech"] = format_schedule_for_speech(schedule)
        except Exception:
            out["calendar_speech"] = None

    if include_news:
        out["news"] = get_news_rss()

    if include_stocks:
        out["stocks"] = get_stocks()

    return out


def format_briefing_for_model(briefing: dict) -> str:
    """Turn briefing dict into a single text block for the LLM to speak from."""
    parts = []

    if briefing.get("weather"):
        w = briefing["weather"]
        if "error" in w:
            parts.append(f"Weather: Unable to fetch ({w['error']}).")
        else:
            temp_f = w.get("temperature_f")
            desc = w.get("weather_desc", "unknown")
            parts.append(f"Weather: {temp_f}°F, {desc}.")

    if briefing.get("calendar_speech"):
        parts.append(briefing["calendar_speech"])

    if briefing.get("system_speech"):
        parts.append(f"System: {briefing['system_speech']}")

    if briefing.get("news"):
        parts.append("Top headlines:")
        for i, n in enumerate(briefing["news"][:3], 1):
            parts.append(f"  {i}. {n.get('title', '')}")

    if briefing.get("stocks"):
        for s in briefing["stocks"]:
            if "error" in s:
                parts.append(f"Stock {s['symbol']}: {s['error']}")
            else:
                pct = s.get("change_pct")
                pct_str = f", {pct:+.1f}%" if pct is not None else ""
                parts.append(f"Stock {s['symbol']}: ${s.get('price', '?')}{pct_str}")

    return "\n".join(parts) if parts else "No briefing data available."
