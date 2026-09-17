# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from google.adk.agents import SequentialAgent

from app.agent import cloud_arch, root_agent
from app.tools import read_pdf_document


def test_root_agent_configuration():
    """Verify that root_agent is a SequentialAgent with correct properties."""
    assert isinstance(root_agent, SequentialAgent)
    assert root_agent.name == "infra_designer"
    assert len(root_agent.sub_agents) == 4


def test_sequential_agent_order():
    """Verify the exact sequential execution order: CLOUD -> NET -> SEC -> DEV OPS."""
    agent_names = [agent.name for agent in root_agent.sub_agents]
    expected_order = ["cloud_arch", "net_eng", "sec_eng", "dev_ops"]
    assert agent_names == expected_order


def test_subagent_output_keys():
    """Verify each sub-agent stores its output in the designated state key."""
    expected_keys = {
        "cloud_arch": "arch_spec",
        "net_eng": "network_spec",
        "sec_eng": "security_spec",
        "dev_ops": "terraform_infra",
    }
    for sub_agent in root_agent.sub_agents:
        assert sub_agent.output_key == expected_keys[sub_agent.name]


def test_cloud_arch_pdf_tool():
    """Verify cloud_arch has the read_pdf_document tool."""
    tool_names = [
        t.__name__ if hasattr(t, "__name__") else str(t)
        for t in (cloud_arch.tools or [])
    ]
    assert "read_pdf_document" in tool_names


def test_read_pdf_document_nonexistent():
    """Verify error handling for missing PDF files."""
    result = read_pdf_document("non_existent_file_xyz.pdf")
    assert "Error: PDF file" in result
    assert "not found" in result


def test_read_pdf_document_valid():
    """Verify reading a valid PDF file returns expected text content."""
    sample_pdf = os.path.join(
        os.path.dirname(__file__), "..", "..", "samples", "ecommerce_requirements.pdf"
    )
    if os.path.exists(sample_pdf):
        result = read_pdf_document(sample_pdf)
        assert "=== Document: ecommerce_requirements.pdf" in result
        assert "Target Cloud Provider: Google Cloud Platform" in result
        assert "Cloud Run" in result
