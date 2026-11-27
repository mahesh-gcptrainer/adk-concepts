import pathlib
from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

skills_root = pathlib.Path(__file__).parent / ".agents" / "skills"

caveman_core = load_skill_from_dir(skills_root / "caveman")
caveman_compress = load_skill_from_dir(skills_root / "caveman-compress")

root_agent = Agent(
    model="gemini-2.5-pro",
    name="token_efficient_agent",
    instruction="Use your loaded skills to minimize output token usage when requested.",
    tools=[skill_toolset.SkillToolset(skills=[caveman_core, caveman_compress])],
)