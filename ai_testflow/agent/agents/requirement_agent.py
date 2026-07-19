from __future__ import annotations

from typing import Any

from ..llm_client import OpenAILlmClient
from ..schemas import REQUIREMENT_BREAKDOWN_SCHEMA, validate_required_keys


def run_requirement_agent(
    client: OpenAILlmClient,
    prompt: str,
    prd_analysis: dict[str, Any],
    knowledge_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = client.generate_json(
        name="requirement_breakdown",
        system_prompt=prompt,
        user_prompt=(
            "请基于 PRD 分析结果和检索到的测试知识拆解可测试需求和测试点。\n\n"
            f"PRD 分析：\n{prd_analysis}\n\n"
            f"测试知识：\n{knowledge_context or {'selected_items': []}}"
        ),
        schema=REQUIREMENT_BREAKDOWN_SCHEMA,
    )
    validate_required_keys("requirement_breakdown", data, REQUIREMENT_BREAKDOWN_SCHEMA)
    _validate_requirement_traceability(data, prd_analysis)
    return data


def _validate_requirement_traceability(
    requirement_breakdown: dict[str, Any], prd_analysis: dict[str, Any]
) -> None:
    source_ids = [item["requirement_id"] for item in prd_analysis["functional_requirements"]]
    generated_ids = [item["requirement_id"] for item in requirement_breakdown["requirements"]]
    if len(generated_ids) != len(set(generated_ids)):
        raise ValueError("Requirement Agent returned duplicate requirement_id values")
    if set(generated_ids) != set(source_ids):
        raise ValueError(
            "Requirement Agent must preserve the exact PRD requirement_id set. "
            f"Expected {sorted(source_ids)}, got {sorted(generated_ids)}"
        )
    invalid_test_points = sorted(
        {
            item["requirement_id"]
            for item in requirement_breakdown["test_points"]
            if item["requirement_id"] not in set(source_ids)
        }
    )
    if invalid_test_points:
        raise ValueError(
            "Requirement Agent test points reference unknown requirement_id values: "
            + ", ".join(invalid_test_points)
        )
