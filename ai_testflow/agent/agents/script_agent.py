from __future__ import annotations

from pathlib import Path
from typing import Any

from ...test_generator import render_generated_api_tests, render_generated_playwright_tests
from ..llm_client import OpenAILlmClient
from ..schemas import SCRIPT_PLAN_SCHEMA, validate_required_keys


def run_script_agent(
    client: OpenAILlmClient,
    prompt: str,
    test_cases: list[dict[str, Any]],
    backend_source: str,
    api_test_runtime: dict[str, str],
    api_target: Path,
    playwright_target: Path,
) -> dict[str, Any]:
    script_plan = client.generate_json(
        name="script_plan",
        system_prompt=prompt,
        user_prompt=(
            "请基于测试用例和后端源码生成通用自动化测试动作。\n\n"
            f"测试用例：\n{test_cases}\n\n"
            f"后端源码：\n{backend_source}"
        ),
        schema=SCRIPT_PLAN_SCHEMA,
    )
    validate_required_keys("script_plan", script_plan, SCRIPT_PLAN_SCHEMA)
    script_plan = _align_api_expectations_with_test_cases(script_plan, test_cases)

    api_script = render_generated_api_tests(script_plan["api_tests"], api_test_runtime)
    playwright_script = render_generated_playwright_tests(script_plan["ui_tests"])
    api_target.parent.mkdir(parents=True, exist_ok=True)
    playwright_target.parent.mkdir(parents=True, exist_ok=True)
    api_target.write_text(api_script, encoding="utf-8")
    playwright_target.write_text(playwright_script, encoding="utf-8")
    return {
        "script_plan": script_plan,
        "api_script": str(api_target),
        "playwright_script": str(playwright_target),
    }


def _align_api_expectations_with_test_cases(script_plan: dict[str, Any], test_cases: list[dict[str, Any]]) -> dict[str, Any]:
    test_case_index = {item["test_case_id"]: item for item in test_cases}
    for api_test in script_plan["api_tests"]:
        test_case = test_case_index.get(api_test["test_case_id"])
        if not test_case:
            continue
        if _is_negative_expected_case(test_case) and 200 <= int(api_test["expected_status"]) < 300:
            api_test["expected_status"] = 400
            expected_json = api_test.setdefault("expected_json_contains", {})
            if expected_json.get("success") is True:
                expected_json["success"] = False
    return script_plan


def _is_negative_expected_case(test_case: dict[str, Any]) -> bool:
    text = " ".join(
        str(test_case.get(key, ""))
        for key in ["title", "precondition", "steps", "test_data", "expected_result"]
    )
    negative_terms = [
        "失败",
        "错误",
        "拒绝",
        "不能为空",
        "不能",
        "不允许",
        "不一致",
        "不存在",
        "已存在",
        "长度小于",
        "长度不足",
    ]
    positive_terms = ["成功", "通过", "允许", "正常"]
    if any(term in text for term in negative_terms):
        return True
    return not any(term in text for term in positive_terms)
