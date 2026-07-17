from google.adk.agents.llm_agent import Agent

def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    # Replace with real API call
    return {"city": city, "temp_c": 22}


def get_time(city: str) -> str:
    """Get current local time for a city."""
    return "15:42 JST"


root_agent = Agent(
    name="travel_helper",
    model="gemini-2.5-flash",
    tools=[get_weather, get_time],
)