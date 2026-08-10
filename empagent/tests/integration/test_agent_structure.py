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

from app.agent import (
    root_agent,
    it_subagent,
    payroll_subagent,
    shared_service_subagent,
    app,
)


def test_root_agent_structure():
    assert root_agent.name == "root_agent"
    sub_agent_names = [sa.name for sa in root_agent.sub_agents]
    assert "it_subagent" in sub_agent_names
    assert "payroll_subagent" in sub_agent_names
    assert "shared_service_subagent" in sub_agent_names


def test_subagent_tools():
    it_tool_names = [tool.__name__ for tool in it_subagent.tools]
    assert "create_emp_id" in it_tool_names
    assert "order_laptop" in it_tool_names

    payroll_tool_names = [tool.__name__ for tool in payroll_subagent.tools]
    assert "schedule_next_month_salary" in payroll_tool_names

    shared_tool_names = [tool.__name__ for tool in shared_service_subagent.tools]
    assert "turn_on_cab" in shared_tool_names
    assert "enable_facilities" in shared_tool_names


def test_app_config():
    assert app.name == "app"
    assert app.root_agent.name == "root_agent"
