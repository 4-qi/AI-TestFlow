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
                    "knowledge_refs": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "requirement_id",
                    "module",
                    "business_rule",
                    "acceptance_criteria",
                    "risk_level",
                    "knowledge_refs",
                ],
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
                    "priority": {"type": "string", "enum": ["P0", "P1", "P2"]},
                    "knowledge_refs": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "test_point_id",
                    "requirement_id",
                    "title",
                    "test_type",
                    "priority",
                    "knowledge_refs",
                ],
            },
        },
    },
    "required": ["requirements", "test_points"],
}


TEST_CHARTER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "test_charters": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "charter_id": {"type": "string"},
                    "requirement_id": {"type": "string"},
                    "test_point_id": {"type": "string"},
                    "goal": {"type": "string"},
                    "channel": {"type": "string", "enum": ["api", "browser"]},
                    "preconditions": {"type": "string"},
                    "test_data_strategy": {"type": "string"},
                    "expected_result": {"type": "string"},
                    "priority": {"type": "string", "enum": ["P0", "P1", "P2"]},
                    "knowledge_refs": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "charter_id",
                    "requirement_id",
                    "test_point_id",
                    "goal",
                    "channel",
                    "preconditions",
                    "test_data_strategy",
                    "expected_result",
                    "priority",
                    "knowledge_refs",
                ],
            },
        }
    },
    "required": ["test_charters"],
}


API_ACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "action": {"type": "string", "enum": ["request", "finish"]},
        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
        "path": {"type": "string"},
        "headers": {"type": "object"},
        "query": {"type": "object"},
        "body": {"type": "object"},
        "status": {"type": "string", "enum": ["passed", "failed", "blocked"]},
        "actual_result": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["action"],
}


BROWSER_ACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "action": {
            "type": "string",
            "enum": ["navigate", "fill", "click", "press", "select_option", "check", "scroll", "wait", "finish"],
        },
        "target": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "strategy": {"type": "string", "enum": ["role", "label", "text", "placeholder"]},
                "role": {"type": "string"},
                "value": {"type": "string"},
            },
            "required": ["strategy", "value"],
        },
        "path": {"type": "string"},
        "value": {"type": "string"},
        "key": {"type": "string"},
        "option": {"type": "string"},
        "direction": {"type": "string", "enum": ["up", "down"]},
        "milliseconds": {"type": "integer"},
        "status": {"type": "string", "enum": ["passed", "failed", "blocked"]},
        "actual_result": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["action"],
}


DEFECT_ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "status": {"type": "string"},
        "classifications": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "execution_type": {"type": "string", "enum": ["api", "browser"]},
                    "execution_id": {"type": "string"},
                    "charter_id": {"type": "string"},
                    "classification": {
                        "type": "string",
                        "enum": ["product_defect", "test_data_issue", "environment_failure", "agent_blocked", "passed"],
                    },
                    "reason": {"type": "string"},
                },
                "required": ["execution_type", "execution_id", "charter_id", "classification", "reason"],
            },
        },
        "defects": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "bug_id": {"type": "string"},
                    "title": {"type": "string"},
                    "requirement_id": {"type": "string"},
                    "charter_id": {"type": "string"},
                    "execution_type": {"type": "string", "enum": ["api", "browser"]},
                    "execution_id": {"type": "string"},
                    "expected": {"type": "string"},
                    "actual": {"type": "string"},
                    "severity": {"type": "string"},
                    "priority": {"type": "string"},
                    "reproduction_steps": {"type": "array", "items": {"type": "string"}},
                    "evidence_paths": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "bug_id",
                    "title",
                    "requirement_id",
                    "charter_id",
                    "execution_type",
                    "execution_id",
                    "expected",
                    "actual",
                    "severity",
                    "priority",
                    "reproduction_steps",
                    "evidence_paths",
                ],
            },
        },
    },
    "required": ["status", "classifications", "defects"],
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
