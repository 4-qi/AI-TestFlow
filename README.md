# AI-TestFlow

多角色测试工程师 Agent + React Flask 登录注册 Demo。

本仓库用于验证真正的 AI Testing Workflow：从 PRD 分析、需求拆解、测试用例设计、接口与页面自动化执行、测试报告生成到 Bug 单提交。

当前项目分为两块：

1. Demo 系统：React + Flask 登录注册，被 AI 自动测试。
2. AI Testing Workflow：多角色测试工程师 Agent，是项目核心。

## 1. 项目结构

```text
AI-TestFlow/
  AI_TESTFLOW_ENTRYPOINT.md
  ai-testflow.yml
  agents/
    ai-testflow-agent.md
    ai-testflow-agent.yaml
  ai_testflow/
  skills/
    ai-testflow/
      SKILL.md
      references/
      scripts/
  backend/
    app.py
    requirements.txt
    tests/test_api.py
  frontend/
    package.json
    src/
  docs/
    project-introduction.md
    task-analysis-and-workflow.md
    prd.md
    samples/
      requirement-spec.sample.md
      test-cases.sample.md
      test-report.sample.md
      bug-report.sample.md
    manual-test-execution.md
    api-test-execution.md
    plugin-prototype-design.md
    agent-prototype-design.md
  prompts/
    ai-testflow-inspection.md
  tests/
    test_ai_testflow.py
```

## 2. 环境

Python 环境：

```bash
conda activate AI-TestFlow
python --version
```

已验证 Python 版本：

```text
Python 3.10.20
```

Node 环境：

```bash
node --version
npm --version
```

已验证版本：

```text
Node v22.19.0
npm 10.9.3
```

## 3. AI 测试工程师 Agent 运行方式

在项目根目录执行：

```bash
conda run --no-capture-output -n AI-TestFlow python -m ai_testflow agent-run
```

该命令会自动完成：

1. 读取 `ai-testflow.yml`。
2. 读取 `docs/prd.md`。
3. PRD Agent 调用大模型分析 PRD。
4. Requirement Agent 调用大模型拆测试点。
5. Test Case Agent 调用大模型设计测试用例。
6. Script Agent 生成 pytest 和 Playwright 脚本。
7. Script Review Agent 基于 PRD、测试用例和源码审查脚本动作，修正无证据断言、缺失前置条件和不稳定定位。
8. Execute Agent 执行接口和页面自动化。
9. Analysis Agent 基于真实执行日志判断缺陷、测试脚本问题或环境问题。
10. Report Agent 生成测试报告。
11. Bug Agent 生成 Bug 单。

运行前必须配置：

```bash
export DEEPSEEK_API_KEY=你的 DeepSeek API Key
```

当前 Demo 中被发现的缺陷实例链路是：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

这条链只是当前 Demo 的缺陷实例。Agent 的输出以 `defect-analysis.json` 里的 `defects` 列表为准，后续增加更多需求、用例和失败测试时，可以输出多条缺陷链。

运行产物输出到：

```text
ai-testflow-runs/latest/
```

核心产物：

```text
inspection-summary.json
workflow-state.json
prd-analysis.json
requirements.json
test-points.json
test-cases.json
script-plan.json
pytest-output.txt
generated_api_tests.py
playwright-output.txt
execution-result.json
defect-analysis.json
generated-test-report.md
generated-bug-report.md
```

页面自动化脚本生成到：

```text
frontend/generated-tests/generated_playwright_tests.spec.js
```

说明：Agent 不依赖登录注册 Demo 的固定规则。Demo 只是当前被测对象；测试点、测试用例、脚本动作和缺陷判断都来自 PRD、源码和真实执行日志。真实测试执行结果请看 `inspection-summary.json` 中的 `pytest_exit_code`、`playwright_exit_code`、`failed_test_names` 和 `defects`。

## 4. Agent 原型

本仓库提供一个本地 Agent 原型：

