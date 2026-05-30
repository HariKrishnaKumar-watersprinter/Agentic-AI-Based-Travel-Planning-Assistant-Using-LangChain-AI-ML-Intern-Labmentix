# ✈️ Agentic AI-Based Travel Planning Assistant

A fully autonomous AI travel planner for India built with **LangChain**, **Claude**, and **Streamlit**.

---

## 🎯 Problem Statement

Planning a trip manually requires juggling multiple websites, comparing prices, checking weather, and building itineraries from scratch. This project replaces that friction with a **single AI agent** that reasons like a travel expert:

- Finds the best flights
- Recommends hotels within budget
- Discovers top attractions
- Fetches live weather forecasts
- Estimates total trip cost
- Generates a complete day-wise itinerary

---

## 🏗️ Architecture

```
User Query (natural language)
         │
         ▼
┌─────────────────────────────────────┐
│    LangChain Tool-Calling Agent     │
│         (Claude Sonnet)             │
│                                     │
│  1. Understands user's intent       │
│  2. Decides which tools to call     │
│  3. Calls tools in sequence         │
│  4. Synthesizes a final itinerary   │
└───────────────┬─────────────────────┘
                │
     ┌──────────▼──────────┐
     │     5 Tools          │
     ├──────────────────────┤
     │ search_flights       │──► flights.json
     │ recommend_hotels     │──► hotels.json
     │ discover_places      │──► places.json
     │ get_weather          │──► Open-Meteo API
     │ estimate_budget      │──► Internal logic
     └──────────────────────┘
                │
                ▼
    Structured Trip Itinerary
```

---

## 📁 Project Structure

```
travel_agent/
├── app.py               # Streamlit web application (4 tabs)
├── agent.py             # LangChain Tool-Calling Agent + CLI runner
├── requirements.txt     # Python dependencies
├── README.md            # This file
│
├── tools/               # LangChain tools (one per concern)
│   ├── __init__.py      # Exports ALL_TOOLS list
│   ├── flight_tool.py   # Filters flights.json by route, finds cheapest/fastest
│   ├── hotel_tool.py    # Filters hotels.json by city/stars/price, ranks by value
│   ├── places_tool.py   # Filters places.json by city/type/rating
│   ├── weather_tool.py  # Calls Open-Meteo API for 7-day forecast
│   └── budget_tool.py   # Computes total trip cost (flight+hotel+daily expenses)
│
└── data/                # JSON datasets
    ├── flights.json     # 30 domestic Indian flights
    ├── hotels.json      # 40 hotels across 8 cities
    └── places.json      # 40 attractions across 8 cities
```

---

## 🔧 Tools Explained

### 1. `search_flights`
- **Input**: `"Chennai to Goa"`
- **Logic**: Loads `flights.json`, filters by origin→destination, sorts by price and duration
- **Output**: Cheapest option + fastest option with full details

### 2. `recommend_hotels`
- **Input**: `"Goa, max_price=4000, stars=3"`
- **Logic**: Filters by city, applies optional price/star filters, sorts by stars↓ then price↑
- **Output**: Top 3 hotels with amenities and recommended pick

### 3. `discover_places`
- **Input**: `"Goa, type=beach, min_rating=4.0"`
- **Logic**: Filters by city, type, and rating, returns top 5 sorted by rating
- **Output**: Ranked attractions with type, rating, and ID

### 4. `get_weather`
- **Input**: `"Goa, days=3"`
- **Logic**: Calls `https://api.open-meteo.com` with city coordinates, parses WMO codes
- **Output**: Daily temp (min/max), weather description, rain probability

### 5. `estimate_budget`
- **Input**: `"Goa, days=3, flight_price=4800, hotel_price=3200, style=mid"`
- **Logic**: Sums flight + hotel × days + daily expenses (from city averages) + 5% buffer
- **Output**: Full breakdown with grand total

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- An Anthropic API key (for the Chat tab / agent.py)

### Installation

```bash
# Clone / download the project
cd travel_agent

# Install dependencies
pip install -r requirements.txt



### Run the Streamlit App

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

### Run the CLI Agent Directly

```bash
python agent.py
```

---

## 🖥️ Streamlit App Tabs

| Tab | Description |
|-----|-------------|
| **Plan My Trip** | One-click itinerary generator — select city, duration, budget in sidebar |
| **Explore Tools** | Test each tool individually with custom inputs |
| **Chat with Agent** | Conversational interface — type natural language requests |
| **About** | Project documentation and architecture |

---

## 📊 Supported Cities

Delhi · Mumbai · Goa · Bangalore · Chennai · Hyderabad · Kolkata · Jaipur

---

## 💡 Example Queries (Chat Tab)

```
"Plan a 3-day trip from Chennai to Goa on a mid-range budget."
"I want to visit Delhi from Hyderabad for 5 days. Keep hotels under ₹4000/night."
"What's the cheapest flight from Kolkata to Jaipur?"
"Recommend luxury hotels in Mumbai."
"What are the top-rated places to visit in Bangalore?"
```

---

## 🔌 API Used

| API | Purpose | Auth Required |
|-----|---------|--------------|
| [Open-Meteo](https://open-meteo.com) | Live weather forecasts | ❌ None |
| [GLM](https://chat.z.ai/) | AI reasoning + tool calling | ✅ API Key |

---

## 🛡️ Error Handling

- All tool functions wrapped in `try-except`
- Weather tool gracefully degrades when API is unreachable
- Agent has `handle_parsing_errors=True` for robustness
- Streamlit catches and displays agent errors clearly

---

## 🧩 Extending the Project

To add a new tool:
1. Create `tools/my_tool.py` with a `@tool` decorated function
2. Import it in `tools/__init__.py` and add to `ALL_TOOLS`
3. The agent will automatically discover and use it

---

## 📚 References

- [LangChain Documentation](https://docs.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Open-Meteo API](https://open-meteo.com/en/docs)
- [GLM API](https://chat.z.ai/)

## 🎤 Author

**Hari Krishna Kumar -AI,ML,Data Science & Analytics Enthusiast**

---
## 📬 Contact

For collaboration or queries:

* LinkedIn: *[www.linkedin.com/in/hari-668364112]*
* Email: *[harikrishnakumar368@gmail.com]*

---
