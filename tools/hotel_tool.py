"""
Hotel Recommendation Tool
Reads hotels.json and filters by city, star rating, and price.
Returns top hotel options ranked by value.
"""

import json
import os
from langchain.tools import tool

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "hotels.json")


def load_hotels() -> list:
    """Load hotels dataset from JSON file."""
    with open(DATA_PATH, "r") as f:
        return json.load(f)


@tool
def recommend_hotels(query: str) -> str:
    """
    Recommend hotels in a given city, with optional filters for budget and stars.

    Input format: "CITY" or "CITY, max_price=10000" or "CITY, stars=4"
    Examples:
        "Goa"
        "Mumbai, max_price=3000"
        "Delhi, stars=4"
        "Bangalore, max_price=10000, stars=3"

    Returns top hotel options with name, stars, price per night, and amenities.
    """
    try:
        # Parse city and optional filters
        params = {"max_price": None, "stars": None}
        parts = [p.strip() for p in query.split(",")]
        city = parts[0].strip().title()

        for part in parts[1:]:
            if "=" in part:
                key, val = part.split("=")
                key = key.strip().lower()
                val = val.strip()
                if key in params:
                    params[key] = int(val)

        hotels = load_hotels()

        # Filter by city
        city_hotels = [h for h in hotels if h["city"].lower() == city.lower()]
        if not city_hotels:
            return f"No hotels found in {city}."

        # Apply optional filters
        if params["stars"]:
            city_hotels = [h for h in city_hotels if h["stars"] >= params["stars"]]
        if params["max_price"]:
            city_hotels = [h for h in city_hotels if h["price_per_night"] <= params["max_price"]]

        if not city_hotels:
            return f"No hotels in {city} match your filters. Try relaxing constraints."

        # Sort by stars desc, then price asc (best value)
        city_hotels = sorted(city_hotels, key=lambda x: (-x["stars"], x["price_per_night"]))

        # Return top 3
        top_hotels = city_hotels[:3]

        def format_hotel(h, rank):
            stars_str = "⭐" * h["stars"]
            amenities = ", ".join(h["amenities"])
            return (
                f"#{rank} {h['name']} ({stars_str})\n\n"
                f"    Hotel ID  : {h['hotel_id']}\n"
                f"    Price/Night: ₹{h['price_per_night']:,}\n"
                f"    Amenities : {amenities}\n"
            )

        result = f"🏨  Hotels in {city} ({len(city_hotels)} found, showing top 3)\n\n"
        for i, hotel in enumerate(top_hotels, 1):
            result += format_hotel(hotel, i)

        # Add recommended pick
        recommended = top_hotels[0]
        result += f"\n✅ Recommended: {recommended['name']} at ₹{recommended['price_per_night']:,}/night"

        return result

    except Exception as e:
        return f"Error finding hotels: {str(e)}"
