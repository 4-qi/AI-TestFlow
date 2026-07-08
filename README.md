# AI-TestFlow

自动化测试全流程插件原型 + React Flask 登录注册 Demo。

本仓库用于验证从 PRD 分析、需求拆解、测试用例设计、用例执行、测试报告生成到 Bug 单提交的最小闭环。

当前项目包含四层：

1. React + Flask 登录注册 Demo 系统。
2. `ai_testflow` CLI 检测工具。
3. `skills/ai-testflow` 专用 AI Skill 组件原型。
4. `agents/ai-testflow-agent.*` 本地 Agent 原型。

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
    requirement-spec.md
    test-cases.md
    manual-test-execution.md
    api-test-execution.md
    test-report.md
    bug-report.md
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

## 3. CLI 插件运行方式

在项目根目录执行：

```bash
conda run -n AI-TestFlow python -m ai_testflow run-all
```

该命令会自动完成：

1. 读取 `ai-testflow.yml`。
2. 读取 PRD、后端代码和历史自动化测试。
3. 由 Agent 执行 PRD 分析，生成 `prd-analysis.json`。
4. 由 Agent 根据 PRD 生成结构化需求 `requirements.json`。
5. 由 Agent 根据结构化需求设计运行态测试用例清单 `generated-test-cases.md`。
6. 生成可执行接口自动化测试脚本 `generated_api_tests.py`。
7. 运行 `conda run -n AI-TestFlow python -m pytest -q ai-testflow-runs/latest/generated_api_tests.py`。
8. 捕获真实 pytest 输出。
9. 将失败用例回溯到 `traceability.json` 的 `defects` 列表。
10. 生成测试报告和 Bug 单。

当前 Demo 中被发现的缺陷实例链路是：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

这条链只是当前 Demo 的缺陷实例。CLI 的输出以 `traceability.json` 里的 `defects` 列表为准，后续增加更多需求、用例和失败测试时，可以输出多条缺陷链。

运行产物输出到：

```text
ai-testflow-runs/latest/
```

核心产物：

```text
inspection-summary.json
prd-analysis.json
requirements.json
pytest-output.txt
traceability.json
generated-test-cases.md
generated_api_tests.py
generated-test-report.md
generated-bug-report.md
```

说明：即使检测到 BUG-001，CLI 插件命令也会返回成功。这里的含义是“插件执行成功，并发现缺陷”。

## 4. Agent 原型

本仓库提供一个本地 Agent 原型：

```text
agents/ai-testflow-agent.md
agents/ai-testflow-agent.yaml
```

Agent 的职责是调度和解释：

```text
读取配置和上下文
  -> 调用 ai_testflow CLI
  -> 读取运行产物
  -> 解释 PRD 到 Bug 的追踪链路
  -> 输出测试结论和后续建议
```

Agent 不替代 CLI。CLI 负责稳定执行，Agent 负责理解、编排和解释。

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
8 passed
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
| 需求规格说明书 | `docs/requirement-spec.md` |
| 测试用例 | `docs/test-cases.md` |
| 手工测试执行记录 | `docs/manual-test-execution.md` |
| 接口自动化测试执行记录 | `docs/api-test-execution.md` |
| 测试报告 | `docs/test-report.md` |
| Bug 单 | `docs/bug-report.md` |
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
