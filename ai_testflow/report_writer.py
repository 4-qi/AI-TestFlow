from __future__ import annotations

from typing import Any

from .pytest_runner import PytestResult


def build_test_report(summary: dict[str, Any], traceability: dict[str, Any], pytest_result: PytestResult) -> str:
    failed_names = ", ".join(pytest_result.failed_test_names) if pytest_result.failed_test_names else "无"
    return f"""# AI-TestFlow CLI 检验报告

## 1. 执行结论

本轮 CLI 插件检验状态：`{summary["status"]}`。

登录注册 Demo 主流程测试中通过 `{summary["passed_tests"]}` 条，失败 `{summary["failed_tests"]}` 条。失败用例为 `{failed_names}`。

## 2. 需求追踪

```text
{traceability["requirement_id"]} -> {traceability["rule_id"]} -> {traceability["acceptance_id"]} -> {traceability["test_case_id"]} -> {traceability["bug_id"]}
```

## 3. pytest 摘要

| 项目 | 内容 |
| --- | --- |
| 命令 | `{" ".join(pytest_result.command)}` |
| exit code | `{pytest_result.exit_code}` |
| passed | `{pytest_result.passed_tests}` |
| failed | `{pytest_result.failed_tests}` |
| 失败用例 | `{failed_names}` |

## 4. 缺陷判断

按 `{traceability["requirement_id"]}` 和 `{traceability["rule_id"]}`，用户名长度小于 6 位时注册必须失败。当前自动化测试期望 `{traceability["expected"]}`，实际结果为 `{traceability["actual"]}`，因此形成 `{traceability["bug_id"]}`。
"""


def build_bug_report(summary: dict[str, Any], traceability: dict[str, Any], pytest_result: PytestResult) -> str:
    failed_names = ", ".join(pytest_result.failed_test_names) if pytest_result.failed_test_names else "无"
    return f"""# {traceability["bug_id"]} 注册接口未校验用户名长度

| 字段 | 内容 |
| --- | --- |
| Bug 编号 | `{traceability["bug_id"]}` |
| 关联需求 | `{traceability["requirement_id"]}` |
| 关联规则 | `{traceability["rule_id"]}` |
| 关联验收标准 | `{traceability["acceptance_id"]}` |
| 关联测试用例 | `{traceability["test_case_id"]}` |
| 自动化失败用例 | `{failed_names}` |
| pytest exit code | `{pytest_result.exit_code}` |

## 1. 期望结果

{traceability["expected"]}。

## 2. 实际结果

{traceability["actual"]}。

## 3. CLI 检验结论

`python -m ai_testflow run` 已完成执行，插件本身执行成功，并发现 `{traceability["bug_id"]}`。该缺陷来自真实自动化测试失败，不是测试脚本通过后人工标记的问题。
"""

