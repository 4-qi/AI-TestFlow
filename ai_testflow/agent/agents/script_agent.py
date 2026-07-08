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
    prd_text: str = "",
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
    script_plan = _align_api_expectations_with_test_cases(script_plan, test_cases, prd_text, backend_source)

    script_plan["ui_tests"] = _stable_ui_tests(script_plan["ui_tests"])
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


def _align_api_expectations_with_test_cases(
    script_plan: dict[str, Any],
    test_cases: list[dict[str, Any]],
    prd_text: str = "",
    backend_source: str = "",
) -> dict[str, Any]:
    test_case_index = {item["test_case_id"]: item for item in test_cases}
    for api_test in script_plan["api_tests"]:
        test_case = test_case_index.get(api_test["test_case_id"])
        if not test_case:
            continue
        is_negative = _is_negative_expected_case(test_case)
        if is_negative:
            if 200 <= int(api_test["expected_status"]) < 300:
                api_test["expected_status"] = 400
        _align_blank_username_expectation(api_test, prd_text, backend_source)
        api_test["expected_json_contains"] = _stable_json_expectations(
            api_test.get("expected_json_contains", {}),
            prd_text,
            force_success_false=is_negative or _is_failure_status(api_test),
        )
    return script_plan


def _is_negative_expected_case(test_case: dict[str, Any]) -> bool:
    expected_text = str(test_case.get("expected_result", ""))
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
    positive_terms = ["成功", "通过", "允许", "正常", "200"]
    if any(term in expected_text for term in positive_terms):
        return False
    if any(term in expected_text for term in negative_terms):
        return True
    return False


def _stable_json_expectations(expected_json: dict[str, Any], prd_text: str, force_success_false: bool = False) -> dict[str, Any]:
    stable: dict[str, Any] = {}
    if "success" in expected_json:
        stable["success"] = False if force_success_false else expected_json["success"]

    for key, value in expected_json.items():
        if key == "success":
            continue
        if _is_prd_anchored_json_expectation(key, value, prd_text):
            stable[key] = value
    return stable


def _is_prd_anchored_json_expectation(key: str, value: Any, prd_text: str) -> bool:
    if not prd_text:
        return False
    if key not in prd_text:
        return False
    if isinstance(value, str):
        if not value:
            return False
        return _compact(value) in _compact(prd_text)
    if isinstance(value, dict):
        return any(_is_prd_anchored_json_expectation(str(child_key), child_value, prd_text) for child_key, child_value in value.items())
    return str(value) in prd_text


def _compact(value: str) -> str:
    return "".join(value.split())


def _align_blank_username_expectation(api_test: dict[str, Any], prd_text: str, backend_source: str) -> None:
    json_body = api_test.get("json_body", {})
    username = json_body.get("username")
    if not isinstance(username, str) or username.strip() != "" or username == "":
        return
    if "用户名不能为空" not in prd_text:
        return
    if "username =" not in backend_source or ".strip()" not in backend_source:
        return
    api_test["expected_status"] = 400
    api_test["expected_json_contains"] = {"success": False}


def _is_failure_status(api_test: dict[str, Any]) -> bool:
    return int(api_test.get("expected_status", 200)) >= 400


def _stable_ui_tests(ui_tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stable_tests: list[dict[str, Any]] = []
    for ui_test in ui_tests:
        actions = ui_test.get("actions", [])
        action_names = {action.get("action") for action in actions}
        if "fill_label" in action_names or "click_role" in action_names:
            continue
        stable_tests.append(ui_test)
    return stable_tests
