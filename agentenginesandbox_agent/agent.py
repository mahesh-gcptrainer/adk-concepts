import os
from google.adk.agents import LlmAgent
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

AGENT_ENGINE_RESOURCE = os.getenv("AGENT_ENGINE_RESOURCE_NAME")

root_agent = LlmAgent(
    name="sandbox_code_agent",
    model="gemini-2.5-flash",
    code_executor=AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name=AGENT_ENGINE_RESOURCE,
        # sandbox_resource_name=SANDBOX_RESOURCE,  # Use this instead of agent_engine_resource_name to reuse an existing sandbox
    ),
    instruction=(
        "You are a precise data and math assistant. "
        "Always write and execute Python code to verify calculations, "
        "run simulations, or process data rather than doing math mentally."
    ),
    description="Executes Python code in a sandboxed environment to solve problems."
)