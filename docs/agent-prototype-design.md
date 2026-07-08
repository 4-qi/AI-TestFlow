# AI-TestFlow Agent 原型设计方案

## 1. 设计目标

AI-TestFlow Agent 的目标是把已有 CLI 插件原型升级为面向用户的一站式 AI 测试执行入口。

升级后的分工是：

```text
Agent 负责理解、编排、解释
CLI 负责稳定、可重复、可验证地执行
pytest 负责真实测试执行
文档和 JSON 负责证据留存
```

因此，Agent 不是单纯聊天说明，也不是把所有逻辑写进提示词，而是把 AI 决策层和确定性执行层组合起来。

## 2. Agent 架构

```text
用户请求
  -> AI-TestFlow Agent
  -> 读取 Agent 配置
  -> 读取 Skill 执行规范
  -> 调用 ai_testflow CLI
  -> 读取运行产物
  -> 解释测试结果和 Bug
  -> 输出测试结论
```

当前仓库实现：

| 模块 | 路径 | 作用 |
| --- | --- | --- |
| Agent 说明 | `agents/ai-testflow-agent.md` | 定义 Agent 角色、输入、输出、约束 |
| Agent 配置 | `agents/ai-testflow-agent.yaml` | 结构化声明命令、输入、输出、阶段 |
| Skill 组件 | `skills/ai-testflow/SKILL.md` | 给 AI 提供本地执行步骤 |
| CLI 执行器 | `ai_testflow/` | 执行全流程并生成产物 |
| 运行产物 | `ai-testflow-runs/latest/` | 保存 JSON、pytest 输出、报告和 Bug 单 |

## 3. Agent 与 CLI 的边界

| 能力 | Agent | CLI |
| --- | --- | --- |
| 理解用户意图 | 是 | 否 |
| 决定是否执行检测 | 是 | 否 |
| 读取配置 | 是 | 是 |
| PRD 解析 | 调度并解释 | 执行并输出 JSON |
| 测试脚本生成 | 调度并解释 | 执行并写入文件 |
| pytest 执行 | 调度 | 执行 |
| 缺陷链路解释 | 是 | 输出结构化数据 |
| Markdown 报告生成 | 解释和引用 | 执行并写入文件 |
| Bug 系统推送 | 后续扩展 | 后续扩展 |

这种边界能避免把 Agent 做成不可验证的纯提示词流程。所有关键结论都必须落到文件和测试输出上。

## 4. Agent 输入输出契约

Agent 输入：

```text
ai-testflow.yml
docs/prd.md
docs/requirement-spec.md
docs/test-cases.md
backend/app.py
backend/tests/test_api.py
```

Agent 调用：

```bash
conda run -n AI-TestFlow python -m ai_testflow run-all
```

Agent 输出依据：

```text
ai-testflow-runs/latest/inspection-summary.json
ai-testflow-runs/latest/prd-analysis.json
ai-testflow-runs/latest/requirements.json
ai-testflow-runs/latest/generated-test-cases.md
ai-testflow-runs/latest/generated_api_tests.py
ai-testflow-runs/latest/pytest-output.txt
ai-testflow-runs/latest/traceability.json
ai-testflow-runs/latest/generated-test-report.md
ai-testflow-runs/latest/generated-bug-report.md
```

## 5. 当前最小闭环

当前 Agent 原型已经能覆盖：

1. PRD 分析。
2. 需求拆解。
3. 测试用例设计。
4. 自动化测试脚本生成。
5. 用例执行。
6. 测试报告生成。
7. Bug 单生成。

当前运行结果：

```text
status: defects_found
requirements_count: 14
test_cases_count: 12
passed_tests: 11
failed_tests: 1
failed_test_names: test_generated_register_rejects_short_username
```

当前缺陷实例：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

## 6. Agent 演示方式

演示时可以按三步说明：

1. 用户向 Agent 发起检测请求。
2. Agent 调用 CLI 执行全流程。
3. Agent 读取产物并输出测试结论。

演示命令：

```bash
conda run -n AI-TestFlow python -m ai_testflow run-all
```

然后展示：

```text
agents/ai-testflow-agent.md
agents/ai-testflow-agent.yaml
ai-testflow-runs/latest/inspection-summary.json
ai-testflow-runs/latest/generated-test-report.md
ai-testflow-runs/latest/generated-bug-report.md
```

## 7. 后续升级方向

1. 接入真实大模型 API，让 Agent 直接解析新 PRD 并生成更多测试用例。
2. 增加 Playwright 页面自动化测试生成。
3. 增加 Jira、禅道或飞书多维表格 Bug 推送。
4. 增加 CI 触发入口，在代码提交后自动运行 Agent。
5. 发布成 Workspace Agent 或 IDE Agent，使用户通过对话触发检测。
