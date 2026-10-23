"""Root agent definition managing the sequential multi-agent infrastructure pipeline."""

from google.adk.agents import SequentialAgent
from google.adk.apps import App

from app.agents import (
    cloud_architect_agent,
    network_engineer_agent,
    security_engineer_agent,
    devops_engineer_agent,
)

# Root SequentialAgent orchestrating the exact 4-stage pipeline:
# Cloud Architect -> Network Engineer -> Security Engineer -> DevOps Engineer
root_agent = SequentialAgent(
    name="cloud_infrastructure_pipeline",
    description=(
        "Sequential multi-agent infrastructure system: ingests a case study PDF, "
        "analyzes architecture requirements, designs network topology, hardens security "
        "and compliance, and generates production-ready Terraform code."
    ),
    sub_agents=[
        cloud_architect_agent,
        network_engineer_agent,
        security_engineer_agent,
        devops_engineer_agent,
    ],
)

# Standard ADK App instance
app = App(
    name="app",
    root_agent=root_agent,
)
