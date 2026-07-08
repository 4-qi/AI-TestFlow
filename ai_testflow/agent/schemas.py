from __future__ import annotations

from typing import Any


PRD_ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "business_goal": {"type": "string"},
        "user_roles": {"type": "array", "items": {"type": "string"}},
        "functional_requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "requirement_id": {"type": "string"},
                    "title": {"type": "string"},
                    "source_text": {"type": "string"},
                    "business_rule": {"type": "string"},
                    "interfaces": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["requirement_id", "title", "source_text", "business_rule", "interfaces"],
            },
        },
        "non_functional_requirements": {"type": "array", "items": {"type": "string"}},
        "interface_scope": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["business_goal", "user_roles", "functional_requirements", "non_functional_requirements", "interface_scope"],
}


REQUIREMENT_BREAKDOWN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "requirement_id": {"type": "string"},
                    "module": {"type": "string"},
                    "business_rule": {"type": "string"},
                    "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
                    "risk_level": {"type": "string"},
                },
                "required": ["requirement_id", "module", "business_rule", "acceptance_criteria", "risk_level"],
            },
        },
        "test_points": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "test_point_id": {"type": "string"},
                    "requirement_id": {"type": "string"},
                    "title": {"type": "string"},
                    "test_type": {"type": "string"},
                    "priority": {"type": "string"},
                },
                "required": ["test_point_id", "requirement_id", "title", "test_type", "priority"],
            },
        },
    },
    "required": ["requirements", "test_points"],
}


TEST_CASE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "test_cases": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "test_case_id": {"type": "string"},
                    "requirement_id": {"type": "string"},
                    "test_point_id": {"type": "string"},
                    "title": {"type": "string"},
                    "precondition": {"type": "string"},
                    "steps": {"type": "array", "items": {"type": "string"}},
                    "test_data": {"type": "string"},
                    "expected_result": {"type": "string"},
                    "priority": {"type": "string"},
                    "automation_type": {"type": "string"},
                },
                "required": [
                    "test_case_id",
                    "requirement_id",
                    "test_point_id",
                    "title",
                    "precondition",
                    "steps",
                    "test_data",
                    "expected_result",
                    "priority",
                    "automation_type",
                ],
            },
        }
    },
    "required": ["test_cases"],
}


SCRIPT_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "api_test_case_ids": {"type": "array", "items": {"type": "string"}},
        "playwright_flows": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "flow_id": {"type": "string", "enum": ["PW-REG-001", "PW-AUTH-001"]},
                    "title": {"type": "string"},
                    "test_case_ids": {"type": "array", "items": {"type": "string"}},
                    "steps": {"type": "array", "items": {"type": "string"}},
                    "expected_result": {"type": "string"},
                },
                "required": ["flow_id", "title", "test_case_ids", "steps", "expected_result"],
            },
        },
    },
    "required": ["api_test_case_ids", "playwright_flows"],
}


DEFECT_ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "status": {"type": "string"},
        "defects": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "bug_id": {"type": "string"},
                    "title": {"type": "string"},
                    "requirement_id": {"type": "string"},
                    "test_case_id": {"type": "string"},
                    "failed_test_name": {"type": "string"},
                    "expected": {"type": "string"},
                    "actual": {"type": "string"},
                    "severity": {"type": "string"},
                    "priority": {"type": "string"},
                    "reproduction_steps": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "bug_id",
                    "title",
                    "requirement_id",
                    "test_case_id",
                    "failed_test_name",
                    "expected",
                    "actual",
                    "severity",
                    "priority",
                    "reproduction_steps",
                ],
            },
        },
    },
    "required": ["status", "defects"],
}


MARKDOWN_DOCUMENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {"markdown": {"type": "string"}},
    "required": ["markdown"],
}


def validate_required_keys(name: str, data: dict[str, Any], schema: dict[str, Any]) -> None:
    required = schema.get("required", [])
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"{name} missing required keys: {', '.join(missing)}")
