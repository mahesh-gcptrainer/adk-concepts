#pip install "google-adk[db]" aiosqlite

from google.adk import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    instruction='Answer user questions to the best of your knowledge',
)

runner = Runner(
    app_name='my_app',
    agent=root_agent,
    session_service=DatabaseSessionService(
        db_url="sqlite+aiosqlite:///.adk/sessions_mahesh.db"
    ) 
)