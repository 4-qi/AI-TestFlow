# AI-TestFlow

多角色测试工程师 Agent + React Flask 登录注册 Demo。

本仓库用于验证真正的 AI Testing Workflow：从 PRD 分析、测试知识检索、需求拆解、探索任务设计、实时接口与浏览器测试、测试报告生成到 Bug 单提交，并在测试通过后沉淀回归脚本。

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
  knowledge/
    testing/
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
    testing-agent-evolution-roadmap.md
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
4. Knowledge Agent 从本地 YAML 知识库检索测试经验。
5. Requirement Agent 拆解需求、风险和测试点。
6. Test Design Agent 生成 API 或 Browser 探索测试任务，不生成固定脚本。
7. API Agent 通过实时 HTTP 会话执行接口探索测试。
8. Browser Agent 拉起本地 Chromium，循环执行“结构化观察 -> 决策 -> 语义操作”。
9. Analysis Agent 将结果分类为产品缺陷、测试数据问题、环境失败、Agent 阻塞或通过。
10. Report Agent 和 Bug Agent 生成测试报告与证据充分的 Bug 单。
11. Automation Agent 最后只把已通过的执行轨迹沉淀为 pytest 或 Playwright 回归脚本。

为控制真实模型调用时间，`execution_policy.max_charters_per_channel` 限制每个渠道单轮执行的任务数。Test Design Agent 按优先级输出任务，未进入本轮预算的任务会记录在 `workflow-state.json` 和终端摘要中，不会被伪装成已执行或通过。

运行前必须配置 `.env`：

```bash
cp .env.example .env
```

然后编辑 `.env`：

```text
DEEPSEEK_API_KEY=你的 DeepSeek API Key
OPENAI_API_KEY=你的 OpenAI API Key
```

如果使用 DeepSeek，`ai-testflow.yml` 中保持如下配置：

```yaml
llm:
  provider: deepseek
  model: deepseek-v4-pro
  api_key_env: DEEPSEEK_API_KEY
  base_url: https://api.deepseek.com
```

如果使用 OpenAI API，把 `ai-testflow.yml` 中的 `llm` 改成：

```yaml
llm:
  provider: openai
  model: gpt-4.1-mini
  api_key_env: OPENAI_API_KEY
```

OpenAI 配置不需要 `base_url`。如果要使用其他 OpenAI 模型，只修改 `llm.model` 的值即可。

如果要切换模型，直接修改 `llm.model`，例如在 DeepSeek Pro 和 Flash 之间切换：

```yaml
model: deepseek-v4-pro
```

```yaml
model: deepseek-v4-flash
```

`.env` 只保存在本地，不要提交到 Git；`.env.example` 用于说明需要哪些环境变量，可以提交。

当前 Demo 的验收基准链路是：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

该链路只用于验收。缺陷答案保存在 `docs/samples/demo-defect-ground-truth.md`，不属于 Agent 输入。Agent 的真实输出以 `defect-analysis.json` 中的 `defects` 列表为准。

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
knowledge-context.json
test-charters.json
api-action-log.jsonl
api-observations.jsonl
api-execution-result.json
browser-action-log.jsonl
browser-observations.jsonl
browser-execution-result.json
execution-result.json
defect-analysis.json
generated-test-report.md
generated-bug-report.md
automation-manifest.json
regression/
```

首次执行阶段不会生成 pytest 或 Playwright 测试脚本。API Agent 实时发送 HTTP 请求，Browser Agent 实时调用固定 Playwright Controller。只有状态为 `passed` 的轨迹才会在流程末尾写入 `regression/`。

说明：Agent 不依赖登录注册 Demo 的固定规则，也不读取完整前端源码。Demo 只是当前被测对象；测试目标来自 PRD 和通用测试知识，测试结论来自真实接口响应和页面观察。

## 4. Agent 原型

本仓库提供一个本地 Agent 原型：

```text
agents/ai-testflow-agent.md
agents/ai-testflow-agent.yaml
```

Agent 的职责是模拟测试工程师团队：

```text
PRD Agent
  -> Knowledge Agent
  -> Requirement Agent
  -> Test Design Agent
  -> API Agent / Browser Agent
  -> Analysis Agent
  -> Report Agent / Bug Agent
  -> Automation Agent
```

CLI 只保留 `agent-run` 作为公开入口，避免旧规则流程与实时 Agent 流程混淆。

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
npx playwright install chromium
```

`npx playwright install chromium` 安装 Browser Agent 实时控制所需的 Chromium，不会生成页面测试脚本。

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
1 failed, 12 passed
```

说明：当前失败用例是预埋缺陷 BUG-001 的真实测试结果。项目用于演示从需求到测试失败再到 Bug 单的完整流程，因此该失败是预期业务现象，不是测试脚本写错。

插件自身单元测试：

```bash
conda run -n AI-TestFlow python -m pytest -q tests
```

已验证结果：

```text
21 passed
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
| 测试 Agent 三阶段演进路线 | `docs/testing-agent-evolution-roadmap.md` |

## 12. AI 检验入口

如果要让 AI 按自动化测试插件流程检验本项目，从根目录入口开始：

```text
AI_TESTFLOW_ENTRYPOINT.md
```

可直接使用的提示词模板：

```text
prompts/ai-testflow-inspection.md
```

## 13. 提交 GitHub 前检查

建议提交前确认工作区干净：

```bash
git status --short
```

下面这些文件只保存在本地，不提交到 GitHub：

```text
.env
node_modules/
ai-testflow-runs/
frontend/generated-tests/
test-results/
backend/instance/
__pycache__/
.pytest_cache/
```

当前远程仓库地址可用以下命令查看：

```bash
git remote -v
```

推送当前 `master` 分支：

```bash
git push -u origin master
```
