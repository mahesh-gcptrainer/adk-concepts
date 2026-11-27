from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import ToolContext
from google.genai import types


# --- Mock Backend APIs (Replace with real airline microservices) ---
def _fetch_live_flight_api(flight_no: str) -> dict:
    mock_flights = {
        "AI-202": {
            "status": "DELAYED",
            "delay_hours": 3.5,
            "reason": "Weather",
            "next_available": "AI-208 at 6:00 PM",
        },
        "AI-101": {
            "status": "ON_TIME",
            "delay_hours": 0.0,
            "reason": None,
            "next_available": None,
        },
    }
    return mock_flights.get(flight_no.upper(), {"status": "UNKNOWN"})


def _fetch_passenger_crm(user_id: str) -> dict:
    return {"tier": "Gold", "lounge_eligible": True}


# --- Tools (Exposed selectively via Context Engineering) ---
def rebook_flight(new_flight: str, tool_context: ToolContext) -> dict:
    """Rebooks the passenger onto an alternate flight."""
    old_flight = tool_context.state.get("active_flight", "UNKNOWN")
    tool_context.state["rebooked_to"] = new_flight
    return {
        "status": "CONFIRMED",
        "previous_flight": old_flight,
        "new_flight": new_flight,
    }


def check_baggage_status(bag_tag: str) -> dict:
    """Checks checked-in baggage location."""
    return {"bag_tag": bag_tag, "location": "Loaded on aircraft"}


# --- Context Engineering Layer (Runs dynamically before every LLM call) ---
def inject_runtime_context(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Assembles lean runtime state and scopes tools before inference."""
    state = callback_context.state

    # 1. Extract flight number from user message (simple heuristic for demo)
    flight_no = state.get("active_flight", "AI-202")
    if llm_request.contents:
        last_text = "".join(
            part.text or "" for part in llm_request.contents[-1].parts or []
        )
        for token in last_text.replace("?", "").replace(".", "").split():
            if token.upper().startswith("AI-"):
                flight_no = token.upper()
                state["active_flight"] = flight_no

    # 2. Fetch live runtime data (Data Facade pattern)
    flight_info = _fetch_live_flight_api(flight_no)
    #crm_info = _fetch_passenger_crm(callback_context.invocation_context.user_id)
    crm_info = _fetch_passenger_crm(callback_context.user_id or "guest_user")

    # 3. Dynamic Tool Scoping: Only expose `rebook_flight` if delay > 2 hours
    if llm_request.config and llm_request.config.tools:
        is_major_delay = flight_info.get("delay_hours", 0) > 2.0
        scoped_tools = []
        for tool_group in llm_request.config.tools:
            if tool_group.function_declarations:
                filtered_decls = [
                    decl
                    for decl in tool_group.function_declarations
                    if decl.name != "rebook_flight" or is_major_delay
                ]
                if filtered_decls:
                    scoped_tools.append(
                        types.Tool(function_declarations=filtered_decls)
                    )
        llm_request.config.tools = scoped_tools

    # 4. Inject just-in-time context into the system instruction
    runtime_context_block = f"""
[RUNTIME CONTEXT - DO NOT HALLUCINATE BEYOND THIS]
- Passenger Tier: {crm_info['tier']} (Complimentary lounge access on delays > 2 hrs: {crm_info['lounge_eligible']})
- Active Flight: {flight_no}
- Live Status: {flight_info}
"""
    existing_sys = llm_request.config.system_instruction or ""
    llm_request.config.system_instruction = f"{existing_sys}\n{runtime_context_block}"

    return None  # Proceed to call the LLM with the engineered context


# --- Root Agent Definition (Prompt Engineering stays minimal & static) ---
root_agent = LlmAgent(
    name="airline_support_agent",
    model="gemini-2.5-flash",
    description="Airline customer support agent with runtime context injection.",
    instruction=(
        "You are a polite, concise airline support agent. "
        "Keep responses under 3 sentences. Use the injected [RUNTIME CONTEXT] "
        "to answer accurately and offer a clear next step."
    ),
    tools=[rebook_flight, check_baggage_status],
    before_model_callback=inject_runtime_context,
)