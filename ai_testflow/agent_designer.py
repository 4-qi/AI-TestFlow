from __future__ import annotations

from typing import Any


MODULE_BY_REQUIREMENT_ID = {
    "PRD-FR-001": "MOD-001",
    "PRD-FR-002": "MOD-001",
    "PRD-FR-003": "MOD-001",
    "PRD-FR-004": "MOD-001",
    "PRD-FR-005": "MOD-001",
    "PRD-FR-006": "MOD-001",
    "PRD-FR-007": "MOD-001",
    "PRD-FR-008": "MOD-002",
    "PRD-FR-009": "MOD-002",
    "PRD-FR-010": "MOD-002",
    "PRD-FR-011": "MOD-002",
    "PRD-FR-012": "MOD-002",
    "PRD-FR-013": "MOD-003",
    "PRD-FR-014": "MOD-003",
}


TEST_FOCUS_BY_REQUIREMENT_ID = {
    "PRD-FR-001": "注册页面元素完整性",
    "PRD-FR-002": "空用户名注册失败",
    "PRD-FR-003": "小于 6 位用户名注册失败",
    "PRD-FR-004": "空密码注册失败",
    "PRD-FR-005": "两次密码不一致注册失败",
    "PRD-FR-006": "重复用户名注册失败",
    "PRD-FR-007": "合法输入注册成功",
    "PRD-FR-008": "登录页面元素完整性",
    "PRD-FR-009": "未注册用户登录失败",
    "PRD-FR-010": "密码错误登录失败",
    "PRD-FR-011": "正确账号密码登录成功",
    "PRD-FR-012": "错误信息可读",
    "PRD-FR-013": "登录态展示",
    "PRD-FR-014": "登录态清除",
}


TEST_CASE_DESIGNS = [
    {
        "test_case_id": "TC-REG-001",
        "requirement_id": "PRD-FR-007",
        "title": "合法用户注册成功",
        "precondition": "用户名未存在",
        "test_data": "`username=testuser`, `password=Password123`, `confirm_password=Password123`",
        "expected_result": "注册成功，返回用户名 `testuser`",
        "priority": "P0",
    },
    {
        "test_case_id": "TC-REG-002",
        "requirement_id": "PRD-FR-002",
        "title": "用户名为空注册失败",
        "precondition": "无",
        "test_data": "`username=`, `password=Password123`, `confirm_password=Password123`",
        "expected_result": "注册失败，提示 `用户名不能为空`",
        "priority": "P0",
    },
    {
        "test_case_id": "TC-REG-003",
        "requirement_id": "PRD-FR-003",
        "title": "用户名长度小于 6 位注册失败",
        "precondition": "用户名未存在",
        "test_data": "`username=abc`, `password=Password123`, `confirm_password=Password123`",
        "expected_result": "注册失败，提示 `用户名长度不能少于6位`",
        "priority": "P0",
    },
    {
        "test_case_id": "TC-REG-004",
        "requirement_id": "PRD-FR-004",
        "title": "密码为空注册失败",
        "precondition": "无",
        "test_data": "`username=testuser`, `password=`, `confirm_password=`",
        "expected_result": "注册失败，提示 `密码不能为空`",
        "priority": "P0",
    },
    {
        "test_case_id": "TC-REG-005",
        "requirement_id": "PRD-FR-005",
        "title": "确认密码不一致注册失败",
        "precondition": "无",
        "test_data": "`username=testuser`, `password=Password123`, `confirm_password=Password456`",
        "expected_result": "注册失败，提示 `两次输入的密码不一致`",
        "priority": "P0",
    },
    {
        "test_case_id": "TC-REG-006",
        "requirement_id": "PRD-FR-006",
        "title": "重复用户名注册失败",
        "precondition": "`testuser` 已注册",
        "test_data": "`username=testuser`, `password=Password123`, `confirm_password=Password123`",
        "expected_result": "注册失败，提示 `用户名已存在`",
        "priority": "P0",
    },
    {
        "test_case_id": "TC-LOGIN-001",
        "requirement_id": "PRD-FR-011",
        "title": "正确账号密码登录成功",
        "precondition": "`testuser` 已注册",
        "test_data": "`username=testuser`, `password=Password123`",
        "expected_result": "登录成功，返回用户名 `testuser`",
        "priority": "P0",
    },
    {
        "test_case_id": "TC-LOGIN-002",
        "requirement_id": "PRD-FR-010",
        "title": "密码错误登录失败",
        "precondition": "`testuser` 已注册",
        "test_data": "`username=testuser`, `password=WrongPassword`",
        "expected_result": "登录失败，提示 `用户名或密码错误`",
        "priority": "P0",
    },
    {
        "test_case_id": "TC-LOGIN-003",
        "requirement_id": "PRD-FR-009",
        "title": "未注册用户登录失败",
        "precondition": "用户名未注册",
        "test_data": "`username=missinguser`, `password=Password123`",
        "expected_result": "登录失败，提示 `用户名或密码错误`",
        "priority": "P0",
    },
    {
        "test_case_id": "TC-ME-001",
        "requirement_id": "PRD-FR-013",
        "title": "未登录访问当前用户失败",
        "precondition": "未登录",
        "test_data": "无",
        "expected_result": "获取失败，提示 `用户未登录`",
        "priority": "P1",
    },
    {
        "test_case_id": "TC-ME-002",
        "requirement_id": "PRD-FR-013",
        "title": "登录后获取当前用户成功",
        "precondition": "`testuser` 已登录",
        "test_data": "无",
        "expected_result": "获取成功，返回用户名 `testuser`",
        "priority": "P1",
    },
    {
        "test_case_id": "TC-LOGOUT-001",
        "requirement_id": "PRD-FR-014",
        "title": "退出登录后清除登录态",
        "precondition": "`testuser` 已登录",
        "test_data": "无",
        "expected_result": "退出成功，再访问当前用户接口提示 `用户未登录`",
        "priority": "P1",
    },
]


def design_requirements_from_prd(prd_analysis: dict[str, Any]) -> list[dict[str, str]]:
    requirements: list[dict[str, str]] = []
    for item in prd_analysis["functional_requirements"]:
        requirement_id = item["requirement_id"]
        requirements.append(
            {
                "requirement_id": requirement_id,
                "title": item["title"],
                "description": item["description"],
                "module_id": MODULE_BY_REQUIREMENT_ID.get(requirement_id, ""),
                "test_focus": TEST_FOCUS_BY_REQUIREMENT_ID.get(requirement_id, ""),
                "source": "docs/prd.md",
                "generated_by": "ai_testflow_agent",
            }
        )
    return requirements


def design_test_cases_from_requirements(requirements: list[dict[str, str]]) -> list[dict[str, str]]:
    requirement_ids = {item["requirement_id"] for item in requirements}
    return [dict(item) for item in TEST_CASE_DESIGNS if item["requirement_id"] in requirement_ids]
