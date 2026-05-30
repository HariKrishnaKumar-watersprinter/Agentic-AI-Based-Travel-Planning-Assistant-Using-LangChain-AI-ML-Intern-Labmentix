"""
Streamlit Web Application — AI Travel Planning Assistant
Provides an interactive UI for generating AI-powered trip itineraries.
"""

import streamlit as st
import sys
import os
import datetime

# Allow importing from the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.flight_tool import search_flights
from tools.hotel_tool import recommend_hotels
from tools.places_tool import discover_places
from tools.weather_tool import get_weather
from tools.budget_tool import estimate_budget

# ──────────────────────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# Cached tool runners
# All args are explicitly cast to primitive types so the cache
# key is always consistent — prevents Streamlit's "Clear caches"
# dialog from appearing.
# ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def cached_search_flights(origin: str, destination: str) -> str:
    return search_flights.invoke(f"{origin} to {destination}")

@st.cache_data(show_spinner=False)
def cached_get_weather(destination: str, duration: int, start_date: str = "") -> str:
    """Takes city, days, and an optional ISO date string (YYYY-MM-DD) for travel date."""
    q = f"{str(destination)}, days={int(duration)}"
    if start_date:
        q += f", start_date={start_date}"
    return get_weather.invoke(q)

@st.cache_data(show_spinner=False)
def cached_recommend_hotels(destination: str, max_budget: int) -> str:
    return recommend_hotels.invoke(f"{str(destination)}, max_price={int(max_budget)}")

@st.cache_data(show_spinner=False)
def cached_discover_places(destination: str) -> str:
    return discover_places.invoke(str(destination))

@st.cache_data(show_spinner=False)
def cached_estimate_budget(destination: str, duration: int,
                            flight_price: float, hotel_price: float,
                            travel_style: str) -> str:
    # Normalise to consistent hashable types — prevents cache invalidation
    q = (f"{str(destination)}, days={int(duration)}, "
         f"flight_price={round(float(flight_price), 2)}, "
         f"hotel_price={round(float(hotel_price), 2)}, "
         f"style={str(travel_style)}")
    return estimate_budget.invoke(q)

