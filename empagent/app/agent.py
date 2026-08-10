# ruff: noqa
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

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.tools import (
    create_emp_id,
    order_laptop,
    schedule_next_month_salary,
    turn_on_cab,
    enable_facilities,
)


MODEL = "gemini-3.6-flash"


# Subagent 1: IT Subagent (Make Emp ID, order laptop)
it_subagent = Agent(
    name="it_subagent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Handles IT onboarding: Creates Employee ID (Emp ID) and orders laptop.",
    instruction=(
        "You are the IT Subagent. When onboarding a new employee, perform IT tasks:\n"
        "1. Create an Employee ID (Emp ID) using the `create_emp_id` tool.\n"
        "2. Order a corporate laptop using the `order_laptop` tool.\n"
        "Summarize the IT setup once completed."
    ),
    tools=[create_emp_id, order_laptop],
)


# Subagent 2: Payroll Subagent (Schedule next month salary)
payroll_subagent = Agent(
    name="payroll_subagent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Handles Payroll onboarding: Schedules next month's salary payout.",
    instruction=(
        "You are the Payroll Subagent. When onboarding a new employee, perform Payroll tasks:\n"
        "1. Schedule next month's salary using the `schedule_next_month_salary` tool.\n"
        "Summarize the payroll schedule once completed."
    ),
    tools=[schedule_next_month_salary],
)


# Subagent 3: Shared Service Subagent (Turn on cab, facilities)
shared_service_subagent = Agent(
    name="shared_service_subagent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Handles Shared Services onboarding: Turns on cab service and enables facilities access.",
    instruction=(
        "You are the Shared Service Subagent. When onboarding a new employee, perform Shared Service tasks:\n"
        "1. Turn on cab service using the `turn_on_cab` tool.\n"
        "2. Enable building facilities and desk access using the `enable_facilities` tool.\n"
        "Summarize cab and facilities activation once completed."
    ),
    tools=[turn_on_cab, enable_facilities],
)


# Root Agent: Onboard Coordinator
root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Onboard coordinator root agent that routes new employee onboarding to IT, Payroll, and Shared Service sub-agents.",
    instruction=(
        "You are the Onboard Coordinator (root_agent).\n"
        "When a new employee name enters for onboarding, route and delegate to all 3 sub-agents:\n"
        "1. `it_subagent`: Creates Emp ID and orders laptop.\n"
        "2. `payroll_subagent`: Schedules next month's salary.\n"
        "3. `shared_service_subagent`: Turns on cab service and enables facilities access.\n\n"
        "Coordinate with all three sub-agents and present a complete, organized onboarding summary."
    ),
    sub_agents=[it_subagent, payroll_subagent, shared_service_subagent],
)

app = App(
    root_agent=root_agent,
    name="app",
)
