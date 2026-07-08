# AI-TestFlow 多角色测试工程师 Agent 设计

## 1. 目标

AI-TestFlow Agent 的目标是提供一个即插即用的测试工程师角色，从 PRD 开始完成测试全流程。

```text
PRD -> 需求拆解 -> 测试点 -> 测试用例 -> 自动化脚本 -> 执行 -> 分析 -> 报告 -> Bug
```

Demo 系统只作为被测对象，真正项目价值在 AI Testing Workflow。

## 2. 多 Agent 分工

| Agent | 输入 | 输出 |
| --- | --- | --- |
| PRD Agent | `docs/prd.md` | `prd-analysis.json` |
| Requirement Agent | PRD 分析结果 | `requirements.json`、`test-points.json` |
| Test Case Agent | 测试点 | `test-cases.json` |
| Script Agent | 测试用例 | `script-plan.json`、`generated_api_tests.py`、`generated_playwright_tests.spec.js` |
| Execute Agent | 自动化脚本 | `execution-result.json`、测试日志 |
| Analysis Agent | 需求、用例、日志 | `defect-analysis.json` |
| Report Agent | 全部上游产物 | `generated-test-report.md` |
| Bug Agent | 缺陷分析 | `generated-bug-report.md` |

## 3. 主入口

```bash
conda run -n AI-TestFlow python -m ai_testflow agent-run
```

必须配置：

```bash
export OPENAI_API_KEY=你的 OpenAI API Key
```

没有 Key 时必须失败，不允许退回硬编码流程。

## 4. 输入和样例

主输入：

```text
docs/prd.md
backend/
frontend/
```

样例参考：

```text
docs/samples/
```

样例参考不参与 Agent 主流程。

## 5. 产物

```text
ai-testflow-runs/latest/workflow-state.json
ai-testflow-runs/latest/prd-analysis.json
ai-testflow-runs/latest/requirements.json
ai-testflow-runs/latest/test-points.json
ai-testflow-runs/latest/test-cases.json
ai-testflow-runs/latest/script-plan.json
ai-testflow-runs/latest/generated_api_tests.py
ai-testflow-runs/latest/generated_playwright_tests.spec.js
ai-testflow-runs/latest/pytest-output.txt
ai-testflow-runs/latest/playwright-output.txt
ai-testflow-runs/latest/execution-result.json
ai-testflow-runs/latest/defect-analysis.json
ai-testflow-runs/latest/generated-test-report.md
ai-testflow-runs/latest/generated-bug-report.md
```
