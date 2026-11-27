from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor

root_agent = LlmAgent(
    name="code_exec_agent",
    model="gemini-2.5-flash",
    code_executor=BuiltInCodeExecutor(),
    instruction=(
        "You are a precise data and math assistant. "
        "Always write and execute Python code to verify calculations, "
        "run simulations, or process data rather than doing math mentally."
    ),
    description="Executes Python code in a sandboxed environment to solve problems."
)