from __future__ import annotations

from typing import Any

from ..llm_client import OpenAILlmClient
from ..schemas import TEST_CHARTER_SCHEMA, validate_required_keys


def run_test_design_agent(
    client: OpenAILlmClient,
    prompt: str,
    requirement_breakdown: dict[str, Any],
    knowledge_context: dict[str, Any],
) -> dict[str, Any]:
    data = client.generate_json(
        name="test_charter_design",
        system_prompt=prompt,
        user_prompt=(
            "请基于需求、测试点和测试知识设计实时探索测试任务。\n\n"
            f"需求与测试点：\n{requirement_breakdown}\n\n"
            f"测试知识：\n{knowledge_context}"
        ),
        schema=TEST_CHARTER_SCHEMA,
    )
    validate_required_keys("test_charter_design", data, TEST_CHARTER_SCHEMA)
    _validate_charter_traceability(data, requirement_breakdown)
    return data


def _validate_charter_traceability(
    test_design: dict[str, Any], requirement_breakdown: dict[str, Any]
) -> None:
    requirement_ids = {item["requirement_id"] for item in requirement_breakdown["requirements"]}
    test_point_ids = {item["test_point_id"] for item in requirement_breakdown["test_points"]}
    charter_ids = [item["charter_id"] for item in test_design["test_charters"]]
    if len(charter_ids) != len(set(charter_ids)):
        raise ValueError("Test Design Agent returned duplicate charter_id values")
    for charter in test_design["test_charters"]:
        if charter["requirement_id"] not in requirement_ids:
            raise ValueError(
                f"Test charter {charter['charter_id']} references unknown requirement_id "
                f"{charter['requirement_id']}"
            )
        if charter["test_point_id"] not in test_point_ids:
            raise ValueError(
                f"Test charter {charter['charter_id']} references unknown test_point_id "
                f"{charter['test_point_id']}"
            )
