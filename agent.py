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
# ──────────────────────────────────────────────────────────────
# System Prompt
# ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert AI Travel Planning Assistant for India. 
Your job is to create complete, personalized trip itineraries.

## Your capabilities:
- search_flights       : Find flights between Indian cities
- recommend_hotels     : Find hotels by city, budget, and star rating
- discover_places      : Discover tourist attractions and POIs
- get_weather          : Get weather forecast for the destination
- estimate_budget      : Calculate total trip cost 

## How to respond to a travel request:
1. Understandthe trip: origin, destination, duration, preferences
2. Search flights from origin to destination.show the connecting flights cost in the bracket(follow the budget tool output format strictly)
3. Get weather for the destination (for trip duration) can show in single line for per day
4. Find hotels in the destination and show all of it also provide the best recommendation
5. Discover top places in the destination
6. Estimate budget using the best flight + hotel found if any flight or hotel details are missing calculate for remaining(follow the budget tool output format strictly)
7. Generate a structured itinerary with day-wise plan

## Output Format:
Always produce a final answer in this structure:

```
🌍 TRIP SUMMARY
===============
[City], [Duration] | [Travel Style]

🌤️ WEATHER FORECAST
--------------------
[Directly insert the complete output from the get_weather tool here, preserving its original formatting.follow this formatting strictly]

✈️ FLIGHT SELECTED
------------------
[Flight details from tool]

🏨 HOTEL RECOMMENDATION
-----------------------
[show all hotel details from tool for the distination cities also provide the recommendation ]

📅 DAY-WISE ITINERARY
---------------------
Day 1: [Places to visit]
Day 2: [Places to visit]

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
    # Initialize the Google Gemini LLM
    api_key3='AIzaSyB-RlhWoRhR09UO86z_uk7zUY7dlh30J4Q'
    api_key='32b3477efdef4eae98093e60429796f5.iD5LgyTDO1Pg88dV'
    api_key2='fe530a38259c4de2bc506cf863512984.Mtfh8Sb2nsy97Sgb'
    
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
        max_iterations=10,
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
