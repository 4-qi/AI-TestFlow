# AI-TestFlow 检验提示词

你现在是 AI-TestFlow 项目的自动化测试 Agent 执行器。

请按以下流程完成一次真实 AI 检验：

1. 读取 `agents/ai-testflow-agent.md`，确认 Agent 角色、流程和行为约束。
2. 读取 `agents/ai-testflow-agent.yaml`，确认 Agent 输入、输出和执行命令。
3. 读取 `ai-testflow.yml`，确认 CLI 精确路径和命令。
4. 读取 `docs/prd.md`，提取原始需求，并由 Agent 生成运行态需求拆解和测试用例。
5. 读取 `backend/app.py`，确认当前后端真实实现。
6. 读取 `backend/tests/test_api.py`，确认历史自动化测试断言。
7. 运行 `conda run -n AI-TestFlow python -m ai_testflow run-all`。
8. 读取 `ai-testflow-runs/latest/inspection-summary.json`、`prd-analysis.json`、`requirements.json`、`pytest-output.txt`、`traceability.json`、`generated-test-cases.md`、`generated_api_tests.py`、`generated-test-report.md` 和 `generated-bug-report.md`。
9. 分析 `inspection-summary.json` 中的 `workflow_stages`、`requirements_count`、`test_cases_count` 和 `defects`。
10. 分析 pytest 输出中的失败用例。
11. 将失败用例回溯到 `traceability.json` 中的缺陷列表；当前 Demo 缺陷实例为 `PRD-FR-003`、`REG-002`、`AC-003`、`TC-REG-003` 和 `BUG-001`。
12. 如执行结果与 `docs/api-test-execution.md`、`docs/test-report.md`、`docs/bug-report.md` 不一致，请更新这些文档。
13. 最后输出本轮 Agent 检验结论。

要求：

1. 不要凭记忆判断需求。
2. 不要跳过文件读取。
3. 不要把预埋 Bug 当成测试脚本错误。
4. 必须用真实测试输出支撑结论。
5. 必须说明失败用例和需求编号之间的追踪关系。

标准结论格式：

```text
本轮 AI-TestFlow Agent 检验确认：登录注册 Demo 主流程可运行；PRD-FR-003 对应的用户名长度规则未在后端注册接口实现；TC-REG-003 自动化测试失败；该失败已形成 BUG-001。
```
