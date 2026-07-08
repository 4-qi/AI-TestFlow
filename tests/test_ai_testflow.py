from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from ai_testflow.agent.llm_client import LlmJsonParseError, LlmSettings, OpenAILlmClient, _unwrap_named_object, load_env_file
from ai_testflow.agent.agents.script_agent import run_script_agent
from ai_testflow.agent.orchestrator import _filter_defects_to_failed_tests
from ai_testflow.agent_designer import design_requirements_from_prd, design_test_cases_from_requirements
from ai_testflow.analyzer import analyze_prd, build_requirements, extract_requirement_rows, extract_test_case_rows
from ai_testflow.cli import _print_agent_summary
from ai_testflow.config import load_config
from ai_testflow.inspector import KNOWN_DEFECTS, run_inspection
from ai_testflow.pytest_runner import parse_pytest_result
from ai_testflow.test_generator import render_generated_api_tests, render_generated_playwright_tests


def test_load_config_reads_exact_paths():
    config = load_config("ai-testflow.yml")

    assert config.project_name == "AI-TestFlow"
    assert str(config.prd_path) == "docs/prd.md"
    assert str(config.output_dir) == "ai-testflow-runs/latest"
    assert str(config.generated_tests_path) == "ai-testflow-runs/latest/generated_api_tests.py"
    assert str(config.generated_playwright_tests_path) == "frontend/generated-tests/generated_playwright_tests.spec.js"
    assert config.llm_provider == "deepseek"
    assert config.llm_model == "deepseek-v4-pro"
    assert config.llm_api_key_env == "DEEPSEEK_API_KEY"
    assert config.llm_base_url == "https://api.deepseek.com"
    assert config.api_test_runtime == {"mode": "flask_app", "app_factory": "backend.app:create_app"}
    assert config.playwright_command == [
        "bash",
        "-lc",
        "cd frontend && npm exec playwright test generated-tests/generated_playwright_tests.spec.js --config playwright.config.js",
    ]
    assert config.pytest_command == [
        "conda",
        "run",
        "-n",
        "AI-TestFlow",
        "python",
        "-m",
        "pytest",
        "-q",
        "backend/tests",
    ]
    assert config.generated_pytest_command == [
        "conda",
        "run",
        "-n",
        "AI-TestFlow",
        "python",
        "-m",
        "pytest",
        "-q",
        "ai-testflow-runs/latest/generated_api_tests.py",
    ]


