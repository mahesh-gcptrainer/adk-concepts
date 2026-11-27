import logging
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

logger = logging.getLogger(__name__)

async def auto_save_session_to_memory(callback_context: CallbackContext):
    inv_ctx = callback_context._invocation_context
    session = inv_ctx.session
    memory_service = inv_ctx.memory_service

    print(f"[Memory Debug] service={type(memory_service)}, events={len(session.events)}")
    if not memory_service:
        print("[Memory Debug] ERROR: memory_service is None! Check --memory_service_uri flag.")
        return

    try:
        await memory_service.add_session_to_memory(session)
        print(f"[Memory Debug] Successfully triggered memory generation for session {session.id}")
    except Exception as e:
        print(f"[Memory Debug] FAILED to add session to memory: {e}")


root_agent = Agent(
    model="gemini-2.5-flash",
    name="memory_enabled_assistant",
    instruction=(
        "You are a helpful assistant. Use any preloaded memories about the user "
        "to personalize your answers without explicitly mentioning that you queried a database."
    ),
    tools=[PreloadMemoryTool()],
    after_agent_callback=auto_save_session_to_memory,
)

#adk web --reload_agents --session_service_uri="agentengine://projects/739157543705/locations/us-central1/reasoningEngines/1432157051009630208" --memory_service_uri="agentengine://projects/739157543705/locations/us-central1/reasoningEngines/1432157051009630208"
#My name is Mahesh, I am a Google Cloud Architect based in Bengaluru, and I always prefer Terraform over Deployment Manager