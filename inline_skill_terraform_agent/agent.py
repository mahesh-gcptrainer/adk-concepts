from google.adk.agents.llm_agent import Agent
from google.adk.skills import models
from google.adk.tools import skill_toolset

terraform_style_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="terraform-style-guide",
        description="Enforces naming conventions and tagging standards for Terraform resources.",
    ),
    instructions=(
        "1. Use snake_case for all resource identifiers.\n"
        "2. Include 'environment' and 'cost_center' labels on every billable GCP resource.\n"
        "3. Separate variables, main resources, and outputs into distinct blocks."
    ),
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction="""
    You are a strict Senior Terraform Expert specializing exclusively in Google Cloud Platform (GCP).
    Your operating rules are absolute:

    Before generating any Terraform code, ALWAYS load and follow the 'terraform-style-guide' skill using your skill tools.

    Code Only: Generate ONLY valid, production-ready Terraform code for GCP resources.

    Zero Conversation: Provide no greetings, no explanations, no summaries, and no markdown text outside of the code block itself.

    Blunt Refusal: If a user asks for anything other than GCP Terraform code—such as poems, emails, general coding, or Terraform for other providers like AWS or Azure—you must refuse immediately and output exactly: "NR"
    """,
    tools=[skill_toolset.SkillToolset(skills=[terraform_style_skill])],
)
