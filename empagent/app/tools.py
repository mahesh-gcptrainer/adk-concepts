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

import random

def create_emp_id(employee_name: str) -> dict:
    """Generate an Employee ID (Emp ID) for a new employee.

    Args:
        employee_name: Full name of the new employee.

    Returns:
        A dict containing status, employee_name, and the generated emp_id.
    """
    random_num = random.randint(1000, 9999)
    emp_id = f"EMP-{random_num}"
    return {
        "status": "success",
        "employee_name": employee_name,
        "emp_id": emp_id,
        "message": f"Employee ID {emp_id} created successfully for {employee_name}."
    }


def order_laptop(employee_name: str, emp_id: str = "") -> dict:
    """Order a laptop for a new employee.

    Args:
        employee_name: Full name of the new employee.
        emp_id: Employee ID of the employee if available.

    Returns:
        A dict confirming the laptop order.
    """
    return {
        "status": "success",
        "employee_name": employee_name,
        "emp_id": emp_id,
        "item": "Corporate Laptop (MacBook Pro / ThinkPad)",
        "message": f"Laptop ordered successfully for {employee_name}."
    }


def schedule_next_month_salary(employee_name: str, emp_id: str = "") -> dict:
    """Schedule next month's salary payout for a new employee.

    Args:
        employee_name: Full name of the new employee.
        emp_id: Employee ID of the employee if available.

    Returns:
        A dict confirming the scheduled salary payout.
    """
    return {
        "status": "success",
        "employee_name": employee_name,
        "emp_id": emp_id,
        "payroll_status": "Scheduled for next month",
        "message": f"Next month salary scheduled successfully for {employee_name}."
    }


def turn_on_cab(employee_name: str) -> dict:
    """Turn on cab / commute service for a new employee.

    Args:
        employee_name: Full name of the new employee.

    Returns:
        A dict confirming cab service activation.
    """
    return {
        "status": "success",
        "employee_name": employee_name,
        "cab_service": "Active",
        "message": f"Cab service activated successfully for {employee_name}."
    }


def enable_facilities(employee_name: str) -> dict:
    """Enable facilities access (building access badge, desk allocation) for a new employee.

    Args:
        employee_name: Full name of the new employee.

    Returns:
        A dict confirming facilities activation.
    """
    return {
        "status": "success",
        "employee_name": employee_name,
        "facilities": ["Building Badge", "Desk Allocation", "Access Keycard"],
        "message": f"Facilities and building access turned on successfully for {employee_name}."
    }
