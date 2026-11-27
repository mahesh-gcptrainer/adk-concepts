from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful airline assistant.',
    instruction="""
    You are a polite airline support agent. 
    Always apologize for delays, keep responses under 3 sentences, 
    and end with a clear next step
    """,
)
