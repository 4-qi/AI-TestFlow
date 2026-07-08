# AI-TestFlow

自动化测试全流程插件原型 + React Flask 登录注册 Demo。

本仓库用于验证从 PRD 分析、需求拆解、测试用例设计、用例执行、测试报告生成到 Bug 单提交的最小闭环。

当前项目包含三层：

1. React + Flask 登录注册 Demo 系统。
2. `ai_testflow` CLI 检测工具。
3. `skills/ai-testflow` 专用 AI Skill 组件原型。

## 1. 项目结构

```text
AI-TestFlow/
  AI_TESTFLOW_ENTRYPOINT.md
  ai-testflow.yml
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
conda run -n AI-TestFlow python -m ai_testflow run
```

该命令会自动完成：

1. 读取 `ai-testflow.yml`。
2. 读取 PRD、需求规格、测试用例、后端代码和自动化测试。
3. 运行 `conda run -n AI-TestFlow python -m pytest -q backend/tests`。
4. 捕获真实 pytest 输出。
5. 将失败用例回溯到 `traceability.json` 的 `defects` 列表。
6. 生成结构化需求、测试用例、执行记录、测试报告和 Bug 单。

当前 Demo 中的缺陷实例链路是：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

运行产物输出到：

```text
ai-testflow-runs/latest/
```

核心产物：

```text
inspection-summary.json
requirements.json
pytest-output.txt
traceability.json
generated-test-cases.md
generated-test-report.md
generated-bug-report.md
```

说明：即使检测到 BUG-001，CLI 插件命令也会返回成功。这里的含义是“插件执行成功，并发现缺陷”。

## 4. Skill 组件运行方式

本仓库提供一个 repo 内专用 Skill 原型：

```text
skills/ai-testflow/SKILL.md
```

当 AI 需要以专用组件方式执行本项目检验流程时，从该 Skill 开始，并运行：

```bash
python skills/ai-testflow/scripts/run_ai_testflow.py
```

Skill 会调用现有 CLI，并要求 AI 读取 `ai-testflow-runs/latest/` 下的结构化结果来解释缺陷。

## 5. 安装依赖

后端依赖：

```bash
conda run -n AI-TestFlow pip install -r backend/requirements.txt
```

前端依赖：

```bash
cd frontend
npm install
```

## 6. 启动 Demo 后端

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

## 7. 启动 Demo 前端

在 `frontend` 目录执行：

```bash
npm run dev
```

前端地址：

```text
http://127.0.0.1:5173
```

## 8. 运行底层 pytest

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
4 passed
```

## 9. 预埋缺陷

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

## 10. 文档入口

| 文档 | 路径 |
| --- | --- |
| AI 检验流程入口 | `AI_TESTFLOW_ENTRYPOINT.md` |
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

## 11. AI 检验入口

如果要让 AI 按自动化测试插件流程检验本项目，从根目录入口开始：

```text
AI_TESTFLOW_ENTRYPOINT.md
```

可直接使用的提示词模板：

```text
prompts/ai-testflow-inspection.md
```
