# AI-TestFlow 多角色测试工程师 Agent

## 1. 定位

AI-TestFlow 是一个从需求开始工作的测试工程师 Agent 原型。它先使用知识库设计测试，再通过实时 HTTP 和浏览器工具探索被测系统，最后生成报告、Bug 单和已通过场景的回归脚本。

```text
Demo 系统 = 被测对象
AI Testing Workflow = 项目核心
```

## 2. 工作流

| 角色 | 职责 | 主要产物 |
| --- | --- | --- |
| PRD Agent | 提取业务目标、规则和接口范围 | `prd-analysis.json` |
| Knowledge Agent | 检索通用测试经验 | `knowledge-context.json` |
| Requirement Agent | 拆解需求、风险和测试点 | `requirements.json`、`test-points.json` |
| Test Design Agent | 设计 API 或 Browser 探索任务 | `test-charters.json` |
| API Agent | 实时发送请求并观察响应 | `api-*-log.jsonl`、`api-execution-result.json` |
| Browser Agent | 实时观察并操作本地浏览器 | `browser-*-log.jsonl`、`browser-execution-result.json` |
| Analysis Agent | 区分产品缺陷与执行问题 | `defect-analysis.json` |
| Report / Bug Agent | 输出报告和缺陷单 | Markdown 报告 |
| Automation Agent | 最后将通过轨迹沉淀为回归脚本 | `automation-manifest.json`、`regression/` |

## 3. 运行

```bash
conda run --no-capture-output -n AI-TestFlow python -m ai_testflow agent-run
```

首次执行不生成测试脚本。Browser Agent 不读取完整前端源码，不允许模型输出 CSS Selector、XPath 或 JavaScript；API Agent 和 Browser Agent 每次只能提交一个结构化动作。

## 4. 结论规则

- `product_defect`：真实行为违反明确需求，允许生成 Bug。
- `test_data_issue`：测试数据或前置条件问题，不生成 Bug。
- `environment_failure`：服务、网络或浏览器环境问题，不生成 Bug。
- `agent_blocked`：达到最大步骤或无法可靠操作，不生成 Bug。
- `passed`：测试目标满足，可以交给 Automation Agent 沉淀回归脚本。

三阶段观察能力路线见 `docs/testing-agent-evolution-roadmap.md`。
