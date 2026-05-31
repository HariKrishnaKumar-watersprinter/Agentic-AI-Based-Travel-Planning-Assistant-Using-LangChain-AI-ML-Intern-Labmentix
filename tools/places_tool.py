"""
Places Discovery Tool
Reads places.json and recommends attractions based on city, type, and rating.
"""

import json
import os
import streamlit as st
from langchain.tools import tool

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "places.json")

@st.cache_data
def load_places() -> list:
    """Load places dataset from JSON file."""
    with open(DATA_PATH, "r") as f:
        return json.load(f)


@tool
def discover_places(query: str) -> str:
    """
    Discover tourist attractions and points of interest in a given city.

    Input format: "CITY" or "CITY, type=temple" or "CITY, min_rating=4.0"
    Examples:
        "Goa"
        "Delhi, type=museum"
        "Mumbai, min_rating=4.0"
        "Jaipur, type=fort, min_rating=4.0"

    Supported types: temple, fort, museum, park, beach, lake, market, monument

    Returns top-rated places with name, type, and rating score.
    """
    try:
        # Parse city and optional filters
        params = {"type": None, "min_rating": None}
        parts = [p.strip() for p in query.split(",")]
        city = parts[0].strip().title()

        for part in parts[1:]:
            if "=" in part:
                key, val = part.split("=")
                key = key.strip().lower()
                val = val.strip()
                if key == "type":
                    params["type"] = val.lower()
                elif key == "min_rating":
                    params["min_rating"] = float(val)

        places = load_places()

        # Filter by city
        city_places = [p for p in places if p["city"].lower() == city.lower()]
        if not city_places:
            return f"No places found in {city}."

        # Apply optional filters
        if params["type"]:
            city_places = [p for p in city_places if p["type"].lower() == params["type"]]
        if params["min_rating"]:
            city_places = [p for p in city_places if p["rating"] >= params["min_rating"]]

        if not city_places:
            return f"No places in {city} match your filters. Try relaxing constraints."

        # Sort by rating descending
        city_places = sorted(city_places, key=lambda x: -x["rating"])

        # Top 5 attractions
        top_places = city_places[:5]

        type_emoji = {
            "temple": "🛕", "fort": "🏰", "museum": "🏛️",
            "park": "🌿", "beach": "🏖️", "lake": "🌊",
            "market": "🛒", "monument": "🗿"
        }

        result = f"📍  Places to visit in {city} ({len(city_places)} found, top 5)\n\n"
        for i, place in enumerate(top_places, 1):
            emoji = type_emoji.get(place["type"], "📌")
            result += (
                f"{i}. {emoji} {place['name']}\n"
                f"    Type   : {place['type'].title()}\n"
                f"    Rating : {'⭐' * int(place['rating'])} ({place['rating']})\n"
                f"    ID     : {place['place_id']}\n\n"
            )

        return result.strip()

    except Exception as e:
        return f"Error discovering places: {str(e)}"
