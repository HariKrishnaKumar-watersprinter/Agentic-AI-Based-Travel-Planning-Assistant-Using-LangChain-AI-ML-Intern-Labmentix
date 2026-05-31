"""
Budget Estimation Tool
Calculates estimated total trip cost based on flights, hotels, and daily expenses.
"""

from langchain.tools import tool

# Average daily expense estimates per city (food + local transport + misc)
DAILY_EXPENSE_ESTIMATES = {
    "Delhi":     {"budget": 800,  "mid": 1500, "luxury": 3000},
    "Mumbai":    {"budget": 1000, "mid": 1800, "luxury": 3500},
    "Goa":       {"budget": 1200, "mid": 2000, "luxury": 4000},
    "Bangalore": {"budget": 900,  "mid": 1600, "luxury": 3200},
    "Chennai":   {"budget": 800,  "mid": 1400, "luxury": 2800},
    "Hyderabad": {"budget": 750,  "mid": 1300, "luxury": 2600},
    "Kolkata":   {"budget": 700,  "mid": 1200, "luxury": 2500},
    "Jaipur":    {"budget": 850,  "mid": 1500, "luxury": 3000},
}


@tool
def estimate_budget(query: str) -> str:
    """
    Estimate total trip budget including flights, hotel, and daily expenses.

    Input format: "CITY, days=N, flight_price=P, hotel_price=Q, style=mid"
    Parameters:
        - CITY          : destination city
        - days          : number of days (required)
        - flight_price  : one-way flight cost in ₹ (required)
        - hotel_price   : hotel cost per night in ₹ (required)
        - style         : budget / mid / luxury (default: mid)

    Example:
        "Goa, days=3, flight_price=4800, hotel_price=3200, style=mid"
        "Delhi, days=5, flight_price=2900, hotel_price=3900"
    """
    try:
        # Parse parameters
        params = {
            "days": None,
            "flight_price": None,
            "hotel_price": None,
            "style": "mid"
        }

        parts = [p.strip() for p in query.split(",")]
        city = parts[0].strip().title()

        for part in parts[1:]:
            if "=" in part:
                key, val = part.split("=")
                key = key.strip().lower()
                val = val.strip()
                if key in params:
                    if key == "style":
                        params[key] = val.lower()
                    else:
                        params[key] = float(val)

        # Validate required fields
        missing = [k for k in ["days", "flight_price", "hotel_price"] if params[k] is None]
        if missing:
            return f"Missing required parameters: {', '.join(missing)}. Example: 'Goa, days=3, flight_price=4800, hotel_price=3200'"

        days = int(params["days"])
        flight_cost = params["flight_price"]
        hotel_cost_total = params["hotel_price"] * days
        style = params["style"] if params["style"] in ["budget", "mid", "luxury"] else "mid"

        # Daily expenses
        city_expenses = DAILY_EXPENSE_ESTIMATES.get(city, DAILY_EXPENSE_ESTIMATES["Delhi"])
        daily_expenses = city_expenses[style]
        total_daily = daily_expenses * days

        # Totals
        subtotal = flight_cost + hotel_cost_total + total_daily
        taxes_fees = round(subtotal * 0.05)  # ~5% buffer
        grand_total = subtotal + taxes_fees

        result = (
            f" Budget Estimate — {days}-Day Trip to {city}\n"
            f"Travel Style: {style.title()}\n\n"
            f"- ✈️ Flight (one-way): ₹{flight_cost:,.0f}\n"
            f"- 🏨 Hotel ({days} nights): ₹{hotel_cost_total:,.0f} (₹{params['hotel_price']:,.0f}/night)\n"
            f"- 🍽️ Food & Local Travel: ₹{total_daily:,.0f} (₹{daily_expenses:,}/day)\n"
            f"- 📦 Taxes & Contingency: ₹{taxes_fees:,}\n\n"
            f" 🏷️ ESTIMATED TOTAL: ₹{grand_total:,.0f}\n\n"
            f"💡 Tip: {_budget_tip(style, city)}"
        )
        return result

    except Exception as e:
        return f"Error estimating budget: {str(e)}"


def _budget_tip(style: str, city: str) -> str:
    """Return a contextual budget tip."""
    tips = {
        "budget": f"To save more in {city}, use local autos/buses and eat at dhabas.",
        "mid": f"Mid-range travel in {city} offers a great balance of comfort and value.",
        "luxury": f"For a luxury experience in {city}, consider premium hotel packages that include meals.",
    }
    return tips.get(style, "Plan ahead to get the best deals!")
