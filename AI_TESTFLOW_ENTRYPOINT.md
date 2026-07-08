# AI-TestFlow 真 Agent 检验入口

## 1. 定位

本项目的核心不是登录注册 Demo 本身，而是右侧 AI Testing Workflow。

```text
Demo 系统：React + Flask 登录注册，被测试对象
AI Testing Workflow：多角色测试工程师 Agent，项目核心
```

## 2. 主入口

运行真正测试工程师 Agent：

```bash
conda run -n AI-TestFlow python -m ai_testflow agent-run
```

运行前必须配置：

```bash
export OPENAI_API_KEY=你的 OpenAI API Key
```

如果未配置 `OPENAI_API_KEY`，`agent-run` 必须直接报错，不允许退回硬编码规则流程。

## 3. 多 Agent 流程

```text
docs/prd.md
  -> PRD Agent：提取业务规则和接口范围
  -> Requirement Agent：拆测试点和验收标准
  -> Test Case Agent：设计接口和页面测试用例
  -> Script Agent：生成 pytest 和 Playwright 脚本
  -> Execute Agent：执行自动化测试
  -> Analysis Agent：分析实际结果和期望结果
  -> Report Agent：生成测试报告
  -> Bug Agent：生成 Bug 单
```

`docs/samples/` 下的需求规格、测试用例、测试报告、Bug 单只是参考样例，不是 Agent 主流程输入。

## 4. 运行产物

产物输出到：

```text
ai-testflow-runs/latest/
```

核心产物：

```text
workflow-state.json
prd-analysis.json
requirements.json
test-points.json
test-cases.json
script-plan.json
generated_api_tests.py
generated_playwright_tests.spec.js
pytest-output.txt
playwright-output.txt
execution-result.json
defect-analysis.json
generated-test-report.md
generated-bug-report.md
```

## 5. 验收判断

本项目保留预埋业务缺陷：

```text
PRD-FR-003 -> REG-002 -> TC-REG-003 -> BUG-001
```

期望：

```text
短用户名 abc 注册应失败，HTTP 400
```

实际：

```text
当前后端注册接口未校验用户名长度，可能返回 HTTP 200
```

Agent 必须基于 PRD、测试用例和执行结果判断该问题为业务规则缺陷，并生成测试报告和 Bug 单。
