"""Live Agent Interactive Runner for ADK Self-Authoring Skill Factory

Run this script to interactively ask the Skill Factory to design and write
a new skill using configuration loaded from your .env file.

Usage:
    python agent_live.py
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load credentials and configuration from .env file
load_dotenv()

from google.adk.runners import InMemoryRunner
from google.genai import types
from skill_factory import create_skill_factory_agent, DEFAULT_SKILLS_DIR


async def run_live_factory():
    print("\n\033[1;36mInitializing ADK Skill Factory Agent from .env configuration...\033[0m")
    
    # Display configuration from .env
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION")
    enterprise = os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE")
    
    if enterprise or project:
        print(f"  Configuration : Vertex AI / Enterprise Mode")
        print(f"  Project       : {project}")
        print(f"  Location      : {location}")
    elif os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        print(f"  Configuration : Direct Gemini API")
    else:
        print("  Notice: No explicit credentials in .env, using default environment / ADC.")

    factory_agent = create_skill_factory_agent(model="gemini-2.5-flash")
    runner = InMemoryRunner(agent=factory_agent)

    app_name = runner.app_name
    user_id = "developer"
    session_id = "factory_session_001"

    await runner.session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    user_prompt = (
        "Please create a new skill named 'markdown-table-formatter'. "
        "It should take raw CSV or unformatted text lines and convert them into "
        "a clean, well-aligned Markdown table with column headers. Include detailed instructions."
    )

    print(f"\n\033[1;33mPrompt to Skill Factory:\033[0m {user_prompt}\n")
    print("Generating skill via LLM...")

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_prompt)]
    )

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
                    if part.function_call:
                        print(f"\n\033[36m[Tool Call]\033[0m {part.function_call.name}(...)")
                    if part.function_response:
                        print(f"\033[32m[Tool Response]\033[0m {part.function_response.name}: Success")
    except Exception as e:
        print(f"\n\033[1;31mError during agent run:\033[0m {e}")
        return

    print(f"\n\n\033[1;32mDone! Check the '{DEFAULT_SKILLS_DIR}' directory to inspect the generated skill.\033[0m")


if __name__ == "__main__":
    asyncio.run(run_live_factory())
