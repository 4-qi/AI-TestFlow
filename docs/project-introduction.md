# AI-TestFlow 项目介绍

## 1. 项目是什么

AI-TestFlow 是一个多角色 AI 测试工程师 Agent 原型。它从 PRD 开始，结合本地测试知识完成需求分析和探索任务设计，然后实时调用接口和本地浏览器测试被测系统，最后输出执行证据、测试报告、Bug 单，并把已经验证通过的路径沉淀为回归脚本。

项目同时包含 React + Flask 登录注册 Demo，但两者角色不同：

```text
React + Flask Demo = 被测对象
AI Testing Workflow = 项目核心
```

## 2. 为什么不再先生成脚本

测试工程师拿到新需求后，通常先理解业务和风险，再操作真实系统确认行为。若直接从需求生成固定 Playwright 或 pytest 脚本，模型会提前假设页面结构、定位方式、接口行为和测试路径，更接近脚本生成器而不是测试工程师。

AI-TestFlow 因此采用：

```text
Goal -> Observe -> Decide -> Act -> Observe -> Conclude
```

自动化脚本被放到测试验证之后，只用于沉淀稳定回归路径。

## 3. 当前完整流程

1. PRD Agent 从 `docs/prd.md` 提取业务目标、业务规则和接口范围。
2. Knowledge Agent 从 `knowledge/testing/` 检索表单、认证、API 和 Web 探索经验。
3. Requirement Agent 结合 PRD 和知识条目拆解需求、风险和测试点。
4. Test Design Agent 输出 API 或 Browser 测试任务，只说明验证目标，不规定固定脚本步骤。
5. API Agent 在真实 HTTP 会话中逐步发送请求并观察响应。
6. Browser Agent 拉起 Chromium，读取页面文本、Accessibility Tree 和控件信息，再逐步输入、点击和观察。
7. Analysis Agent 区分产品缺陷、测试数据问题、环境失败、Agent 阻塞和通过。
8. Report Agent 和 Bug Agent 输出结构化测试报告与有证据支撑的缺陷单。
9. Automation Agent 最后只把 `passed` 执行轨迹转换成回归脚本并进行语法校验。

## 4. 无视觉 Browser Agent

阶段一不使用视觉模型。Browser Agent 看到的是运行页面的结构化状态：

- URL 和页面标题。
- 页面可见文本。
- Accessibility Tree。
- 输入框、按钮、链接等可交互控件。
- Console 错误和失败网络请求。

Playwright 是固定 Browser Controller，只负责执行 `navigate`、`fill`、`click`、`press`、`select_option`、`check`、`scroll` 和 `wait`。模型不能输出 CSS Selector、XPath、JavaScript 或完整测试文件。

截图会保存到运行目录作为审计证据，但不会发送给当前文本模型。

## 5. 实时 API Agent

API Agent 使用结构化 `request` 动作调用真实接口。HTTP Controller 维护 Cookie，并记录请求方法、路径、请求体、状态码、响应体和耗时。每次响应都会返回给大模型，由它决定继续请求还是结束任务。

这与生成 pytest 后执行不同：首次测试的动作是根据最新系统状态实时决定的。pytest 只在场景通过后由 Automation Agent 生成。

## 6. 缺陷判断

Analysis Agent 使用五类结果：

| 分类 | 含义 | 是否生成 Bug |
| --- | --- | --- |
| `product_defect` | 真实行为违反明确需求 | 是 |
| `test_data_issue` | 数据或前置条件不成立 | 否 |
| `environment_failure` | 服务、网络或浏览器异常 | 否 |
| `agent_blocked` | 达到最大步骤或无法可靠操作 | 否 |
| `passed` | 目标满足 | 否，进入自动化沉淀 |

程序还会校验缺陷引用的 `execution_id` 是否真实失败，避免模型把 blocked 或未执行任务写成产品 Bug。

## 7. Demo 和缺陷基准

Demo 实现注册、登录、当前用户和退出登录功能，并保留用户名长度规则缺陷，用于验证 Agent 是否能发现需求与实现不一致。

业务 PRD 不再披露缺陷答案。真实缺陷基准位于 `docs/samples/demo-defect-ground-truth.md`，只用于运行后的效果评估，不进入 Agent 上下文。

## 8. 如何运行

配置 `.env` 和 `ai-testflow.yml` 后，在项目根目录执行：

```bash
conda run --no-capture-output -n AI-TestFlow python -m ai_testflow agent-run
```

CLI 会自动启动 Flask 和 React，实时输出十个 Agent 阶段，并把结果写入 `ai-testflow-runs/latest/`。发现产品缺陷表示测试工作流成功完成，因此命令仍返回 `0`；只有配置、LLM、服务启动或框架失败才返回 `1`。

`execution_policy.max_charters_per_channel` 用于限制单轮真实模型执行预算。没有进入预算的任务会明确记录为未执行，不参与通过率和缺陷判断。

## 9. 主要运行产物

```text
prd-analysis.json
knowledge-context.json
requirements.json
test-points.json
test-charters.json
api-action-log.jsonl
api-observations.jsonl
browser-action-log.jsonl
browser-observations.jsonl
execution-result.json
defect-analysis.json
automation-manifest.json
generated-test-report.md
generated-bug-report.md
regression/
```

JSONL 文件保留每一步动作和观察，Markdown 文件用于测试结论展示，`regression/` 只保存本轮通过任务生成的脚本。

## 10. 项目价值

该项目展示了三类能力：

1. React、Flask、SQLite 前后端 Demo 开发。
2. 从需求、风险、探索测试、执行证据到 Bug 单的完整测试工程流程。
3. LLM 结构化输出、多 Agent 编排、知识检索、实时工具调用、失败分类和可追溯产物设计。

页面观察后续将按 Structured、Vision、Hybrid 三阶段扩展，详细方案见 `docs/testing-agent-evolution-roadmap.md`。
