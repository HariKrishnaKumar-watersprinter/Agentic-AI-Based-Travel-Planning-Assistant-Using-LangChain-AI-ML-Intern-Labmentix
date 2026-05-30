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
import re
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
@st.cache_data
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

# ──────────────────────────────────────────────────────────────
# Sidebar — Configuration
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Trip Configuration")

    CITIES = ["Delhi", "Mumbai", "Goa", "Bangalore", "Chennai",
              "Hyderabad", "Kolkata", "Jaipur"]

    origin = st.selectbox("🛫 Departure City", CITIES, index=4)
    destination = st.selectbox("🛬 Destination City", CITIES, index=2)
    duration = st.slider("📅 Trip Duration (days)", min_value=1, max_value=7, value=3)
    travel_style = st.radio("💼 Travel Style", ["budget", "mid", "luxury"], index=1, horizontal=True,width='content')
    max_budget = st.number_input("💰 Max Hotel Price/Night (₹)", min_value=500,
                                  max_value=10000, value=4000, step=500)

    st.markdown("---")
    st.header("🔎 Quick Tools")
    quick_city = st.selectbox("City", CITIES, index=2)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏨 Hotels"):
            result = recommend_hotels.invoke(f"{quick_city}, max_price={max_budget}")
            st.session_state["quick_result"] = result
    with col2:
        if st.button("📍 Places"):
            result = discover_places.invoke(quick_city)
            st.session_state["quick_result"] = result

    if "quick_result" in st.session_state:
        st.text_area("Result", st.session_state["quick_result"], height=200)

    st.markdown("---")
    st.markdown("**About this app**")
    st.caption(
        "Built with LangChain + Google Gemini AI.\n"
        "Uses real datasets for flights, hotels & places.\n"
        "Weather via Open-Meteo API."
    )

# ──────────────────────────────────────────────────────────────
# Main Panel — Tab Layout
# ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Chat with Agent", "🗺️ Plan My Trip", "🔍 Explore Tools", "ℹ️ About"
])


