from __future__ import annotations

import json

from ai_testflow.config import load_config
from ai_testflow.inspector import KNOWN_DEFECTS, run_inspection
from ai_testflow.pytest_runner import parse_pytest_result


def test_load_config_reads_exact_paths():
    config = load_config("ai-testflow.yml")

    assert config.project_name == "AI-TestFlow"
    assert str(config.prd_path) == "docs/prd.md"
    assert str(config.output_dir) == "ai-testflow-runs/latest"
    assert str(config.generated_tests_path) == "ai-testflow-runs/latest/generated_api_tests.py"
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
        "docs/requirement-spec.md",
        "docs/test-cases.md",
        "backend/app.py",
        "backend/tests/test_api.py",
        "docs/api-test-execution.md",
        "docs/test-report.md",
        "docs/bug-report.md",
    ]:
        file_path = tmp_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if path == "docs/requirement-spec.md":
            file_path.write_text(
                "| 需求编号 | 所属模块 | 需求描述 | 测试重点 |\n"
                "| --- | --- | --- | --- |\n"
                "| PRD-FR-003 | MOD-001 | 用户名长度必须大于等于 6 位 | 小于 6 位用户名注册失败 |\n",
                encoding="utf-8",
            )
        elif path == "docs/test-cases.md":
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
prd_path: docs/prd.md
requirement_spec_path: docs/requirement-spec.md
test_cases_path: docs/test-cases.md
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
api_execution_report_path: docs/api-test-execution.md
test_report_path: docs/test-report.md
bug_report_path: docs/bug-report.md
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
