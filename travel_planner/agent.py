from google.adk import Agent
from pydantic import BaseModel, Field

# 1. Define Standard Tools
def get_weather(city: str) -> str:
    """Get the mock weather for a city."""
    mock_weather = {
        "Paris": "Sunny, 22°C",
        "Tokyo": "Rainy, 18°C",
        "NYC": "Cloudy, 15°C",
        "Bangalore": "Sunny, 28°C"
    }
    return mock_weather.get(city, f"Unknown weather for {city}, assume 20°C and clear.")

# 2. Define Pydantic Schemas for Structured Tools
class FlightInput(BaseModel):
    origin: str = Field(description="Origin city code (e.g. SFO)")
    destination: str = Field(description="Destination city code (e.g. CDG)")
    date: str = Field(description="Date of the flight")

class FlightResult(BaseModel):
    flight_number: str
    price_usd: int
    status: str

# 3. Define Structured Tools
def search_flights(flight_input: FlightInput) -> str:
    """Search for flights."""
    return f"Found flight UA123 from {flight_input.origin} to {flight_input.destination} on {flight_input.date} for $450."

def book_flight(flight_input: FlightInput) -> FlightResult:
    """Book a flight."""
    return FlightResult(
        flight_number="UA123",
        price_usd=450,
        status="Booked"
    )

# 4. Define Sub-Agents
weather_checker = Agent(
    name="weather_checker",
    model="gemini-2.5-flash",
    mode="single_turn",
    tools=[get_weather],
    instruction="Check the weather for a city using the provided tool. Return only the result."
)

flight_booker = Agent(
    name="flight_booker",
    model="gemini-2.5-flash",
    mode="task",
    tools=[search_flights, book_flight],
    instruction="You help users search and book flights. Use the tools available. Ask clarifying questions if needed. When booking is complete, you are done."
)

# 5. Define Root Agent (Orchestrator)
root_agent = Agent(
    name="travel_planner",
    model="gemini-2.5-flash",
    sub_agents=[weather_checker, flight_booker],
    instruction=(
        "You are a travel coordinator. Delegate weather questions to the weather_checker, "
        "and flight bookings to the flight_booker. For complex requests, use both appropriately."
    )
)