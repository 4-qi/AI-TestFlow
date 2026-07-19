# AI-TestFlow 多角色测试工程师 Agent 设计

## 1. 目标

AI-TestFlow 从 PRD 开始模拟测试工程师的真实工作，不在首次测试前生成自动化脚本：

```text
PRD -> 测试知识 -> 需求与风险 -> 探索任务 -> 实时执行 -> 分析 -> 自动化沉淀 -> 报告与 Bug
```

React + Flask 登录注册系统只是被测对象。Agent 不读取完整前端源码，也不读取 `docs/samples/demo-defect-ground-truth.md`。

## 2. Agent 分工

| Agent | 输入 | 输出 |
| --- | --- | --- |
| PRD Agent | `docs/prd.md` | `prd-analysis.json` |
| Knowledge Agent | PRD 分析、本地 YAML 知识库 | `knowledge-context.json` |
| Requirement Agent | PRD 分析、测试知识 | `requirements.json`、`test-points.json` |
| Test Design Agent | 需求、测试点、测试知识 | `test-charters.json` |
| API Agent | API 测试任务、实时响应 | API 动作、观察和执行结果 |
| Browser Agent | Browser 测试任务、结构化页面观察 | 浏览器动作、观察和执行结果 |
| Analysis Agent | 需求、任务和真实执行证据 | `defect-analysis.json` |
| Report Agent | 全部上游产物 | `generated-test-report.md` |
| Bug Agent | 产品缺陷分析 | `generated-bug-report.md` |
| Automation Agent | 已通过的执行轨迹 | `automation-manifest.json`、`regression/` |

## 3. 实时执行原则

- API Agent 使用 HTTP Controller 发送请求并维护 Cookie，不生成 pytest 后再执行。
- Browser Agent 使用固定 Playwright Controller 操作浏览器，不生成每轮专用 `.spec.js`。
- Browser Agent 只接收 URL、页面文本、Accessibility Tree、交互控件、Console 和 Network 信息。
- 页面截图只保存为证据，阶段一不发送给模型。
- `blocked`、环境失败和测试数据问题不得提交产品 Bug。
- Automation Agent 只能处理 `passed` 轨迹。

## 4. 主入口

```bash
conda run --no-capture-output -n AI-TestFlow python -m ai_testflow agent-run
```

LLM、知识库、服务启动、API 和浏览器运行参数全部由 `ai-testflow.yml` 声明。缺少 `llm.api_key_env` 指向的 Key 时直接失败，不退回硬编码规则。

## 5. 产物

本轮运行产物位于 `ai-testflow-runs/latest/`，核心文件包括知识上下文、测试任务、API 与浏览器 JSONL 轨迹、分类结果、报告、Bug 单和通过轨迹生成的回归脚本。

Structured、Vision 和 Hybrid 三阶段演进方案见 `docs/testing-agent-evolution-roadmap.md`。
