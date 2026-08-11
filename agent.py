import uuid

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.6-flash"

def generate_employee_id(name: str) -> dict:
    """Generates a unique employee ID for the new employee.
    
    Args:
        name: The name of the employee.
        
    Returns:
        A dictionary containing the generated employee ID.
    """
    emp_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
    return {"employee_name": name, "employee_id": emp_id}

def create_laptop_request(employee_id: str, model_preference: str = "Standard") -> dict:
    """Creates a laptop provisioning request for the employee.
    
    Args:
        employee_id: The ID of the employee.
        model_preference: The preferred laptop model (e.g., Mac, Windows).
        
    Returns:
        A dictionary with the laptop request status.
    """
    req_id = f"REQ-{uuid.uuid4().hex[:6].upper()}"
    return {"employee_id": employee_id, "request_id": req_id, "status": "approved"}

def setup_payroll(employee_id: str, start_date: str) -> dict:
    """Sets up the payroll account to credit salary for the next month.
    
    Args:
        employee_id: The employee ID.
        start_date: The start date of the employee in YYYY-MM-DD format.
        
    Returns:
        A dictionary confirming payroll setup.
    """
    return {"employee_id": employee_id, "payroll_status": "configured_for_next_month"}

def enable_facilities(employee_id: str, facilities: list[str]) -> dict:
    """Enables shared services such as cabs, gym, and building access.
    
    Args:
        employee_id: The employee ID.
        facilities: A list of facilities to enable (e.g., ['cab', 'gym']).
        
    Returns:
        A dictionary with the status of enabled facilities.
    """
    return {"employee_id": employee_id, "enabled_facilities": facilities, "status": "active"}


it_agent = Agent(
    name="it_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="You are the IT Onboarding Agent. Your job is to generate an employee ID and create a laptop request.",
    description="Handles IT provisioning: generating employee IDs and creating laptop requests.",
    tools=[generate_employee_id, create_laptop_request]
)

payroll_agent = Agent(
    name="payroll_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="You are the Payroll Onboarding Agent. Your job is to set up payroll for the new employee to credit their salary next month.",
    description="Handles payroll setup to credit salary next month.",
    tools=[setup_payroll]
)

facilities_agent = Agent(
    name="facilities_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="You are the Facilities Onboarding Agent. Your job is to enable shared services like cabs and other facilities.",
    description="Handles facilities setup: enabling cabs, gym, and building access.",
    tools=[enable_facilities]
)

root_agent = Agent(
    name="coordinator_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction=(
        "You are the Onboarding Coordinator Agent. When an employee is onboarded with a name, "
        "you must delegate the request to the appropriate sub-agents to complete the process. "
        "1. First, delegate to the it_agent to generate an employee ID and laptop request. "
        "2. Then, delegate to the payroll_agent to set up payroll. "
        "3. Finally, delegate to the facilities_agent to enable cabs and other facilities. "
        "Coordinate the flow of information (like the generated employee ID) between these agents."
    ),
    sub_agents=[it_agent, payroll_agent, facilities_agent]
)

app = App(
    root_agent=root_agent,
    name="app",
)