def test_llm_client_requires_api_key(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is required for agent-run"):
        OpenAILlmClient(LlmSettings(provider="openai", model="gpt-4.1-mini", api_key_env="OPENAI_API_KEY"))


def test_deepseek_llm_client_requires_api_key(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY is required for agent-run"):
        OpenAILlmClient(
            LlmSettings(
                provider="deepseek",
                model="deepseek-v4-pro",
                api_key_env="DEEPSEEK_API_KEY",
                base_url="https://api.deepseek.com",
            )
        )


def test_load_env_file_sets_missing_api_key(monkeypatch, tmp_path):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    env_path = tmp_path / ".env"
    env_path.write_text("DEEPSEEK_API_KEY=local-test-key\n", encoding="utf-8")

    load_env_file(env_path)

    assert os.environ["DEEPSEEK_API_KEY"] == "local-test-key"


def test_llm_json_unwraps_named_object():
    data = {
        "prd_analysis": {
            "business_goal": "验证登录注册 Demo",
            "user_roles": ["未登录用户"],
            "functional_requirements": [],
            "non_functional_requirements": [],
            "interface_scope": [],
        }
    }

    assert _unwrap_named_object("prd_analysis", data) == data["prd_analysis"]


def test_llm_json_parse_error_saves_raw_output(tmp_path):
    client = OpenAILlmClient.__new__(OpenAILlmClient)
    client._raw_output_dir = tmp_path

    with pytest.raises(LlmJsonParseError, match="test_case_design returned invalid JSON"):
        client._parse_json_response("test_case_design", '{"test_cases": [}')

    raw_path = tmp_path / "llm-raw-test_case_design.txt"
    assert raw_path.read_text(encoding="utf-8") == '{"test_cases": [}'


def test_agent_summary_prints_readable_failed_tests_and_defects(capsys):
    _print_agent_summary(
        {
            "status": "defects_found",
            "requirements_count": 14,
            "test_points_count": 15,
            "test_cases_count": 16,
            "pytest_exit_code": 1,
            "playwright_exit_code": 0,
            "passed_tests": 9,
            "failed_tests": 1,
            "failed_test_names": ["test_generated_register_short_username_rule"],
            "playwright_passed_tests": 4,
            "playwright_failed_tests": 0,
            "playwright_failed_test_names": [],
            "defects": [
                {
                    "bug_id": "BUG-AUTO-001",
                    "requirement_id": "REQ-003",
                    "test_case_id": "TC-005",
                    "failed_test_name": "test_generated_register_short_username_rule",
                }
            ],
        },
        Path("ai-testflow-runs/latest"),
    )

    output = capsys.readouterr().out

    assert "AI-TestFlow Result" in output
    assert "- Status: defects_found" in output
    assert "- Pytest exit code: 1" in output
    assert "- Playwright exit code: 0" in output
    assert "- Failed test names:" in output
    assert "  - test_generated_register_short_username_rule" in output
    assert (
        "  - BUG-AUTO-001 | requirement=REQ-003 | test_case=TC-005 "
        "| failed_test=test_generated_register_short_username_rule"
    ) in output


def test_parse_pytest_result_extracts_failed_test_mapping():
    output = """
.....F......                                                             [100%]
FAILED backend/tests/test_api.py::test_register_rejects_short_username_by_requirement
1 failed, 11 passed in 0.78s
"""

    result = parse_pytest_result(["pytest"], 1, output, "", output)

    assert result.passed_tests == 11
    assert result.failed_tests == 1
    assert result.failed_test_names == ["test_register_rejects_short_username_by_requirement"]


def test_parse_playwright_result_extracts_failed_test_titles():
    output = """
  1) generated-tests/generated_playwright_tests.spec.js:377:3 › 验证注册页面包含所有必要元素 ─────────
  2) generated-tests/generated_playwright_tests.spec.js:377:3 › 用户名为空提交时显示错误提示 ─────────
    generated-tests/generated_playwright_tests.spec.js:377:3 › 验证注册页面包含所有必要元素 ─────────
    generated-tests/generated_playwright_tests.spec.js:377:3 › 用户名为空提交时显示错误提示 ─────────
  2 failed
"""

    result = parse_pytest_result(["playwright"], 1, output, "", output)

    assert result.failed_tests == 2
    assert result.failed_test_names == ["验证注册页面包含所有必要元素", "用户名为空提交时显示错误提示"]


def test_analyze_prd_extracts_requirements_and_interfaces():
    prd_text = """
### PRD-FR-003 用户名长度限制

用户注册时，用户名长度必须大于等于 6 位。

### PRD-NFR-001 响应时间

接口响应时间应满足 Demo 验证需要。

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/register` | POST | 注册用户 |
"""

    analysis = analyze_prd(prd_text)

    assert analysis["functional_requirements"] == [
        {
            "requirement_id": "PRD-FR-003",
            "title": "用户名长度限制",
            "description": "用户注册时，用户名长度必须大于等于 6 位。",
        }
    ]
    assert analysis["non_functional_requirements"] == [
        {
            "requirement_id": "PRD-NFR-001",
            "title": "响应时间",
            "description": "接口响应时间应满足 Demo 验证需要。",
        }
    ]
    assert analysis["interfaces"] == [{"path": "/api/register", "method": "POST", "description": "注册用户"}]


def test_requirement_breakdown_merges_prd_and_spec_rows():
    prd_analysis = {
        "functional_requirements": [
            {
                "requirement_id": "PRD-FR-003",
                "title": "用户名长度限制",
                "description": "用户注册时，用户名长度必须大于等于 6 位。",
            }
        ],
        "non_functional_requirements": [],
        "interfaces": [],
    }
    requirement_spec = """
| 需求编号 | 所属模块 | 需求描述 | 测试重点 |
| --- | --- | --- | --- |
| PRD-FR-003 | MOD-001 | 用户名长度必须大于等于 6 位 | 小于 6 位用户名注册失败 |
"""

    requirement_rows = extract_requirement_rows(requirement_spec)
    requirements = build_requirements(prd_analysis, requirement_rows)

    assert requirement_rows == [
        {
            "requirement_id": "PRD-FR-003",
            "module_id": "MOD-001",
            "description": "用户名长度必须大于等于 6 位",
            "test_focus": "小于 6 位用户名注册失败",
        }
    ]
    assert requirements == [
        {
            "requirement_id": "PRD-FR-003",
            "title": "用户名长度限制",
            "description": "用户注册时，用户名长度必须大于等于 6 位。",
            "module_id": "MOD-001",
            "test_focus": "小于 6 位用户名注册失败",
            "source": "docs/prd.md",
        }
    ]


def test_agent_designs_requirements_and_test_cases_from_prd_analysis():
    prd_analysis = {
        "functional_requirements": [
            {
                "requirement_id": "PRD-FR-003",
                "title": "用户名长度限制",
                "description": "用户注册时，用户名长度必须大于等于 6 位。",
            },
            {
                "requirement_id": "PRD-FR-011",
                "title": "登录成功",
                "description": "用户输入已注册用户名和正确密码时，系统应允许用户登录并进入首页。",
            },
        ],
        "non_functional_requirements": [],
        "interfaces": [],
    }

    requirements = design_requirements_from_prd(prd_analysis)
    test_cases = design_test_cases_from_requirements(requirements)

    assert requirements == [
        {
            "requirement_id": "PRD-FR-003",
            "title": "用户名长度限制",
            "description": "用户注册时，用户名长度必须大于等于 6 位。",
            "module_id": "MOD-001",
            "test_focus": "小于 6 位用户名注册失败",
            "source": "docs/prd.md",
            "generated_by": "ai_testflow_agent",
        },
        {
            "requirement_id": "PRD-FR-011",
            "title": "登录成功",
            "description": "用户输入已注册用户名和正确密码时，系统应允许用户登录并进入首页。",
            "module_id": "MOD-002",
            "test_focus": "正确账号密码登录成功",
            "source": "docs/prd.md",
            "generated_by": "ai_testflow_agent",
        },
    ]
    assert [item["test_case_id"] for item in test_cases] == ["TC-REG-003", "TC-LOGIN-001"]


def test_generated_api_tests_render_generic_api_actions():
    api_tests = [
        {
            "test_case_id": "TC-003",
            "name": "用户名长度小于6时注册失败",
            "setup_api_actions": [],
            "method": "POST",
            "path": "/api/register",
            "json_body": {
                "username": "abc",
                "password": "Password123",
                "confirm_password": "Password123",
            },
            "expected_status": 400,
            "expected_json_contains": {
                "success": False,
                "message": "用户名长度不能少于6位",
            },
        }
    ]

    generated_script = render_generated_api_tests(api_tests)

    assert "def test_generated_" in generated_script
    assert "'method': 'POST'" in generated_script
    assert "'setup_api_actions': []" in generated_script
    assert "'path': '/api/register'" in generated_script
    assert "'username': 'abc'" in generated_script
    assert 'importlib.import_module("backend.app")' in generated_script
    assert 'assert response.status_code == case["expected_status"]' in generated_script
    assert "_assert_json_contains(body, case[\"expected_json_contains\"])" in generated_script


def test_generated_playwright_tests_render_generic_ui_actions():
    ui_tests = [
        {
            "test_case_id": "TC-UI-001",
            "title": "短用户名注册页面提示",
            "actions": [
                {"action": "goto", "url": "/register"},
                {"action": "fill_label", "label": "用户名", "value": "abc"},
                {"action": "click_role", "role": "button", "name": "注册"},
                {"action": "expect_text", "text": "用户名长度不能少于6位"},
            ],
        }
    ]

    generated_script = render_generated_playwright_tests(ui_tests)

    assert "from '@playwright/test'" in generated_script
    assert "const cases =" in generated_script
    assert "fill_label" in generated_script
    assert "expect_text" in generated_script
    assert "async function fillByLabel" in generated_script
    assert "async function clickByRole" in generated_script
    assert "async function expectText" in generated_script
    assert "page.getByLabel(label).first().fill(value)" in generated_script
    assert "page.locator('button').filter({ hasText: name })" in generated_script
    assert "page.getByText(text).first()" in generated_script


def test_script_agent_uses_structured_plan_to_generate_scripts(tmp_path):
    class FakeClient:
        def generate_json(self, **kwargs):
            assert kwargs["name"] == "script_plan"
            return {
                "api_tests": [
                    {
                        "test_case_id": "TC-REG-003",
                        "name": "用户名长度小于6时注册失败",
                        "setup_api_actions": [],
                        "method": "POST",
                        "path": "/api/register",
                        "json_body": {
                            "username": "abc",
                            "password": "Password123",
                            "confirm_password": "Password123",
                        },
                        "expected_status": 400,
                        "expected_json_contains": {
                            "success": False,
                            "message": "用户名长度不能少于6位",
                        },
                    }
                ],
                "ui_tests": [
                    {
                        "test_case_id": "TC-REG-003",
                        "title": "注册页短用户名校验",
                        "actions": [
                            {"action": "goto", "url": "/register"},
                            {"action": "fill_label", "label": "用户名", "value": "abc"},
                            {"action": "expect_text", "text": "用户名长度不能少于6位"},
                        ],
                    }
                ],
            }

    test_cases = [
        {
            "test_case_id": "TC-REG-003",
            "requirement_id": "PRD-FR-003",
            "test_point_id": "TP-REG-003",
            "title": "用户名长度小于 6 位注册失败",
            "precondition": "用户名未存在",
            "steps": ["输入 username=abc", "提交注册"],
            "test_data": "username=abc",
            "expected_result": "注册失败，提示用户名长度不能少于6位",
            "priority": "P0",
            "automation_type": "api_and_ui",
        }
    ]
    api_target = tmp_path / "generated_api_tests.py"
    playwright_target = tmp_path / "generated_playwright_tests.spec.js"

    result = run_script_agent(
        FakeClient(),
        "prompt",
        test_cases,
        "backend source",
        {"mode": "flask_app", "app_factory": "backend.app:create_app"},
        api_target,
        playwright_target,
    )

    assert result["script_plan"]["api_tests"][0]["test_case_id"] == "TC-REG-003"
    assert "'path': '/api/register'" in api_target.read_text(encoding="utf-8")
    playwright_text = playwright_target.read_text(encoding="utf-8")
    assert "const cases =" in playwright_text
    assert "fill_label" in playwright_text


def test_script_agent_uses_review_agent_when_configured(tmp_path):
    class FakeClient:
        def __init__(self):
            self.calls = []

        def generate_json(self, **kwargs):
            self.calls.append(kwargs["system_prompt"])
            if len(self.calls) == 1:
                return {
                    "api_tests": [
                        {
                            "test_case_id": "TC-001",
                            "name": "initial plan",
                            "setup_api_actions": [],
                            "method": "GET",
                            "path": "/api/initial",
                            "json_body": {},
                            "expected_status": 200,
                            "expected_json_contains": {},
                        }
                    ],
                    "ui_tests": [],
                }
            return {
                "api_tests": [
                    {
                        "test_case_id": "TC-001",
                        "name": "reviewed plan",
                        "setup_api_actions": [],
                        "method": "GET",
                        "path": "/api/reviewed",
                        "json_body": {},
                        "expected_status": 200,
                        "expected_json_contains": {},
                    }
                ],
                "ui_tests": [],
            }

    api_target = tmp_path / "generated_api_tests.py"
    playwright_target = tmp_path / "generated_playwright_tests.spec.js"
    client = FakeClient()

    result = run_script_agent(
        client,
        "script prompt",
        [{"test_case_id": "TC-001"}],
        "backend source",
        {"mode": "flask_app", "app_factory": "backend.app:create_app"},
        api_target,
        playwright_target,
        prd_text="prd",
        review_prompt="review prompt",
    )

    assert client.calls == ["script prompt", "review prompt"]
    assert result["script_plan"]["api_tests"][0]["path"] == "/api/reviewed"
    assert "'path': '/api/reviewed'" in api_target.read_text(encoding="utf-8")


def test_generated_api_tests_run_setup_actions(tmp_path):
    api_tests = [
        {
            "test_case_id": "TC-LOGIN-001",
            "name": "正确用户名密码登录成功",
            "setup_api_actions": [
                {
                    "method": "POST",
                    "path": "/api/register",
                    "json_body": {
                        "username": "setupuser",
                        "password": "Password123",
                        "confirm_password": "Password123",
                    },
                    "expected_status": 200,
                }
            ],
            "method": "POST",
            "path": "/api/login",
            "json_body": {
                "username": "setupuser",
                "password": "Password123",
            },
            "expected_status": 200,
            "expected_json_contains": {
                "message": "登录成功",
            },
        }
    ]
    generated_path = tmp_path / "generated_api_tests.py"
    generated_path.write_text(render_generated_api_tests(api_tests), encoding="utf-8")

    script = generated_path.read_text(encoding="utf-8")

    assert "for setup_action in case[\"setup_api_actions\"]" in script
    assert "'username': 'setupuser'" in script


def test_defect_filter_keeps_only_real_failed_tests():
    pytest_result = parse_pytest_result(
        ["pytest"],
        1,
        (
            "FAILED generated_api_tests.py::test_generated_tc_004__6_abc\n"
            "1 failed, 14 passed"
        ),
        "",
        (
            "FAILED generated_api_tests.py::test_generated_tc_004__6_abc\n"
            "1 failed, 14 passed"
        ),
    )
    defect_analysis = {
        "status": "has_defects",
        "defects": [
            {
                "bug_id": "BUG-001",
                "title": "短用户名注册成功",
                "requirement_id": "PRD-FR-003",
                "test_case_id": "TC-004",
                "failed_test_name": "test_generated_tc_004__6_abc",
                "expected": "HTTP 400",
                "actual": "HTTP 200",
                "severity": "高",
                "priority": "高",
                "reproduction_steps": ["POST /api/register"],
            },
            {
                "bug_id": "BUG-002",
                "title": "未失败测试不应进入 Bug",
                "requirement_id": "PRD-FR-010",
                "test_case_id": "TC-025",
                "failed_test_name": "test_generated_tc_025",
                "expected": "HTTP 401",
                "actual": "HTTP 401",
                "severity": "中",
                "priority": "中",
                "reproduction_steps": ["POST /api/login"],
            },
        ],
    }

    result = _filter_defects_to_failed_tests(defect_analysis, pytest_result)

    assert result["status"] == "has_defects"
    assert [item["bug_id"] for item in result["defects"]] == ["BUG-001"]


def test_known_defect_maps_short_username_failure_to_bug():
    defect = KNOWN_DEFECTS[0]

    assert defect["requirement_id"] == "PRD-FR-003"
    assert defect["rule_id"] == "REG-002"
    assert defect["acceptance_id"] == "AC-003"
    assert defect["test_case_id"] == "TC-REG-003"
    assert defect["bug_id"] == "BUG-001"


def test_run_inspection_writes_stable_summary(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for path in [
        "docs/prd.md",
        "docs/samples/requirement-spec.sample.md",
        "docs/samples/test-cases.sample.md",
        "backend/app.py",
        "backend/tests/test_api.py",
        "docs/api-test-execution.md",
        "docs/samples/test-report.sample.md",
        "docs/samples/bug-report.sample.md",
    ]:
        file_path = tmp_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if path == "docs/samples/requirement-spec.sample.md":
            file_path.write_text(
                "| 需求编号 | 所属模块 | 需求描述 | 测试重点 |\n"
                "| --- | --- | --- | --- |\n"
                "| PRD-FR-003 | MOD-001 | 用户名长度必须大于等于 6 位 | 小于 6 位用户名注册失败 |\n",
                encoding="utf-8",
            )
        elif path == "docs/samples/test-cases.sample.md":
            file_path.write_text(
                "| 用例编号 | 关联需求 | 标题 | 前置条件 | 测试数据 | 期望结果 | 优先级 |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| TC-REG-003 | PRD-FR-003 | 用户名长度小于 6 位注册失败 | 用户名未存在 | `username=abc` | 注册失败，提示 `用户名长度不能少于6位` | P0 |\n",
                encoding="utf-8",
            )
        elif path == "docs/prd.md":
            file_path.write_text(
                "### PRD-FR-003 用户名长度限制\n\n"
                "用户注册时，用户名长度必须大于等于 6 位。\n",
                encoding="utf-8",
            )
        else:
            file_path.write_text(path, encoding="utf-8")

    config_text = """project_name: AI-TestFlow
llm:
  provider: deepseek
  model: deepseek-v4-pro
  api_key_env: DEEPSEEK_API_KEY
  base_url: https://api.deepseek.com
prd_path: docs/prd.md
requirement_spec_path: docs/samples/requirement-spec.sample.md
test_cases_path: docs/samples/test-cases.sample.md
backend_source_path: backend/app.py
pytest_path: backend/tests
pytest_command:
  - python
  - -c
  - import sys; print('FAILED backend/tests/test_api.py::test_register_rejects_short_username_by_requirement'); print('1 failed, 11 passed in 0.78s'); sys.exit(1)
generated_tests_path: ai-testflow-runs/latest/generated_api_tests.py
generated_pytest_command:
  - python
  - -c
  - import sys; print('FAILED ai-testflow-runs/latest/generated_api_tests.py::test_generated_register_rejects_short_username'); print('1 failed, 11 passed in 0.78s'); sys.exit(1)
generated_playwright_tests_path: ai-testflow-runs/latest/generated_playwright_tests.spec.js
api_execution_report_path: docs/api-test-execution.md
test_report_path: docs/samples/test-report.sample.md
bug_report_path: docs/samples/bug-report.sample.md
output_dir: ai-testflow-runs/latest
"""
    (tmp_path / "ai-testflow.yml").write_text(config_text, encoding="utf-8")

    config = load_config("ai-testflow.yml")
    result = run_inspection(config, tmp_path)
    summary = json.loads((tmp_path / "ai-testflow-runs/latest/inspection-summary.json").read_text(encoding="utf-8"))

    assert result.summary["status"] == "defects_found"
    assert summary["failed_tests"] == 1
    assert summary["passed_tests"] == 11
    assert summary["requirements_count"] == 1
    assert summary["test_cases_count"] == 1
    assert summary["bug_id"] == "BUG-001"
    assert summary["defects"][0]["bug_id"] == "BUG-001"
    assert summary["defects"][0]["failed_test_name"] == "test_generated_register_rejects_short_username"
    assert (tmp_path / "ai-testflow-runs/latest/pytest-output.txt").exists()
    assert (tmp_path / "ai-testflow-runs/latest/prd-analysis.json").exists()
    assert (tmp_path / "ai-testflow-runs/latest/requirements.json").exists()
    assert (tmp_path / "ai-testflow-runs/latest/generated-test-cases.md").exists()
    assert (tmp_path / "ai-testflow-runs/latest/generated_api_tests.py").exists()
