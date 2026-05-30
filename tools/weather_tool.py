"""
Weather Lookup Tool
Calls the free Open-Meteo API to retrieve weather forecast for a destination city.
Supports a start_date so the forecast matches the user's actual travel date,
not today's date.
No API key required.
"""

import datetime
import requests
from langchain.tools import tool

# City coordinates for Open-Meteo API
CITY_COORDINATES = {
    "Delhi":     {"lat": 28.6139, "lon": 77.2090},
    "Mumbai":    {"lat": 19.0760, "lon": 72.8777},
    "Goa":       {"lat": 15.2993, "lon": 74.1240},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Chennai":   {"lat": 13.0827, "lon": 80.2707},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Kolkata":   {"lat": 22.5726, "lon": 88.3639},
    "Jaipur":    {"lat": 26.9124, "lon": 75.7873},
}

WMO_DESCRIPTIONS = {
    0:  "☀️  Clear Sky",
    1:  "🌤️  Mostly Clear",
    2:  "⛅ Partly Cloudy",
    3:  "☁️  Overcast",
    45: "🌫️  Foggy",
    48: "🌫️  Depositing Rime Fog",
    51: "🌦️  Light Drizzle",
    53: "🌦️  Moderate Drizzle",
    55: "🌧️  Dense Drizzle",
    61: "🌧️  Slight Rain",
    63: "🌧️  Moderate Rain",
    65: "🌧️  Heavy Rain",
    71: "🌨️  Slight Snowfall",
    73: "🌨️  Moderate Snowfall",
    75: "🌨️  Heavy Snowfall",
    80: "🌦️  Slight Showers",
    81: "🌦️  Moderate Showers",
    82: "⛈️  Violent Showers",
    95: "⛈️  Thunderstorm",
    99: "⛈️  Thunderstorm with Hail",
}

# Open-Meteo supports forecasts up to 16 days ahead and
# historical data via the archive API. For dates beyond 16 days
# we use monthly climate averages as a fallback.
MAX_FORECAST_DAYS = 16

# Monthly climate normals (avg high / avg low °C) for each city
CLIMATE_NORMALS = {
    "Delhi":     [(21,7),(24,10),(30,15),(36,21),(41,26),(40,29),(35,27),(34,26),(34,24),(33,18),(28,12),(22,8)],
    "Mumbai":    [(31,19),(32,19),(33,21),(33,24),(33,27),(32,26),(30,25),(29,25),(30,24),(33,23),(33,21),(32,19)],
    "Goa":       [(32,20),(33,21),(34,23),(34,26),(33,27),(30,25),(29,24),(29,24),(29,24),(32,24),(33,22),(32,21)],
    "Bangalore": [(28,15),(31,17),(33,19),(34,21),(33,21),(29,19),(27,19),(27,19),(28,19),(28,18),(27,16),(26,15)],
    "Chennai":   [(29,20),(31,21),(33,23),(35,26),(38,28),(37,28),(35,27),(35,27),(34,25),(31,24),(29,22),(28,20)],
    "Hyderabad": [(29,15),(32,17),(36,21),(39,25),(40,27),(35,25),(30,23),(29,23),(30,22),(30,19),(28,15),(27,13)],
    "Kolkata":   [(26,13),(29,15),(34,20),(36,24),(36,26),(34,27),(32,27),(32,27),(32,26),(32,23),(29,18),(26,13)],
    "Jaipur":    [(22,8),(25,11),(31,16),(37,22),(41,27),(40,29),(35,27),(33,26),(34,24),(33,18),(28,12),(23,8)],
}


def _climate_fallback(city: str, start_date: datetime.date, days: int) -> str:
    """Return monthly climate normals when the date is beyond forecast range."""
    normals = CLIMATE_NORMALS.get(city, CLIMATE_NORMALS["Delhi"])
    result = (
        f"🌤️  Weather Forecast for {city}\n"
        f"    ({start_date.strftime('%d %b %Y')} — "
        f"{(start_date + datetime.timedelta(days=days-1)).strftime('%d %b %Y')})\n\n"
        f"⚠️  Note: Date is beyond the 16-day live forecast window is not available.\n"
        f"    Showing historical climate averages for this period.\n\n"
    )
    for day in range(days):
        day_date = start_date + datetime.timedelta(days=day)
        month_idx = day_date.month - 1
        high, low = normals[month_idx]
        result += (
            f"Day {day+1} ({day_date.strftime('%Y-%m-%d')})\n"
            f"  Condition : 📊 Climate Average\n"
            f"  Temp      : {low}°C → {high}°C (historical avg)\n"
            f"  Rain Prob : See local forecast closer to travel date\n\n"
        )
    return result.strip()


