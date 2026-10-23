"""Unit and integration tests for the Sequential Multi-Agent Cloud Infrastructure Pipeline."""

import os
import pytest
from pathlib import Path
from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types

from app.agent import root_agent, app
from app.agents import (
    cloud_architect_agent,
    network_engineer_agent,
    security_engineer_agent,
    devops_engineer_agent,
)
from app.tools.pdf_loader import extract_pdf_text, load_pdf_as_adk_content


def test_agent_classes():
    """Verify all four specialized agents are implemented using the LlmAgent class."""
    agents = [
        cloud_architect_agent,
        network_engineer_agent,
        security_engineer_agent,
        devops_engineer_agent,
    ]
    for ag in agents:
        assert isinstance(ag, LlmAgent), f"{ag.name} must be an instance of LlmAgent"


def test_agent_output_keys():
    """Verify each agent has an appropriate output_key for state propagation."""
    assert cloud_architect_agent.output_key == "cloud_architecture_spec"
    assert network_engineer_agent.output_key == "network_spec"
    assert security_engineer_agent.output_key == "security_spec"
    assert devops_engineer_agent.output_key == "devops_terraform_spec"


def test_sequential_agent_order():
    """Verify root_agent is a SequentialAgent and executes in the exact requested sequence:
    Cloud Architect -> Network Engineer -> Security Engineer -> DevOps Engineer
    """
    assert isinstance(root_agent, SequentialAgent), "root_agent must be an instance of SequentialAgent"
    assert len(root_agent.sub_agents) == 4, "SequentialAgent must contain exactly 4 sub-agents"

    expected_sequence = [
        "cloud_architect_agent",
        "network_engineer_agent",
        "security_engineer_agent",
        "devops_engineer_agent",
    ]
    actual_sequence = [ag.name for ag in root_agent.sub_agents]
    assert actual_sequence == expected_sequence, f"Expected {expected_sequence}, got {actual_sequence}"


def test_pdf_extraction_tool():
    """Verify PDF extraction tool reads the case study PDF properly."""
    sample_pdf = Path(__file__).parent.parent / "sample_case_study.pdf"
    assert sample_pdf.exists(), "sample_case_study.pdf should exist for testing"

    result = extract_pdf_text(str(sample_pdf))
    assert result["status"] == "success"
    assert result["page_count"] >= 1
    assert "Apex Global Financial Services" in result["extracted_text"]
    assert "Google Cloud Platform" in result["extracted_text"]


def test_pdf_multimodal_content_loader():
    """Verify load_pdf_as_adk_content produces valid Gemini multimodal Content."""
    sample_pdf = Path(__file__).parent.parent / "sample_case_study.pdf"
    content = load_pdf_as_adk_content(str(sample_pdf), prompt_text="Test prompt")

    assert isinstance(content, types.Content)
    assert len(content.parts) == 2

    # First part should be PDF bytes
    pdf_part = content.parts[0]
    assert pdf_part.inline_data.mime_type == "application/pdf"
    assert len(pdf_part.inline_data.data) > 0

    # Second part should be text prompt
    text_part = content.parts[1]
    assert text_part.text == "Test prompt"
