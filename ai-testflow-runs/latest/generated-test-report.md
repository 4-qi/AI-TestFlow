# AI-TestFlow CLI 检验报告

## 1. 执行结论

本轮 CLI 插件检验状态：`defects_found`。

登录注册 Demo 主流程测试中通过 `11` 条，失败 `1` 条。失败用例为 `test_generated_register_rejects_short_username`。

## 2. 一站式流程阶段

| 阶段 | 状态 | 输出 |
| --- | --- | --- |
| PRD分析 | completed | `需求原文已读取` |
| 需求拆解 | completed | `14` |
| 测试用例设计 | completed | `12` |
| 自动化测试脚本生成 | completed | `generated_api_tests.py` |
| 用例执行 | completed | `12` |
| 测试报告生成 | completed | `generated-test-report.md` |
| 自动提Bug | completed | `1` |

## 3. pytest 摘要

| 项目 | 内容 |
| --- | --- |
| 命令 | `conda run -n AI-TestFlow python -m pytest -q ai-testflow-runs/latest/generated_api_tests.py` |
| exit code | `1` |
| passed | `11` |
| failed | `1` |
| 失败用例 | `test_generated_register_rejects_short_username` |

## 4. 缺陷列表

| Bug | 关联需求 | 关联用例 | 失败测试 | 标题 |
| --- | --- | --- | --- | --- |
| `BUG-001` | `PRD-FR-003` | `TC-REG-003` | `test_generated_register_rejects_short_username` | 注册接口未校验用户名长度，短用户名可注册成功 |