# ──────────────────────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        background: #f8f9ff;
        border-left: 4px solid #667eea;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.8rem 0;
    }
    .tool-badge {
        background: #e8f4fd;
        border: 1px solid #3498db;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.8rem;
        color: #2980b9;
        display: inline-block;
        margin: 2px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    .metric-box {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>✈️ AI Travel Planning Assistant</h1>
    <p style="font-size:1.1rem; opacity:0.9;">
        Powered by LangChain & Google Gemini — Your intelligent travel companion for India
    </p>
</div>
""", unsafe_allow_html=True)

CITIES = ["Delhi", "Mumbai", "Goa", "Bangalore", "Chennai",
          "Hyderabad", "Kolkata", "Jaipur"]

# ──────────────────────────────────────────────────────────────
# Sidebar — Quick Tools
# ──────────────────────────────────────────────────────────────
#with st.sidebar:
   # st.header("🔎 Quick Tools")
  #  quick_city = st.selectbox("City", CITIES, index=2)
  #  quick_max_budget = st.number_input("Max Price/Night (₹)", min_value=500,
                                       max_value=10000, value=4000, step=500,
                                       key="sidebar_budget")

  #  col1, col2 = st.columns(2)
 #   with col1:
     #   if st.button("🏨 Hotels"):
            # Cast to int — number_input returns float
      #      st.session_state["quick_result"] = cached_recommend_hotels(
         #       quick_city, int(quick_max_budget))
   # with col2:
      #  if st.button("📍 Places"):
    #        st.session_state["quick_result"] = cached_discover_places(quick_city)

   # if "quick_result" in st.session_state:
      #  st.text_area("Result", st.session_state["quick_result"], height=200)

   # st.markdown("---")
   # st.markdown("**About this app**")
   # st.caption(
    #    "Built with LangChain + Google Gemini AI.\n"
    #    "Uses real datasets for flights, hotels & places.\n"
    #    "Weather via Open-Meteo API.")

# ──────────────────────────────────────────────────────────────
# Main Panel — Tab Layout
# ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Chat with Agent", "🗺️ Plan My Trip", "🔍 Explore Tools", "ℹ️ About"
])

# ── TAB 1: Chat with Agent ────────────────────────────────────
with tab1:
    st.subheader("💬 Chat with the AI Travel Agent")
    st.info('You can plan trips to these cities: "Delhi", "Mumbai", "Goa", "Bangalore", "Chennai", '
            '"Hyderabad", "Kolkata", "Jaipur"')

    # Session state initialisation
    for key, default in {
        "chat_history_display": [],
        "chat_history_lc": [],
        "agent_error": None,
        "editing_msg_idx": None,
        "last_user_input": None,
        "agent_running": False,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Helper: run agent ─────────────────────────────────────
    def _run_agent_query(query: str) -> None:
        st.session_state.agent_running = True
        st.session_state.agent_error = None

        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent is thinking and calling tools..."):
                try:
                    from agent import run_agent
                    from langchain_core.messages import HumanMessage, AIMessage

                    result = run_agent(
                        query,
                        chat_history=st.session_state.chat_history_lc,
                        verbose=False,
                    )
                    response = result["output"]

                    tools_used = []
                    for step in result.get("steps", []):
                        action = step[0]
                        tools_used.append({
                            "tool": action.tool,
                            "input": str(action.tool_input)[:120],
                        })

                    if tools_used:
                        with st.expander(f"🔧 Tools called ({len(tools_used)})"):
                            for t in tools_used:
                                st.markdown(
                                    f'<span class="tool-badge">🔧 {t["tool"]}</span> '
                                    f'`{t["input"]}`',
                                    unsafe_allow_html=True,
                                )
                    st.markdown(response)

                    st.session_state.chat_history_display.append({
                        "role": "assistant",
                        "content": response,
                        "tools_used": tools_used,
                        "is_error": False,
                    })
                    st.session_state.chat_history_lc.append(HumanMessage(content=query))
                    st.session_state.chat_history_lc.append(AIMessage(content=response))
                    st.session_state.agent_error = None

                except Exception as exc:
                    err_msg = str(exc)
                    st.session_state.agent_error = err_msg
                    st.error(f"⚠️ Agent error: {err_msg}")
                    st.session_state.chat_history_display.append({
                        "role": "assistant",
                        "content": f"⚠️ Error: {err_msg}",
                        "is_error": True,
                        "tools_used": [],
                    })

        st.session_state.agent_running = False

    st.info(
        "💡 **Tip:** Type a natural language request, e.g.  \n"
        "*'Plan a 3-day trip from Delhi to Goa on a mid-range budget'*"
    )

    # ── Control buttons ────────────────────────────────────────
    ctrl_col1, _ = st.columns([1, 4])
    with ctrl_col1:
        clear_clicked = st.button("🗑️ Clear Chat", key="clear_chat_btn",
                                   disabled=not st.session_state.chat_history_display)
    if clear_clicked:
        st.session_state.chat_history_display = []
        st.session_state.chat_history_lc = []
        st.session_state.agent_error = None
        st.session_state.last_user_input = None
        st.session_state.agent_running = False
        st.rerun()

    # ── Display chat history ───────────────────────────────────
    for i, msg in enumerate(st.session_state.chat_history_display):
        role = msg["role"]
        is_editing = st.session_state.get("editing_msg_idx") == i

        with st.chat_message(role):
            if role == "user":
                if is_editing:
                    new_text = st.text_area("Edit your message",
                                            value=msg["content"], key=f"edit_area_{i}")
                    btn_col1, btn_col2 = st.columns([1, 1])
                    if btn_col1.button("💾 Save", key=f"save_{i}"):
                        if new_text.strip():
                            st.session_state.chat_history_display[i]["content"] = new_text
                            st.session_state.chat_history_display = \
                                st.session_state.chat_history_display[:i + 1]
                            st.session_state.chat_history_lc = \
                                st.session_state.chat_history_lc[:i]
                            st.session_state.editing_msg_idx = None
                            st.session_state.last_user_input = new_text
                            _run_agent_query(new_text)
                            st.rerun()
                    if btn_col2.button("Cancel", key=f"cancel_{i}"):
                        st.session_state.editing_msg_idx = None
                        st.rerun()
                else:
                    st.markdown(msg["content"])
                    c1, c2, c3 = st.columns([0.9, 0.05, 0.05])
                    if c2.button("✏️", key=f"edit_btn_{i}", help="Edit"):
                        st.session_state.editing_msg_idx = i
                        st.rerun()
                    if c3.button("🗑️", key=f"del_btn_{i}", help="Delete"):
                        st.session_state.chat_history_display = \
                            st.session_state.chat_history_display[:i]
                        st.session_state.chat_history_lc = \
                            st.session_state.chat_history_lc[:i]
                        st.rerun()
            else:
                if msg.get("is_error"):
                    st.error(msg["content"])
                    if (i == len(st.session_state.chat_history_display) - 1
                            and st.session_state.last_user_input):
                        if st.button("🔄 Retry Last Request", key=f"retry_msg_{i}"):
                            query_to_run = st.session_state.last_user_input
                            st.session_state.chat_history_display.pop()
                            st.session_state.agent_error = None
                            _run_agent_query(query_to_run)
                            st.rerun()
                        with st.expander("🛠️ Troubleshooting tips"):
                            st.markdown("""
- **RateLimitError** → Too many requests. Wait a moment and press **Retry Last**.
- **Timeout / Connection error** → Check your internet connection, then retry.
- **Parsing error** → The agent hit a reasoning loop. Press **Retry Last** or rephrase.
- **AuthenticationError** → Check your API keys configured in `agent.py`.
- **Any other error** → Press **Clear Chat** to reset and start fresh.
                            """)
                else:
                    st.markdown(msg["content"])
                if msg.get("tools_used"):
                    with st.expander(f"🔧 Tools called ({len(msg['tools_used'])})"):
                        for t in msg["tools_used"]:
                            st.markdown(
                                f'<span class="tool-badge">🔧 {t["tool"]}</span> '
                                f'`{t["input"]}`',
                                unsafe_allow_html=True,
                            )

    # ── New user message ───────────────────────────────────────
    user_input = st.chat_input(
        "e.g., 'Plan a 4-day trip from Delhi to Goa on a mid-range budget'",
        disabled=st.session_state.agent_running,
    )
    if user_input:
        st.session_state.last_user_input = user_input
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history_display.append({
            "role": "user",
            "content": user_input,
            "is_error": False,
            "tools_used": [],
        })
        _run_agent_query(user_input)
        st.rerun()


# ── TAB 2: Plan My Trip ───────────────────────────────────────
with tab2:
    st.subheader("🗺️ Generate Your Complete Itinerary")
    st.info('You can plan trips to these cities: "Delhi", "Mumbai", "Goa", "Bangalore", '
            '"Chennai", "Hyderabad", "Kolkata", "Jaipur"')

    st.header("⚙️ Trip Configuration")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        t2_origin = st.selectbox("🛫 Departure City", CITIES, index=4, key="t2_origin")
    with col2:
        t2_destination = st.selectbox("🛬 Destination City", CITIES, index=2, key="t2_dest")
    with col3:
        travel_date = st.date_input(
            "📆 Departure Date",
            value=None,                  # ← no auto-selection; user must pick
            min_value=datetime.date.today(),
            max_value=datetime.date.today() + datetime.timedelta(days=365),
        )
    with col4:
        t2_duration = st.slider("📅 Trip Duration (days)", 1, 7, 3, key="t2_dur")
    with col5:
        t2_style = st.radio("💼 Travel Style", ["budget", "mid", "luxury"],
                             index=1, horizontal=False, key="t2_style")
    with col6:
        t2_max_budget = st.number_input("💰 Max Hotel Price/Night (₹)", 500, 10000,
                                         4000, 500, key="t2_budget")

    custom_note = st.text_input("📝 Any special preferences?",
                                 placeholder="e.g., love beaches and local food, no museums")

    if st.button("✨ Generate Itinerary", type="primary"):
        # ── Validation ─────────────────────────────────────────
        if t2_origin == t2_destination:
            st.error("🚫 Departure and destination cities must be different.")
        elif travel_date is None:
            st.error("📆 Please select a departure date before generating your itinerary.")
        else:
            with st.spinner("🤖 Your AI travel agent is planning your trip..."):
                progress = st.progress(0)
                status   = st.empty()

                status.info("✈️ Searching flights...")
                progress.progress(15)
                flight_result = cached_search_flights(t2_origin, t2_destination)

                # Extract cheapest price
                flight_price = 0.0
                for line in flight_result.split("\n"):
                    if "Price" in line and "₹" in line:
                        try:
                            flight_price = float(
                                line.split("₹")[1].replace(",", "").strip())
                            break
                        except Exception:
                            pass

                status.info("🌤️ Fetching weather forecast...")
                progress.progress(35)
                # Pass travel_date so forecast starts on the user's chosen date
                weather_result = cached_get_weather(
                    t2_destination,
                    int(t2_duration),
                    travel_date.isoformat(),   # e.g. "2026-06-19"
                )

                status.info("🏨 Finding best hotels...")
                progress.progress(55)
                hotel_result = cached_recommend_hotels(t2_destination, int(t2_max_budget))

                hotel_price = round(float(t2_max_budget), 2)
                for line in hotel_result.split("\n"):
                    if "Price/Night" in line and "₹" in line:
                        try:
                            hotel_price = round(float(
                                line.split("₹")[1].replace(",", "").strip()), 2)
                            break
                        except Exception:
                            pass

                status.info("📍 Discovering attractions...")
                progress.progress(70)
                places_result = cached_discover_places(t2_destination)

                status.info("💰 Calculating budget...")
                progress.progress(85)
                budget_result = cached_estimate_budget(
                    t2_destination,
                    int(t2_duration),
                    round(float(flight_price), 2),
                    round(float(hotel_price), 2),
                    str(t2_style),
                )

                progress.progress(100)
                status.empty()

            # ── Results ────────────────────────────────────────
            st.success("✅ Your itinerary is ready!")

            col_a, col_b, col_c, col_d = st.columns(4)
            col_a.metric("Destination",    t2_destination, f"{t2_duration} Days")
            col_b.metric("Departure Date", travel_date.strftime("%d %b %Y"))
            col_c.metric("Travel Style",   t2_style.title())
            if flight_price > 0:
                col_d.metric("Flight Price", f"₹{flight_price:,.0f}")

            st.markdown("---")

            st.markdown("### 🌤️ Weather")
            st.info(weather_result)

            st.markdown("### ✈️ Flight")
            st.info(flight_result)

            st.markdown("### 🏨 Hotel Recommendation")
            st.success(hotel_result)

            # Day-wise itinerary using the selected travel_date
            st.markdown("### 📅 Day-wise Itinerary")
            place_lines = [
                l.strip() for l in places_result.split("\n")
                if l.strip() and l.strip()[0].isdigit()
            ]
            for day in range(1, t2_duration + 1):
                day_date   = travel_date + datetime.timedelta(days=day - 1)
                date_label = day_date.strftime("%A, %d %b %Y")
                start      = (day - 1) * 2
                day_places = place_lines[start:start + 2] or ["Explore local markets and streets"]
                st.markdown(f"#### Day {day} — {date_label}")
                st.info(" | ".join(day_places))

            with st.expander("📍 All Attractions"):
                st.markdown(places_result)

            st.markdown("### 💰 Budget Breakdown")
            st.success(budget_result)

            if custom_note:
                st.markdown("### 💡 Personalized Note")
                st.info(f"Based on your preference: *'{custom_note}'* — "
                        f"look for {t2_destination}'s best spots matching this interest!")

            full_report = (
                f"AI TRAVEL PLAN: {t2_origin} → {t2_destination} ({t2_duration} Days)\n"
                f"Travel Date  : {travel_date.strftime('%d %b %Y')} to "
                f"{(travel_date + datetime.timedelta(days=t2_duration-1)).strftime('%d %b %Y')}\n"
                f"{'='*60}\n\n"
                f"FLIGHTS:\n{flight_result}\n\n"
                f"WEATHER:\n{weather_result}\n\n"
                f"HOTEL:\n{hotel_result}\n\n"
                f"PLACES:\n{places_result}\n\n"
                f"BUDGET:\n{budget_result}\n"
            )
            st.download_button(
                "⬇️ Download Itinerary (TXT)",
                full_report,
                file_name=f"trip_{t2_origin}_to_{t2_destination}_{t2_duration}days.txt",
                mime="text/plain",
            )


# ── TAB 3: Explore Individual Tools ──────────────────────────
with tab3:
    st.subheader("🔍 Explore Individual Tools")
    tool_choice = st.selectbox(
        "Select a tool",
        ["Flight Search", "Hotel Finder", "Places Discovery",
         "Weather Lookup", "Budget Calculator"],
    )

    if tool_choice == "Flight Search":
        c1, c2 = st.columns(2)
        with c1:
            f_from = st.selectbox("From", CITIES, key="f_from")
        with c2:
            f_to = st.selectbox("To", CITIES, index=2, key="f_to")
        if st.button("Search Flights"):
            with st.spinner("Searching..."):
                st.text(cached_search_flights(f_from, f_to))

    elif tool_choice == "Hotel Finder":
        h_city  = st.selectbox("City", CITIES, key="h_city")
        h_stars = st.slider("Minimum Stars", 1, 5, 3)
        h_price = st.number_input("Max Price/Night (₹)", 500, 10000, 5000, 500)
        if st.button("Find Hotels"):
            with st.spinner("Searching..."):
                st.text(recommend_hotels.invoke(
                    f"{h_city}, stars={h_stars}, max_price={int(h_price)}"))

    elif tool_choice == "Places Discovery":
        p_city   = st.selectbox("City", CITIES, key="p_city")
        p_type   = st.selectbox("Type", ["Any", "temple", "fort", "museum",
                                          "park", "beach", "lake", "market", "monument"])
        p_rating = st.slider("Min Rating", 3.0, 5.0, 4.0, 0.1)
        if st.button("Discover Places"):
            with st.spinner("Searching..."):
                q = p_city
                if p_type != "Any":
                    q += f", type={p_type}"
                q += f", min_rating={p_rating}"
                st.text(discover_places.invoke(q))

    elif tool_choice == "Weather Lookup":
        w_city = st.selectbox("City", CITIES, key="w_city")
        w_days = st.slider("Forecast Days", 1, 7, 5)
        if st.button("Get Weather"):
            with st.spinner("Fetching weather..."):
                # Pass (str, int) matching the fixed cached_get_weather signature
                st.text(cached_get_weather(w_city, int(w_days)))

    elif tool_choice == "Budget Calculator":
        bc_city   = st.selectbox("Destination", CITIES, key="bc_city")
        bc_days   = st.slider("Days", 1, 7, 3, key="bc_days")
        bc_flight = st.number_input("Flight Price (₹)", 1000, 20000, 4000, 500)
        bc_hotel  = st.number_input("Hotel/Night (₹)", 500, 15000, 3000, 500)
        bc_style  = st.radio("Style", ["budget", "mid", "luxury"], key="bc_style")
        if st.button("Calculate Budget"):
            st.text(cached_estimate_budget(
                bc_city,
                int(bc_days),
                round(float(bc_flight), 2),
                round(float(bc_hotel), 2),
                str(bc_style),
            ))


# ── TAB 4: About ──────────────────────────────────────────────
with tab4:
    st.subheader("ℹ️ About This Project")
    st.markdown("""
## 🧳 Agentic AI-Based Travel Planning Assistant

This project is an **end-to-end AI travel planning system** built using:

| Component | Technology |
|-----------|-----------|
| AI Framework | LangChain (Tool-Calling Agent) |
| Language Model | GLM 4.5 Flash |
| UI Framework | Streamlit |
| Data | Custom JSON datasets (flights, hotels, places) |
| Weather | Open-Meteo API (free, no key needed) |

---
## 🔧 Tools Built

| Tool | Description |
|------|-------------|
| `search_flights` | Finds cheapest & fastest flights from JSON dataset |
| `recommend_hotels` | Recommends hotels by city, stars & price |
| `discover_places` | Lists top-rated tourist attractions |
| `get_weather` | Live 7-day weather forecast via Open-Meteo |
| `estimate_budget` | Calculates full trip budget breakdown |

---
## 🏗️ Architecture

```
User Query
    ↓
LangChain Tool-Calling Agent
    ↓ (decides which tools to call)
┌─────────────────────────────────────┐
│  search_flights  →  flights.json    │
│  recommend_hotels →  hotels.json    │
│  discover_places  →  places.json    │
│  get_weather      →  Open-Meteo API │
│  estimate_budget  →  Logic          │
└─────────────────────────────────────┘
    ↓
Structured Itinerary Output
```

---
## 📁 Project Structure

```
travel_agent/
├── app.py                  # Streamlit UI (this file)
├── agent.py                # LangChain ReAct Agent
├── tools/
│   ├── __init__.py
│   ├── flight_tool.py
│   ├── hotel_tool.py
│   ├── places_tool.py
│   ├── weather_tool.py
│   └── budget_tool.py
├── data/
│   ├── flights.json
│   ├── hotels.json
│   └── places.json
└── requirements.txt
```

---
## 🚀 How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```
    """)
