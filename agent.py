"""
Travel Planning Agent
Builds a LangChain ReAct agent that autonomously creates trip itineraries
using the five travel tools: flights, hotels, places, weather, and budget.
"""

#import os
#from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
#from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.llms import Ollama
from tools.flight_tool import search_flights
from tools.hotel_tool import recommend_hotels
from tools.places_tool import discover_places
from tools.weather_tool import get_weather
from tools.budget_tool import estimate_budget
import streamlit as st
# ──────────────────────────────────────────────────────────────
# System Prompt
# ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert AI Travel Planning Assistant for India. 
Your job is to create complete, personalized trip itineraries.

## Your capabilities:
- **search_flights**: Find flights between Indian cities. Don't show flight dates unless provided.
- **recommend_hotels**: Find hotels by city and budget. Show all options and a recommendation.
- **discover_places**: Discover attractions and POIs.
- **get_weather**: Get forecast for the destination city.
- **estimate_budget**: Calculate total trip cost using flight and hotel data.

## Instructions:
1. Call the necessary tools to gather real-world data. **Never make up prices, names, or weather.**
2. Once all data is collected, provide a **single, final response** strictly following the output format.

## Output Format:
Produce your final response exactly in this structure:

```
🌍 TRIP SUMMARY
===============
[City], [Duration] | [Travel Style]

🌤️ WEATHER FORECAST
--------------------
[Directly insert the complete output from the get_weather tool here, preserving its original formatting.follow this formatting strictly]

✈️ FLIGHT SELECTED
------------------
[Directly insert the complete output from the search_flights tool here, preserving its original formatting.follow this formatting strictly]

🏨 HOTEL RECOMMENDATION
-----------------------
[Directly insert the complete output from the recommend_hotels tool here, preserving its original formatting.follow this formatting strictly alos provide the recommendation from that ]

📅 DAY-WISE ITINERARY
---------------------
Day 1: [Detailed activities for Day 1]
Day 2: [Detailed activities for Day 2]
(Continue this list, ensuring each day starts on a new line)

💰 BUDGET BREAKDOWN
-------------------
[Directly insert the complete output from the estimate_budget tool here, preserving its original formatting.follow this formatting strictly]

💡 TRAVEL TIPS
--------------
[2-3 practical tips for the destination]
```
## Rules:
- Always call tools — never make up flight prices, hotel names, or weather.
- If no direct flight exists, say so and suggest options.
- **Format the Day-wise itinerary as a strict vertical list (one day per line).**
- Spread the top-rated places across trip days (max 2-3 per day).
- Be specific with timings and recommendations.
- Keep the tone friendly and informative.
"""

def build_agent(verbose: bool = True) -> AgentExecutor:
    """
    Build and return the LangChain Tool-Calling Agent with all travel tools.

    Args:
        verbose: If True, prints intermediate reasoning steps.

    Returns:
        AgentExecutor ready to process travel queries.
    """
    # Initialize  LLM
    api_key3 = st.secrets['api_key3']
    api_key = st.secrets['api_key']
    api_key2 = st.secrets['api_key2']
    
    llm = ChatGoogleGenerativeAI(api_key=api_key3,model="gemini-2.5-flash")

    llm1 = ChatZhipuAI(api_key=api_key, model='GLM-4.7-Flash')
    llm2 = ChatZhipuAI(api_key=api_key2, model='GLM-4.5-Flash')
    # Build the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    ALL_TOOLS=[search_flights, recommend_hotels, discover_places, get_weather, estimate_budget]
    # Create the tool-calling agent
    agent = create_tool_calling_agent(llm2, ALL_TOOLS, prompt)

    # Wrap in executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=verbose,
        max_iterations=40,
        handle_parsing_errors=True,
        return_intermediate_steps=True)

    return agent_executor


def run_agent(query: str, chat_history: list = None, verbose: bool = True) -> dict:
    """
    Run the travel agent on a user query.

    Args:
        query       : User's travel request in natural language.
        chat_history: Optional list of prior conversation messages.
        verbose     : Whether to print intermediate steps.

    Returns:
        dict with 'output' (final answer) and 'steps' (tool calls made).
    """
    agent = build_agent(verbose=verbose)
    history = chat_history or []

    result = agent.invoke({
        "input": query,
        "chat_history": history,
    })

    return {
        "output": result.get("output", ""),
        "steps": result.get("intermediate_steps", []),
    }


# ──────────────────────────────────────────────────────────────
# Quick CLI test
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_query = (
        "Plan a 3-day trip from Chennai to Goa. "
        "I prefer a mid-range budget with a good hotel. "
        "I love beaches and historical sites."
    )

    print("=" * 60)
    print("🧳 AI Travel Planning Assistant")
    print("=" * 60)
    print(f"Query: {test_query}\n")

    result = run_agent(test_query)
    print("\n" + "=" * 60)
    print("FINAL ITINERARY:")
    print("=" * 60)
    print(result["output"])
