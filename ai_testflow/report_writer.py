from __future__ import annotations

from typing import Any

from .pytest_runner import PytestResult


def build_test_report(summary: dict[str, Any], traceability: dict[str, Any], pytest_result: PytestResult) -> str:
    failed_names = ", ".join(pytest_result.failed_test_names) if pytest_result.failed_test_names else "无"
    defects = traceability["defects"]
    defect_lines = "\n".join(
        f"| `{defect['bug_id']}` | `{defect['requirement_id']}` | `{defect['test_case_id']}` | `{defect['failed_test_name']}` | {defect['title']} |"
        for defect in defects
    )
    if not defect_lines:
        defect_lines = "| 无 | 无 | 无 | 无 | 无 |"
    stage_lines = "\n".join(
        f"| {stage['stage']} | {stage['status']} | `{stage['output']}` |"
        for stage in summary["workflow_stages"]
    )
    return f"""# AI-TestFlow CLI 检验报告

## 1. 执行结论

本轮 CLI 插件检验状态：`{summary["status"]}`。

登录注册 Demo 主流程测试中通过 `{summary["passed_tests"]}` 条，失败 `{summary["failed_tests"]}` 条。失败用例为 `{failed_names}`。

## 2. 一站式流程阶段

| 阶段 | 状态 | 输出 |
| --- | --- | --- |
{stage_lines}

## 3. pytest 摘要

| 项目 | 内容 |
| --- | --- |
| 命令 | `{" ".join(pytest_result.command)}` |
| exit code | `{pytest_result.exit_code}` |
| passed | `{pytest_result.passed_tests}` |
| failed | `{pytest_result.failed_tests}` |
| 失败用例 | `{failed_names}` |

## 4. 缺陷列表

| Bug | 关联需求 | 关联用例 | 失败测试 | 标题 |
| --- | --- | --- | --- | --- |
{defect_lines}
"""


def build_bug_report(summary: dict[str, Any], traceability: dict[str, Any], pytest_result: PytestResult) -> str:
    failed_names = ", ".join(pytest_result.failed_test_names) if pytest_result.failed_test_names else "无"
    defects = traceability["defects"]
    if not defects:
        return """# AI-TestFlow Bug 单

本轮检验未发现需要自动提交的 Bug。
"""
    defect_sections = []
    for defect in defects:
        defect_sections.append(
            f"""# {defect["bug_id"]} {defect["title"]}

| 字段 | 内容 |
| --- | --- |
| Bug 编号 | `{defect["bug_id"]}` |
| 关联需求 | `{defect["requirement_id"]}` |
| 关联规则 | `{defect["rule_id"]}` |
| 关联验收标准 | `{defect["acceptance_id"]}` |
| 关联测试用例 | `{defect["test_case_id"]}` |
| 自动化失败用例 | `{defect["failed_test_name"]}` |
| pytest exit code | `{pytest_result.exit_code}` |

## 1. 期望结果

{defect["expected"]}。

## 2. 实际结果

{defect["actual"]}。

## 3. CLI 检验结论

`python -m ai_testflow run` 已完成执行，插件本身执行成功，并发现 `{defect["bug_id"]}`。该缺陷来自真实自动化测试失败，不是测试脚本通过后人工标记的问题。
"""
        )
    return "\n".join(defect_sections)


def build_generated_test_cases(test_cases: list[dict[str, str]]) -> str:
    rows = "\n".join(
        f"| `{case['test_case_id']}` | `{case['requirement_id']}` | {case['title']} | {case['expected_result']} | {case['priority']} |"
        for case in test_cases
    )
    return f"""# AI-TestFlow 生成测试用例清单

该文件由 CLI 从 `docs/test-cases.md` 结构化生成，用于模拟一站式插件的“测试用例设计”阶段产物。

| 用例编号 | 关联需求 | 标题 | 期望结果 | 优先级 |
| --- | --- | --- | --- | --- |
{rows}
"""