# ── TAB 1: Auto Trip Planner ──────────────────────────────────
with tab2:
    st.subheader("🗺️ Generate Your Complete Itinerary")
    st.markdown("Fill in the sidebar preferences and click **Generate Itinerary** below.")
    st.info('You can plan trips to these cities: "Delhi", "Mumbai", "Goa", "Bangalore", "Chennai",'
                '"Hyderabad", "Kolkata", "Jaipur"')
    
    st.header("⚙️ Trip Configuration")
    
    CITIES = ["Delhi", "Mumbai", "Goa", "Bangalore", "Chennai",
              "Hyderabad", "Kolkata", "Jaipur"]
    col1,col2=st.columns(2)
    with col1:
        origin = st.selectbox("🛫 Departure City", CITIES, index=4)
    with col2:
        destination = st.selectbox("🛬 Destination City", CITIES, index=2)
    # ── Date picker with explicit opt-in ──────────────────────
    date_enabled = st.checkbox("📆 Select a Travel Date", value=False,
                                help="Tick this first, then pick your date.")
    if date_enabled:
        travel_date = st.date_input(
            "Departure Date",
            value=datetime.date.today(),
            min_value=datetime.date.today(),
            max_value=datetime.date.today() + datetime.timedelta(days=365),
            label_visibility="collapsed",
        )
        st.caption(f"✅ Departing on **{travel_date.strftime('%A, %d %b %Y')}**")
    else:
        travel_date = None
        st.caption("⬆️ Tick the checkbox above to choose your departure date.")
    duration = st.slider("📅 Trip Duration (days)", min_value=1, max_value=7, value=3)
    travel_style = st.radio("💼 Travel Style", ["budget", "mid", "luxury"], index=1, key="travel_style_tab2",horizontal=True,width='content')
    max_budget = st.number_input("💰 Max Hotel Price/Night (₹)", min_value=500,
                                  max_value=10000, value=4000, step=500)

   
    custom_note = st.text_input(
        "📝 Any special preferences?",
        placeholder="e.g., love beaches and local food, no museums"
    )
    
    if st.button("✨ Generate Itinerary", type="primary"):
        if origin == destination:
            st.error("Departure and destination cities must be different.")
        else:
            with st.spinner("🤖 Your AI travel agent is planning your trip..."):
                progress = st.progress(0)
                steps_container = st.empty()
    
                # ── Step 1: Flights ──────────────────────────
                steps_container.info("✈️ Searching flights...")
                progress.progress(15)
                flight_result = search_flights.invoke(f"{origin} to {destination}")

                # Extract cheapest flight price from result
                flight_price = 0
                for line in flight_result.split("\n"):
                    if "Price" in line and "₹" in line:
                        try:
                            price_str = line.split("₹")[1].replace(",", "").strip()
                            flight_price = float(price_str)
                            break
                        except Exception:
                            pass

                # ── Step 2: Weather ──────────────────────────
                steps_container.info("🌤️ Fetching weather forecast...")
                progress.progress(35)
                weather_q = f"{destination}, days={duration}"
                if travel_date:
                    weather_q += f", date={travel_date.isoformat()}"
                weather_result = get_weather.invoke(weather_q)

                # ── Step 3: Hotels ──────────────────────────
                steps_container.info("🏨 Finding best hotels...")
                progress.progress(55)
                hotel_query = f"{destination}, max_price={max_budget}"
                hotel_result = recommend_hotels.invoke(hotel_query)

                # Extract hotel price from result
                hotel_price = max_budget  # fallback
                for line in hotel_result.split("\n"):
                    if "Price/Night" in line and "₹" in line:
                        try:
                            price_str = line.split("₹")[1].replace(",", "").strip()
                            hotel_price = float(price_str)
                            break
                        except Exception:
                            pass

                # ── Step 4: Places ──────────────────────────
                steps_container.info("📍 Discovering attractions...")
                progress.progress(70)
                places_result = discover_places.invoke(destination)

                # ── Step 5: Budget ───────────────────────────
                steps_container.info("💰 Calculating budget...")
                progress.progress(85)
                budget_query = (
                    f"{destination}, days={duration}, "
                    f"flight_price={flight_price}, "
                    f"hotel_price={hotel_price}, "
                    f"style={travel_style}"
                )
                budget_result = estimate_budget.invoke(budget_query)
                progress.progress(100)
                steps_container.empty()

            # ── Render Results ───────────────────────────────
            st.success("✅ Your itinerary is ready!")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Destination", destination, f"{duration} Days")
            with col_b:
                st.metric("Travel Style", travel_style.title())
            with col_c:
                if flight_price > 0:
                    st.metric("Flight Price", f"₹{flight_price:,.0f}")

            st.markdown("---")

            st.markdown("### 🌤️ Weather")
            st.info(weather_result)

            #col_left, col_right = st.columns(2)
            #with col_left:
            st.markdown("### ✈️ Flight")
            st.info(flight_result)
            #with col_right:
            

            # Hotel
            st.markdown("### 🏨 Hotel Recommendation")
            st.success(hotel_result)

            # Day-wise Places Itinerary
            st.markdown("### 📅 Day-wise Itinerary")
            # Parse places for day allocation
            place_lines = [
                l.strip() for l in places_result.split("\n")
                if l.strip() and l.strip()[0].isdigit()
            ]
            for day in range(1, duration + 1):
                start = (day - 1) * 2
                day_places = place_lines[start:start + 2]
                if not day_places:
                    day_places = ["Explore local markets and streets"]
                st.markdown(f"#### Day {day}\n",)
                st.info(f" {' | '.join(day_places)}")

            # Full places list
            with st.expander("📍 All Attractions"):
                st.markdown(places_result)

            st.markdown("### 💰 Budget Breakdown")
            st.success(f'{budget_result}')

            # Travel Tips
            if custom_note:
                st.markdown("### 💡 Personalized Note")
                st.info(f"Based on your preference: *'{custom_note}'* — "
                        f"look for {destination}'s best spots matching this interest!")

            # Download
            full_report = (
                f"AI TRAVEL PLAN: {origin} → {destination} ({duration} Days)\n"
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
                file_name=f"trip_{origin}_to_{destination}_{duration}days.txt",
                mime="text/plain"
            )
        

