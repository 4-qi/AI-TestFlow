from __future__ import annotations

import json

import pytest

from ai_testflow.agent.llm_client import LlmSettings, OpenAILlmClient, _unwrap_named_object
from ai_testflow.agent.agents.script_agent import run_script_agent
from ai_testflow.agent_designer import design_requirements_from_prd, design_test_cases_from_requirements
from ai_testflow.analyzer import analyze_prd, build_requirements, extract_requirement_rows, extract_test_case_rows
from ai_testflow.config import load_config
from ai_testflow.inspector import KNOWN_DEFECTS, run_inspection
from ai_testflow.pytest_runner import parse_pytest_result
from ai_testflow.test_generator import render_generated_api_tests


def test_load_config_reads_exact_paths():
    config = load_config("ai-testflow.yml")

    assert config.project_name == "AI-TestFlow"
    assert str(config.prd_path) == "docs/prd.md"
    assert str(config.output_dir) == "ai-testflow-runs/latest"
    assert str(config.generated_tests_path) == "ai-testflow-runs/latest/generated_api_tests.py"
    assert str(config.generated_playwright_tests_path) == "ai-testflow-runs/latest/generated_playwright_tests.spec.js"
    assert config.llm_provider == "deepseek"
    assert config.llm_model == "deepseek-v4-flash"
    assert config.llm_api_key_env == "DEEPSEEK_API_KEY"
    assert config.llm_base_url == "https://api.deepseek.com"
    assert config.playwright_command == [
        "npm",
        "--prefix",
        "frontend",
        "exec",
        "playwright",
        "test",
        "../ai-testflow-runs/latest/generated_playwright_tests.spec.js",
        "--config",
        "playwright.config.js",
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


def test_llm_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is required for agent-run"):
        OpenAILlmClient(LlmSettings(provider="openai", model="gpt-4.1-mini", api_key_env="OPENAI_API_KEY"))


def test_deepseek_llm_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY is required for agent-run"):
        OpenAILlmClient(
            LlmSettings(
                provider="deepseek",
                model="deepseek-v4-flash",
                api_key_env="DEEPSEEK_API_KEY",
                base_url="https://api.deepseek.com",
            )
        )


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


def test_test_case_design_parses_rows_and_generates_api_test_script():
    test_cases_doc = """
| 用例编号 | 关联需求 | 标题 | 前置条件 | 测试数据 | 期望结果 | 优先级 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-REG-003 | PRD-FR-003 | 用户名长度小于 6 位注册失败 | 用户名未存在 | `username=abc` | 注册失败，提示 `用户名长度不能少于6位` | P0 |
"""

    test_cases = extract_test_case_rows(test_cases_doc)
    generated_script = render_generated_api_tests(test_cases)

    assert test_cases == [
        {
            "test_case_id": "TC-REG-003",
            "requirement_id": "PRD-FR-003",
            "title": "用户名长度小于 6 位注册失败",
            "precondition": "用户名未存在",
            "test_data": "`username=abc`",
            "expected_result": "注册失败，提示 `用户名长度不能少于6位`",
            "priority": "P0",
        }
    ]
    assert "def test_generated_register_rejects_short_username(client):" in generated_script
    assert '"username": "abc"' in generated_script
    assert "assert response.status_code == 400" in generated_script
    assert 'assert response.get_json()["message"] == "用户名长度不能少于6位"' in generated_script
    assert "def test_generated_register_success(client):" not in generated_script


def test_script_agent_uses_structured_plan_to_generate_scripts(tmp_path):
    class FakeClient:
        def generate_json(self, **kwargs):
            assert kwargs["name"] == "script_plan"
            return {
                "api_test_case_ids": ["TC-REG-003"],
                "playwright_flows": [
                    {
                        "flow_id": "PW-REG-001",
                        "title": "注册页短用户名校验",
                        "test_case_ids": ["TC-REG-003"],
                        "steps": ["打开注册页", "输入短用户名", "提交注册"],
                        "expected_result": "页面提示用户名长度不能少于6位",
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

    result = run_script_agent(FakeClient(), "prompt", test_cases, api_target, playwright_target)

    assert result["script_plan"]["api_test_case_ids"] == ["TC-REG-003"]
    assert "def test_generated_register_rejects_short_username(client):" in api_target.read_text(encoding="utf-8")
    assert "short username registration should be rejected" in playwright_target.read_text(encoding="utf-8")


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
  model: deepseek-v4-flash
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
