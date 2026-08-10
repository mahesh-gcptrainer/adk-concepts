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

from app.tools import (
    create_emp_id,
    order_laptop,
    schedule_next_month_salary,
    turn_on_cab,
    enable_facilities,
)


def test_create_emp_id():
    result = create_emp_id("John Doe")
    assert result["status"] == "success"
    assert result["employee_name"] == "John Doe"
    assert result["emp_id"].startswith("EMP-")


def test_order_laptop():
    result = order_laptop("John Doe", "EMP-1234")
    assert result["status"] == "success"
    assert result["employee_name"] == "John Doe"
    assert result["emp_id"] == "EMP-1234"


def test_schedule_next_month_salary():
    result = schedule_next_month_salary("John Doe", "EMP-1234")
    assert result["status"] == "success"
    assert result["employee_name"] == "John Doe"
    assert result["payroll_status"] == "Scheduled for next month"


def test_turn_on_cab():
    result = turn_on_cab("John Doe")
    assert result["status"] == "success"
    assert result["employee_name"] == "John Doe"
    assert result["cab_service"] == "Active"


def test_enable_facilities():
    result = enable_facilities("John Doe")
    assert result["status"] == "success"
    assert result["employee_name"] == "John Doe"
    assert "Building Badge" in result["facilities"]