@tool
def get_weather(query: str) -> str:
    """
    Get the weather forecast for a destination city for the travel dates.

    Input format: "CITY, days=N" or "CITY, days=N, start_date=YYYY-MM-DD"
    Examples:
        "Goa, days=3"
        "Delhi, days=5, start_date=2026-06-19"
        "Mumbai, days=7, start_date=2026-07-01"

    Returns daily max/min temperature, precipitation probability,
    and weather description for the exact travel dates selected.
    If the travel date is beyond the 16-day forecast window, returns
    historical climate averages for those months instead.
    """
    try:
        days = 5
        start_date = None
        parts = [p.strip() for p in query.split(",")]
        city = parts[0].strip().title()

        for part in parts[1:]:
            if "=" in part:
                key, val = part.split("=", 1)
                key = key.strip().lower()
                val = val.strip()
                if key == "days":
                    days = min(max(int(val), 1), 16)
                elif key == "start_date":
                    start_date = datetime.date.fromisoformat(val)

        if city not in CITY_COORDINATES:
            available = ", ".join(CITY_COORDINATES.keys())
            return f"City '{city}' not in database. Available: {available}"

        today = datetime.date.today()
        if start_date is None:
            start_date = today

        end_date = start_date + datetime.timedelta(days=days - 1)

        # Check if travel date is beyond Open-Meteo's forecast window
        days_until_travel = (start_date - today).days
        if days_until_travel > MAX_FORECAST_DAYS:
            return _climate_fallback(city, start_date, days)

        coords = CITY_COORDINATES[city]
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={coords['lat']}&longitude={coords['lon']}"
            f"&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max"
            f"&timezone=Asia/Kolkata"
            f"&start_date={start_date.isoformat()}"
            f"&end_date={end_date.isoformat()}"
        )

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        daily        = data.get("daily", {})
        dates        = daily.get("time", [])
        max_temps    = daily.get("temperature_2m_max", [])
        min_temps    = daily.get("temperature_2m_min", [])
        weather_codes= daily.get("weathercode", [])
        precip_probs = daily.get("precipitation_probability_max", [])

        if not dates:
            return _climate_fallback(city, start_date, days)

        result = (
            f"🌤️  Weather Forecast for {city}\n"
            f"    ({start_date.strftime('%d %b %Y')} — "
            f"{end_date.strftime('%d %b %Y')})\n\n"
        )
        for i in range(len(dates)):
            code   = weather_codes[i] if i < len(weather_codes) else 0
            desc   = WMO_DESCRIPTIONS.get(code, "Unknown")
            max_t  = f"{max_temps[i]:.1f}°C" if i < len(max_temps) else "N/A"
            min_t  = f"{min_temps[i]:.1f}°C" if i < len(min_temps) else "N/A"
            precip = (f"{precip_probs[i]}%"
                      if i < len(precip_probs) and precip_probs[i] is not None
                      else "N/A")
            result += (
                f"Day {i+1} ({dates[i]})\n"
                f"  Condition : {desc}\n"
                f"  Temp      : {min_t} → {max_t}\n"
                f"  Rain Prob : {precip}\n\n"
            )

        return result.strip()

    except requests.exceptions.ConnectionError:
        city_name = query.split(",")[0].strip().title()
        return (
            f"⚠️  Weather API unavailable.\n"
            f"Typical weather for {city_name}:\n"
            f"  - Summer (Apr–Jun): 35–42°C in north India, 30–35°C in south.\n"
            f"  - Monsoon (Jul–Sep): heavy rain, 25–32°C.\n"
            f"  - Winter (Nov–Feb): 10–25°C across India.\n"
            f"  - Please check https://open-meteo.com for live forecasts."
        )
    except Exception as e:
        return f"Error fetching weather: {str(e)}"


