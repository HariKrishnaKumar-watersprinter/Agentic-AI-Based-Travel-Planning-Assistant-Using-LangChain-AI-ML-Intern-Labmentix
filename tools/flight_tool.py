# Assuming this is the content of your f:\Project\Labmantix\Agentic ai travel planer\files\tools\flight_tool.py

import json
from datetime import datetime
from langchain.tools import tool
import os

# Path to the flights data
FLIGHTS_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "flights.json")

@tool
def search_flights(query: str) -> str:
    """
    Searches for flights between two cities.
    Input format: "FROM_CITY to TO_CITY"
    Example: "Delhi to Mumbai"
    """
    try:
        from_city, to_city, Date = [c.strip() for c in query.split(" to ")]
    except ValueError:
        return "Invalid query format. Please use 'FROM_CITY to TO_CITY'."

    try:
        with open(FLIGHTS_DATA_PATH, 'r') as f:
            flights = json.load(f)
    except FileNotFoundError:
        return f"Error: Flight data file not found at {FLIGHTS_DATA_PATH}"
    except json.JSONDecodeError:
        return f"Error: Could not decode JSON from {FLIGHTS_DATA_PATH}"

    matching_flights = []
    for flight in flights:
        if flight["from"].lower() == from_city.lower() and flight["to"].lower() == to_city.lower():
            matching_flights.append(flight)

    if not matching_flights:
        return f"No direct flights found from {from_city} to {to_city}. You may need to book connecting flights through Mumbai, Bangalore, or other major airports."

    # Sort by price to find the cheapest
    matching_flights.sort(key=lambda x: x["price"])

    cheapest_flight = matching_flights[0]

    # Parse the datetime strings
    departure_dt = datetime.fromisoformat(cheapest_flight["departure_time"])
    arrival_dt = datetime.fromisoformat(cheapest_flight["arrival_time"])

    # --- START OF MODIFICATION ---
    # Change the format string to only show time (e.g., "12:26 AM")
    formatted_departure_time = departure_dt.strftime("%I:%M %p")
    formatted_arrival_time = arrival_dt.strftime("%I:%M %p")
    # --- END OF MODIFICATION ---

    result = (
        f"✈️ Cheapest Flight from {from_city} to {to_city}:\n"
        f"Date : {Date}
        f"  Airline: {cheapest_flight['airline']}\n"
        f"  Departure: {formatted_departure_time}\n"
        f"  Arrival: {formatted_arrival_time}\n"
        f"  Price: ₹{cheapest_flight['price']:,.0f}\n"
        f"  Flight ID: {cheapest_flight['flight_id']}"
    )
    return result
