"""
Weather Lookup Tool
Calls the free Open-Meteo API to retrieve weather forecast for a destination city.
No API key required.
"""

import requests
from datetime import datetime, timedelta
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


@tool
def get_weather(query: str) -> str:
    """
    Get the weather forecast for a destination city.

    Input format: "CITY" or "CITY, days=3" or "CITY, date=YYYY-MM-DD, days=3"
    Examples:
        "Goa"
        "Delhi, days=5"
        "Mumbai, days=7"
        "Jaipur, date=2024-12-01, days=3"

    Returns daily max/min temperature, precipitation probability,
    and weather description.
    """
    try:
        # Parse city and optional days/date
        days = 5
        start_date_str = None
        parts = [p.strip() for p in query.split(",")]
        city = parts[0].strip().title()

        for part in parts[1:]:
            p_lower = part.lower()
            if "days=" in p_lower:
                days = int(part.split("=")[1].strip())
                days = min(max(days, 1), 7)  # Clamp between 1–7
            elif "date=" in p_lower:
                start_date_str = part.split("=")[1].strip()

        if city not in CITY_COORDINATES:
            available = ", ".join(CITY_COORDINATES.keys())
            return f"City '{city}' not in coordinates database. Available: {available}"

        coords = CITY_COORDINATES[city]
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={coords['lat']}&longitude={coords['lon']}"
            f"&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max"
            f"&timezone=Asia/Kolkata"
        )

        if start_date_str:
            try:
                start_dt = datetime.fromisoformat(start_date_str)
                end_dt = start_dt + timedelta(days=days - 1)
                url += f"&start_date={start_dt.date().isoformat()}&end_date={end_dt.date().isoformat()}"
            except Exception:
                url += f"&forecast_days={days}"
        else:
            url += f"&forecast_days={days}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        weather_codes = daily.get("weathercode", [])
        precip_probs = daily.get("precipitation_probability_max", [])

        result = f"🌤️  Weather Forecast for {city} (Next {days} days)\n\n"
        for i in range(len(dates)):
            code = weather_codes[i] if i < len(weather_codes) else 0
            desc = WMO_DESCRIPTIONS.get(code, "Unknown")
            max_t = f"{max_temps[i]:.1f}°C" if i < len(max_temps) else "N/A"
            min_t = f"{min_temps[i]:.1f}°C" if i < len(min_temps) else "N/A"
            precip = f"{precip_probs[i]}%" if i < len(precip_probs) and precip_probs[i] is not None else "N/A"

            result += (
                f"Day {i+1} ({dates[i]})\n"
                f"  Condition : {desc}\n"
                f"  Temp      : {min_t} → {max_t}\n"
                f"  Rain Prob : {precip}\n\n"
            )

        return result.strip()

    except requests.exceptions.ConnectionError:
        return (
            f"⚠️  Weather API unavailable (no internet access in this environment).\n"
            f"Typical weather for {query.split(',')[0].strip().title()}:\n"
            f"  - Most Indian cities see 28–35°C in summer, 15–25°C in winter.\n"
            f"  - Goa/coastal cities: humid, monsoon June–September.\n"
            f"  - Delhi: hot summers (40°C+), cool winters (5–15°C).\n"
            f"  - Please check https://open-meteo.com for live forecasts."
        )
    except Exception as e:
        return f"Weather details is avilable from till date to future 15 days beyond that details not avilable"
