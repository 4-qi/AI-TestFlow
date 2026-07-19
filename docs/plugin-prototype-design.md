# AI-TestFlow 插件原型设计

## 1. 原型定位

AI-TestFlow 当前以本地 CLI + 多角色 Agent + Skill 的形式验证一站式测试工作流。React + Flask Demo 是被测对象，不是插件本体。

```text
PRD
  -> 测试知识检索
  -> 需求和风险拆解
  -> 探索测试任务设计
  -> 实时 API / Browser 测试
  -> 结果分类
  -> 报告与 Bug
  -> 通过轨迹自动化
```

## 2. 组件

| 组件 | 作用 |
| --- | --- |
| CLI | 提供统一 `agent-run` 入口和实时进度 |
| LLM Client | 支持 DeepSeek 与 OpenAI 的结构化输出 |
| Knowledge Base | 保存通用测试经验并提供本地检索 |
| HTTP Controller | 实时发送接口请求、维护 Cookie 和记录响应 |
| Playwright Controller | 维持浏览器会话并执行受限语义动作 |
| Agent Orchestrator | 编排分析、设计、执行、分类、报告和自动化 |
| Artifact Store | 将每个阶段结果保存为 JSON、JSONL、Markdown 和截图 |
| Skill | 指导上层 AI 调用 CLI 并解释最新运行证据 |

## 3. 通用边界

- 被测项目通过 `ai-testflow.yml` 声明启动命令、就绪地址、API 地址和页面地址。
- 首次测试只读取 PRD、通用测试知识和运行中的系统，不读取完整前端源码。
- 页面模型动作不允许携带 CSS Selector、XPath 或 JavaScript。
- 缺陷基准和历史样例不进入 Agent 输入。
- 自动化脚本只能从本轮已通过轨迹生成。

## 4. 后续形态

当前 CLI 可继续封装为 IDE 插件、Web 控制台或远程 Agent 服务。三阶段页面观察方案见 `docs/testing-agent-evolution-roadmap.md`。
