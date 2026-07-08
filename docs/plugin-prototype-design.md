# AI 自动化测试 Workflow 原型设计

## 1. 原型目标

本项目不再把登录注册 Demo 当作核心成果。Demo 是被测对象，核心成果是 AI Testing Workflow。

```text
React + Flask Demo
       ▲
       │ 被测试
       │
AI Testing Workflow
```

## 2. 主流程

```text
PRD
  -> PRD Agent
  -> Requirement Agent
  -> Test Case Agent
  -> Script Agent
  -> Execute Agent
  -> Analysis Agent
  -> Report Agent
  -> Bug Agent
```

主命令：

```bash
conda run --no-capture-output -n AI-TestFlow python -m ai_testflow agent-run
```

## 3. 技术边界

| 模块 | 职责 |
| --- | --- |
| 大模型 Agent | 理解 PRD、拆需求、设计用例、分析缺陷、写报告 |
| 本地执行器 | 读写文件、生成脚本、调用 pytest 和 Playwright |
| Demo 系统 | 被测登录注册系统 |
| 运行产物 | 保存每个阶段证据 |

## 4. 样例文档处理

以下文档只作为人工交付物样例，不作为 Agent 主流程输入：

```text
docs/samples/requirement-spec.sample.md
docs/samples/test-cases.sample.md
docs/samples/test-report.sample.md
docs/samples/bug-report.sample.md
```

## 5. 验收标准

1. Agent 从 `docs/prd.md` 开始。
2. Agent 调用大模型生成需求拆解和测试用例。
3. Agent 生成接口和页面自动化脚本。
4. Agent 执行 pytest 和 Playwright。
5. Agent 识别 `BUG-001`。
6. Agent 生成测试报告和 Bug 单。
