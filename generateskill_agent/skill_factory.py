"""ADK Self-Authoring Skill Factory

This module implements:
1. `write_skill`: Tool that allows an agent to author, validate, and persist
   a new skill adhering to the Google ADK Skill specification (SKILL.md).
2. `DirectorySkillRegistry`: A dynamic ADK SkillRegistry that discovers
   skills created on the fly in the skills repository.
3. `create_skill_factory_agent`: ADK Agent configured to design and generate skills.
4. `create_skill_consumer_agent`: ADK Agent configured with SkillToolset to
   discover and execute newly minted skills.
"""

import os
import re
import pathlib
from typing import Any, Optional
import yaml
from dotenv import load_dotenv

# Load configuration from .env file
load_dotenv()

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir, Skill, Frontmatter
from google.adk.skills.skill_registry import SkillRegistry
from google.adk.tools.skill_toolset import SkillToolset

DEFAULT_SKILLS_DIR = pathlib.Path(__file__).parent / "skills"


def sanitize_skill_name(name: str) -> str:
    """Ensures skill name is valid lowercase kebab-case (a-z, 0-9, hyphens)."""
    clean = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    clean = re.sub(r"-+", "-", clean)
    return clean or "custom-skill"


def write_skill(
    name: str,
    description: str,
    instructions: str,
    script_name: Optional[str] = None,
    script_code: Optional[str] = None,
    skills_dir: Optional[str] = None,
) -> dict[str, Any]:
    """Writes a new ADK-compliant skill with frontmatter and instructions.

    Args:
        name: Skill name (will be converted to kebab-case).
        description: Description explaining what the skill does and when to use it.
        instructions: Markdown instructions detailing the steps for the skill.
        script_name: Optional filename for an executable script (e.g. 'calc.py').
        script_code: Optional source code for the bundled script.
        skills_dir: Optional custom skills folder path.

    Returns:
        A dictionary containing the status, skill name, and file paths.
    """
    target_base = pathlib.Path(skills_dir) if skills_dir else DEFAULT_SKILLS_DIR
    target_base.mkdir(parents=True, exist_ok=True)

    skill_name = sanitize_skill_name(name)
    skill_dir = target_base / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Format standard SKILL.md with YAML frontmatter
    frontmatter_dict = {
        "name": skill_name,
        "description": description.strip(),
    }
    frontmatter_yaml = yaml.dump(frontmatter_dict, sort_keys=False).strip()
    skill_md_content = f"---\n{frontmatter_yaml}\n---\n\n{instructions.strip()}\n"

    skill_md_path = skill_dir / "SKILL.md"
    skill_md_path.write_text(skill_md_content, encoding="utf-8")

    written_files = [str(skill_md_path)]

    # Optional: write bundled helper script
    if script_name and script_code:
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / script_name
        script_path.write_text(script_code.strip() + "\n", encoding="utf-8")
        written_files.append(str(script_path))

    # Validate that the generated skill is readable by ADK
    validated_skill = load_skill_from_dir(skill_dir)

    return {
        "status": "success",
        "skill_name": validated_skill.name,
        "description": validated_skill.frontmatter.description,
        "skill_dir": str(skill_dir),
        "files": written_files,
        "has_scripts": bool(validated_skill.resources.scripts),
    }


class DirectorySkillRegistry(SkillRegistry):
    """Dynamic SkillRegistry that scans a local directory for runtime-created skills."""

    def __init__(self, skills_dir: Optional[pathlib.Path] = None):
        self.skills_dir = skills_dir or DEFAULT_SKILLS_DIR

    async def get_skill(self, *, name: str) -> Skill:
        skill_dir = self.skills_dir / name
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
            raise FileNotFoundError(f"Skill '{name}' not found in {self.skills_dir}")
        return load_skill_from_dir(skill_dir)

    async def search_skills(self, *, query: str) -> list[Frontmatter]:
        matches: list[Frontmatter] = []
        if not self.skills_dir.exists():
            return matches

        query_lower = query.lower()
        for item in sorted(self.skills_dir.iterdir()):
            if item.is_dir() and (item / "SKILL.md").exists():
                try:
                    skill = load_skill_from_dir(item)
                    if (
                        query_lower in skill.name.lower()
                        or query_lower in (skill.frontmatter.description or "").lower()
                    ):
                        matches.append(skill.frontmatter)
                except Exception:
                    continue
        return matches


def create_skill_factory_agent(model: str = "gemini-2.5-flash") -> Agent:
    """Creates an ADK agent whose primary capability is authoring new skills."""
    return Agent(
        name="skill_factory",
        model=model,
        instruction="""You are the Skill Factory Agent.
Your role is to author reusable, modular skills for other AI agents to execute.

When asked to create a skill:
1. Determine a clear, kebab-case skill name (e.g. 'sla-compliance-auditor', 'json-schema-validator').
2. Write a clear description specifying what the skill does and when an agent should use it.
3. Formulate detailed, high-quality Markdown instructions:
   - Objective
   - Step-by-step procedure
   - Expected input format and output format
   - Edge cases and guidelines
4. If the skill involves deterministic calculations, data parsing, or validation, provide a clean Python script.
5. Invoke the `write_skill` tool to persist the new skill.
""",
        tools=[write_skill],
    )


def create_skill_consumer_agent(
    registry: Optional[SkillRegistry] = None,
    model: str = "gemini-2.5-flash",
) -> Agent:
    """Creates a worker agent equipped with ADK's SkillToolset to use generated skills."""
    reg = registry or DirectorySkillRegistry()
    skill_toolset = SkillToolset(registry=reg)

    return Agent(
        name="task_worker",
        model=model,
        instruction="""You are an adaptive worker agent.
You have access to a skills registry. When given a task:
1. Search for available skills using `search_skills`.
2. Load relevant skills using `load_skill`.
3. Follow the skill's instructions carefully to complete the task.
""",
        tools=[skill_toolset],
    )
