# AI-TestFlow 多角色测试工程师 Agent

## 1. 定位

AI-TestFlow Agent 是一个即插即用的测试工程师角色集合，负责从 PRD 开始完成自动化测试全流程。

Demo 系统只是被测对象：

```text
React + Flask 登录注册 Demo
```

真正有价值的是 AI Testing Workflow：

```text
PRD分析 -> 需求拆解 -> 测试用例设计 -> 脚本生成 -> 执行测试 -> 分析结果 -> 测试报告 -> Bug 单
```

## 2. Agent 拆分

| Agent | 作用 | 输入 | 输出 |
| --- | --- | --- | --- |
| PRD Agent | 提取业务规则 | `docs/prd.md` | `prd-analysis.json` |
| Requirement Agent | 拆测试点 | PRD 分析结果 | `requirements.json`、`test-points.json` |
| Test Case Agent | 写测试用例 | 测试点 | `test-cases.json` |
| Script Agent | 生成自动化脚本 | 测试用例 | `script-plan.json`、`generated_api_tests.py`、`generated_playwright_tests.spec.js` |
| Execute Agent | 执行测试 | 自动化脚本 | `execution-result.json`、测试日志 |
| Analysis Agent | 判断缺陷 | 需求、用例、日志 | `defect-analysis.json` |
| Report Agent | 汇总测试结果 | 全部上游产物 | `generated-test-report.md` |
| Bug Agent | 生成 Bug 单 | 缺陷分析 | `generated-bug-report.md` |

## 3. 主入口

```bash
conda run -n AI-TestFlow python -m ai_testflow agent-run
```

必须配置：

```bash
export DEEPSEEK_API_KEY=你的 DeepSeek API Key
```

无 Key 时必须失败，不允许退回硬编码规则。

## 4. 输入边界

主业务输入只有：

```text
docs/prd.md
```

被测实现输入：

```text
backend/
frontend/
```

样例参考：

```text
docs/samples/
```

样例参考不是 Agent 主流程输入。

## 5. 输出产物

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
