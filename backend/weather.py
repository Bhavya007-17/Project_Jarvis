"""
Weather module using Open-Meteo API (free, no API key).
Returns current conditions and hourly forecast for Dashboard tab.
"""

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes to short labels (subset for common conditions)
WEATHER_LABELS = {
    0: "Clear",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather(lat, lon, hourly_hours=24):
    """
    Fetch current weather and hourly forecast from Open-Meteo.
    :param lat: Latitude (float)
    :param lon: Longitude (float)
    :param hourly_hours: Number of hourly slots to return (default 24)
    :return: dict with current, hourly (list of next N hours), timezone, or error
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,weather_code",
            "timezone": "auto",
            "forecast_days": 2,
        }
        r = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])[:hourly_hours]
        temps = hourly.get("temperature_2m", [])[:hourly_hours]
        codes = hourly.get("weather_code", [])[:hourly_hours]

        hourly_forecast = [
            {
                "time": t,
                "temperature_2m": temps[i] if i < len(temps) else None,
                "weather_code": codes[i] if i < len(codes) else None,
                "weather_label": WEATHER_LABELS.get(
                    codes[i] if i < len(codes) else 0, "Unknown"
                ),
            }
            for i, t in enumerate(times)
        ]

        return {
            "ok": True,
            "timezone": data.get("timezone", "UTC"),
            "current": {
                "time": current.get("time"),
                "temperature_2m": current.get("temperature_2m"),
                "relative_humidity_2m": current.get("relative_humidity_2m"),
                "weather_code": current.get("weather_code"),
                "weather_label": WEATHER_LABELS.get(
                    current.get("weather_code", 0), "Unknown"
                ),
                "wind_speed_10m": current.get("wind_speed_10m"),
            },
            "hourly": hourly_forecast,
        }
    except requests.RequestException as e:
        return {"ok": False, "error": str(e)}
    except (KeyError, TypeError) as e:
        return {"ok": False, "error": f"Parse error: {e}"}