# ── TAB 2: Explore Individual Tools ──────────────────────────
with tab3:
    st.subheader("🔍 Explore Individual Tools")
    tool_choice = st.selectbox(
        "Select a tool",
        ["Flight Search", "Hotel Finder", "Places Discovery", "Weather Lookup", "Budget Calculator"]
    )

    if tool_choice == "Flight Search":
        col1, col2 = st.columns(2)
        with col1:
            f_from = st.selectbox("From", CITIES, key="f_from")
        with col2:
            f_to = st.selectbox("To", CITIES, index=2, key="f_to")
        if st.button("Search Flights"):
            with st.spinner("Searching..."):
                st.text(search_flights.invoke(f"{f_from} to {f_to}"))

    elif tool_choice == "Hotel Finder":
        h_city = st.selectbox("City", CITIES, key="h_city")
        h_stars = st.slider("Minimum Stars", 1, 5, 3)
        h_price = st.number_input("Max Price/Night (₹)", 500, 10000, 5000, 500)
        if st.button("Find Hotels"):
            with st.spinner("Searching..."):
                q = f"{h_city}, stars={h_stars}, max_price={h_price}"
                st.text(recommend_hotels.invoke(q))

    elif tool_choice == "Places Discovery":
        p_city = st.selectbox("City", CITIES, key="p_city")
        p_type = st.selectbox("Type", ["Any", "temple", "fort", "museum",
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
                st.text(get_weather.invoke(f"{w_city}, days={w_days}"))

    elif tool_choice == "Budget Calculator":
        bc_city = st.selectbox("Destination", CITIES, key="bc_city")
        bc_days = st.slider("Days", 1, 7, 3, key="bc_days")
        bc_flight = st.number_input("Flight Price (₹)", 1000, 20000, 4000, 500)
        bc_hotel = st.number_input("Hotel/Night (₹)", 500, 15000, 3000, 500)
        bc_style = st.radio("Style", ["budget", "mid", "luxury"], key="bc_style")
        if st.button("Calculate Budget"):
            q = f"{bc_city}, days={bc_days}, flight_price={bc_flight}, hotel_price={bc_hotel}, style={bc_style}"
            st.text(estimate_budget.invoke(q))


# ── TAB 3: Chat with Agent ────────────────────────────────────
with tab1:
    st.subheader("💬 Chat with the AI Travel Agent")
    st.info('You can plan trips to these cities: "Delhi", "Mumbai", "Goa", "Bangalore", "Chennai",'
                '"Hyderabad", "Kolkata", "Jaipur"')
    
    # ── Session state initialisation ──────────────────────────
    if "chat_history_display" not in st.session_state:
        st.session_state.chat_history_display = []
    if "chat_history_lc" not in st.session_state:
        st.session_state.chat_history_lc = []
    if "agent_error" not in st.session_state:
        st.session_state.agent_error = None
    if "editing_msg_idx" not in st.session_state:
        st.session_state.editing_msg_idx = None
    if "last_user_input" not in st.session_state:
        st.session_state.last_user_input = None
    if "agent_running" not in st.session_state:
        st.session_state.agent_running = False
 
    # ── Helper: run agent and update state ────────────────────
    def _run_agent_query(query: str) -> None:
        """Run the agent on `query` and update session state accordingly."""
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
 
                    # Collect tool call metadata
                    tools_used = []
                    for step in result.get("steps", []):
                        action = step[0]
                        tools_used.append({
                            "tool": action.tool,
                            "input": str(action.tool_input)[:120],
                        })
 
                    # Show inline
                    if tools_used:
                        with st.expander(f"🔧 Tools called ({len(tools_used)})"):
                            for t in tools_used:
                                st.markdown(
                                    f'<span class="tool-badge">🔧 {t["tool"]}</span> '
                                    f'`{t["input"]}`',
                                    unsafe_allow_html=True,
                                )
                    st.markdown(response)
 
                    # Persist to display history
                    st.session_state.chat_history_display.append({
                        "role": "assistant",
                        "content": response,
                        "tools_used": tools_used,
                        "is_error": False,
                    })
 
                    # Persist to LangChain history
                    st.session_state.chat_history_lc.append(HumanMessage(content=query))
                    st.session_state.chat_history_lc.append(AIMessage(content=response))
 
                    # Clear any previous error on success
                    st.session_state.agent_error = None
 
                except Exception as exc:
                    err_msg = str(exc)
                    st.session_state.agent_error = err_msg
                    st.error(f"⚠️ Agent error: {err_msg}")
                    # Save error message in display history (marked as error)
                    st.session_state.chat_history_display.append({
                        "role": "assistant",
                        "content": f"⚠️ Error: {err_msg}",
                        "is_error": True,
                        "tools_used": [],
                    })
 
        st.session_state.agent_running = False

    # ── API key check banner ───────────────────────────────────
    #api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    #if not api_key:
       # st.warning(
          #  "⚠️ **ANTHROPIC_API_KEY not set.** The agent cannot run without it.\n\n"
          #  "Set it before launching the app:\n"
          #  "```bash\nexport ANTHROPIC_API_KEY=sk-ant-...\nstreamlit run app.py\n```")
    #else:
        #st.success("✅ API key detected — agent is ready.")
 
    st.info(
        "💡 **Tip:** Type a natural language request, e.g.  \n"
        "*'Plan a 3-day trip from Delhi to Goa on a mid-range budget'*"
    )
 
    # ── Control buttons row ────────────────────────────────────
    ctrl_col1, ctrl_col2 = st.columns([1, 4]) # Removed the column for retry button
    with ctrl_col1:
        clear_clicked = st.button("🗑️ Clear Chat", key="clear_chat_btn",
                                   disabled=not st.session_state.chat_history_display)
 
    # Handle clear
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
                    new_text = st.text_area("Edit your message", value=msg["content"], key=f"edit_area_{i}")
                    btn_col1, btn_col2 = st.columns([1, 1])
                    if btn_col1.button("💾 Save", key=f"save_{i}"):
                        if new_text.strip():
                            st.session_state.chat_history_display[i]["content"] = new_text
                            # Truncate history to rerun from this edited message
                            st.session_state.chat_history_display = st.session_state.chat_history_display[:i+1]
                            st.session_state.chat_history_lc = st.session_state.chat_history_lc[:i]
                            st.session_state.editing_msg_idx = None
                            st.session_state.last_user_input = new_text
                            _run_agent_query(new_text)
                            st.rerun()
                    if btn_col2.button("Cancel", key=f"cancel_{i}"):
                        st.session_state.editing_msg_idx = None
                        st.rerun()
                else:
                    st.markdown(msg["content"])
                    # Edit/Delete Buttons
                    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([0.9, 0.05, 0.05])
                    if ctrl_col2.button("✏️", key=f"edit_btn_{i}", help="Edit"):
                        st.session_state.editing_msg_idx = i
                        st.rerun()
                    if ctrl_col3.button("🗑️", key=f"del_btn_{i}", help="Delete"):
                        st.session_state.chat_history_display = st.session_state.chat_history_display[:i]
                        st.session_state.chat_history_lc = st.session_state.chat_history_lc[:i]
                        st.rerun()
            else:
                if msg.get("is_error"):
                    st.error(msg["content"])
                    # Show retry button inside the chat bubble for the latest error
                    if i == len(st.session_state.chat_history_display) - 1 and st.session_state.last_user_input:
                        if st.button("🔄 Retry Last Request", key=f"retry_msg_{i}"):
                            query_to_run = st.session_state.last_user_input
                            # Remove the error message bubble
                            st.session_state.chat_history_display.pop()
                            # Clear global error state
                            st.session_state.agent_error = None
                            _run_agent_query(query_to_run)
                            st.rerun()
                        with st.expander("🛠️ Troubleshooting tips"):
                            st.markdown("""
- **RateLimitError** → Too many requests. Wait a moment and press **Retry Last**.
- **Timeout / Connection error** → Check your internet connection, then retry.
- **Parsing error** → The agent hit a reasoning loop. Press **Retry Last** or rephrase your query.
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
        # Save for potential retry
        st.session_state.last_user_input = user_input
 
        # Show user bubble
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
    LangChain Tool-Calling Agent (Claude)
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
    │   ├── flight_tool.py      # Flight search
    │   ├── hotel_tool.py       # Hotel recommendation
    │   ├── places_tool.py      # Places discovery
    │   ├── weather_tool.py     # Weather lookup
    │   └── budget_tool.py      # Budget estimation
    ├── data/
    │   ├── flights.json
    │   ├── hotels.json
    │   └── places.json
    └── requirements.txt
    ```

    ---
    ## 🚀 How to Run

    ```bash
    # 1. Install dependencies
    pip install -r requirements.txt

    # 2. Set API key (for Chat tab)
    export ANTHROPIC_API_KEY=your_key_here

    # 3. Launch the app
    streamlit run app.py
    ```
    """)