```text
agents/ai-testflow-agent.md
agents/ai-testflow-agent.yaml
```

Agent 的职责是模拟测试工程师团队：

```text
PRD Agent
  -> Requirement Agent
  -> Test Case Agent
  -> Script Agent
  -> Execute Agent
  -> Analysis Agent
  -> Report Agent
  -> Bug Agent
```

`run-all` 保留为旧兼容入口，不再作为主推演示方式。

## 5. Skill 组件运行方式

本仓库提供一个 repo 内专用 Skill 原型，作为 Agent 的本地执行组件：

```text
skills/ai-testflow/SKILL.md
```

当 AI 需要以专用组件方式执行本项目检验流程时，从该 Skill 开始，并运行：

```bash
python skills/ai-testflow/scripts/run_ai_testflow.py
```

Skill 会调用现有 CLI，并要求 AI 读取 `ai-testflow-runs/latest/` 下的结构化结果来解释缺陷。

## 6. 安装依赖

后端依赖：

```bash
conda run -n AI-TestFlow pip install -r backend/requirements.txt
```

前端依赖：

```bash
cd frontend
npm install
```

## 7. 启动 Demo 后端

在项目根目录执行：

```bash
conda run --no-capture-output -n AI-TestFlow python backend/app.py
```

后端地址：

```text
http://127.0.0.1:5000
```

说明：

后端启动后会一直占用当前终端，这是正常现象。看到 `Backend URL: http://127.0.0.1:5000` 后，保持该终端运行，再打开一个新终端启动前端。停止后端时，在后端终端按 `Ctrl + C`。

## 8. 启动 Demo 前端

在 `frontend` 目录执行：

```bash
npm run dev
```

前端地址：

```text
http://127.0.0.1:5173
```

## 9. 运行底层 pytest

在项目根目录执行：

```bash
conda run -n AI-TestFlow python -m pytest -q backend/tests
```

已验证结果：

```text
1 failed, 11 passed
```

说明：当前失败用例是预埋缺陷 BUG-001 的真实测试结果。项目用于演示从需求到测试失败再到 Bug 单的完整流程，因此该失败是预期业务现象，不是测试脚本写错。

插件自身单元测试：

```bash
conda run -n AI-TestFlow python -m pytest -q tests
```

已验证结果：

```text
9 passed
```

## 10. 预埋缺陷

需求要求：

```text
用户名长度必须大于等于 6 位。
```

当前系统保留的预埋缺陷：

```text
后端注册接口未校验用户名长度，短用户名可以注册成功。
```

追踪关系：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

## 11. 文档入口

| 文档 | 路径 |
| --- | --- |
| AI 检验流程入口 | `AI_TESTFLOW_ENTRYPOINT.md` |
| Agent 原型说明 | `agents/ai-testflow-agent.md` |
| Agent 结构化配置 | `agents/ai-testflow-agent.yaml` |
| AI Skill 组件 | `skills/ai-testflow/SKILL.md` |
| 项目介绍 | `docs/project-introduction.md` |
| 任务分析与流程 | `docs/task-analysis-and-workflow.md` |
| PRD | `docs/prd.md` |
| 需求规格样例 | `docs/samples/requirement-spec.sample.md` |
| 测试用例样例 | `docs/samples/test-cases.sample.md` |
| 手工测试执行记录 | `docs/manual-test-execution.md` |
| 接口自动化测试执行记录 | `docs/api-test-execution.md` |
| 测试报告样例 | `docs/samples/test-report.sample.md` |
| Bug 单样例 | `docs/samples/bug-report.sample.md` |
| 插件原型设计 | `docs/plugin-prototype-design.md` |
| Agent 原型设计 | `docs/agent-prototype-design.md` |

## 12. AI 检验入口

如果要让 AI 按自动化测试插件流程检验本项目，从根目录入口开始：

```text
AI_TESTFLOW_ENTRYPOINT.md
```

可直接使用的提示词模板：

```text
prompts/ai-testflow-inspection.md
```
