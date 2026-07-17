from google.adk import Agent, Workflow, Event

# 1. Define the LLM Agent
classifier = Agent(
    name="classifier",
    model="gemini-2.5-flash",
    instruction=(
        "First Greet the user and tell me what you can do. Then, once the user says something... "
        "Classify the user message into exactly one of: BUG, BILLING, or FEATURE_REQUEST. "
        "Return ONLY the category in uppercase, nothing else."
    ),
    output_schema=str
)

# 2. Define the Routing Logic
def router(node_input: str) -> Event:
    category = node_input.strip().upper()
    return Event(route=category)

# 3. Define the Handlers
def handle_bug() -> Event:
    return Event(payload="Bug ticket created, engineering notified")

def handle_billing() -> Event:
    return Event(payload="Billing request routed to finance team")

def handle_feature_request() -> Event:
    return Event(payload="Feature request added to product backlog")

# 4. Define the Workflow structure
root_agent = Workflow(
    name="root_agent",
    edges=[
        ("START", classifier, router),
        (router, {
            "BUG": handle_bug,
            "BILLING": handle_billing,
            "FEATURE_REQUEST": handle_feature_request,
        }),
    ]
)