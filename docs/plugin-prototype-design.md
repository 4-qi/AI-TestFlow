# AI 自动化测试插件最小原型设计方案

## 1. 原型目标

插件原型的目标是把本项目中已经跑通的人工链路抽象成可自动化执行的流程：

```text
PRD 文本
  -> PRD 解析
  -> 结构化需求
  -> 测试点提取
  -> 测试用例生成
  -> 接口或页面执行
  -> 执行结果归档
  -> 测试报告生成
  -> Bug 单生成
  -> Bug 系统推送
```

最小原型先不接入真实公司系统，使用本仓库的登录注册 Demo、Markdown 文档、本地测试脚本和 CLI 插件入口验证流程。

CLI 插件入口：

```bash
conda run -n AI-TestFlow python -m ai_testflow run-all
```

Agent 原型入口：

```text
agents/ai-testflow-agent.md
agents/ai-testflow-agent.yaml
```

当前设计中，Agent 是用户面对的一站式 AI 测试入口，CLI 是稳定执行器，pytest 是真实测试执行层。

## 2. 角色与输入输出

| 阶段 | 输入 | 输出 |
| --- | --- | --- |
| Agent 编排 | 用户检测请求、Agent 配置 | 测试结论、缺陷解释、后续建议 |
| PRD 解析 | `docs/prd.md` | `ai-testflow-runs/latest/prd-analysis.json` |
| 需求结构化 | PRD 解析结果、`docs/requirement-spec.md` | `ai-testflow-runs/latest/requirements.json` |
| 用例生成 | 结构化需求、`docs/test-cases.md` | `ai-testflow-runs/latest/generated-test-cases.md` |
| 自动化脚本生成 | 测试用例、接口规格 | `ai-testflow-runs/latest/generated_api_tests.py` |
| 自动化执行 | 生成的接口测试脚本 | `ai-testflow-runs/latest/pytest-output.txt` |
| 手工记录辅助 | 页面用例、页面地址 | `docs/manual-test-execution.md` |
| 报告生成 | 执行记录、缺陷记录 | `docs/test-report.md` |
| Bug 单生成 | 失败用例、实际结果、期望结果 | `docs/bug-report.md` |
| Bug 推送 | Bug 单结构化字段 | 外部 Bug 系统记录 |

## 3. 模块设计

### 3.0 Agent 编排模块

职责：

1. 接收用户的一站式测试请求。
2. 读取 Agent 配置和项目配置。
3. 调用 CLI 执行完整检测。
4. 读取运行产物并解释测试结论。
5. 将失败用例回溯到 PRD、业务规则、验收标准、测试用例和 Bug 单。

本项目最小实现：

使用 `agents/ai-testflow-agent.md` 和 `agents/ai-testflow-agent.yaml` 描述 Agent 的角色、输入输出、执行命令和行为约束。

### 3.1 PRD 文本解析模块

职责：

1. 读取 PRD 文档。
2. 提取功能需求编号。
3. 提取业务规则。
4. 提取接口范围。
5. 提取验收标准。

本项目最小实现：

读取 `docs/prd.md`，识别 `PRD-FR-*` 和 `PRD-NFR-*` 编号，并输出结构化需求清单。

### 3.2 需求结构化模块

职责：

1. 将 PRD 内容拆成模块、规则、验收标准。
2. 建立需求追踪矩阵。
3. 标记高风险规则。

本项目最小实现：

以 `docs/requirement-spec.md` 和 PRD 解析结果生成运行态结构化需求，并把当前 Demo 中发现的缺陷实例写入 `traceability.json`：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

### 3.3 测试用例生成模块

职责：

1. 根据需求规则生成正向用例。
2. 根据异常规则生成反向用例。
3. 为每条用例绑定需求编号。

本项目最小实现：

读取 `docs/test-cases.md`，生成运行态测试用例清单 `ai-testflow-runs/latest/generated-test-cases.md`，覆盖注册、登录、当前用户查询和退出登录。

### 3.4 自动化测试脚本生成模块

职责：

1. 根据测试用例编号选择接口测试模板。
2. 生成 pytest 可执行脚本。
3. 把生成结果保存为插件运行产物。

本项目最小实现：

读取 `docs/test-cases.md` 后生成：

```text
ai-testflow-runs/latest/generated_api_tests.py
```

### 3.5 自动化执行模块

职责：

1. 根据接口规格组织请求。
2. 执行接口测试。
3. 收集状态码、响应体和断言结果。
4. 输出执行记录。

本项目最小实现：

使用 pytest 执行插件生成的接口测试脚本：

```bash
conda run -n AI-TestFlow python -m ai_testflow run-all
```

CLI 插件内部调用 pytest，并把真实输出保存到 `ai-testflow-runs/latest/pytest-output.txt`。

### 3.6 报告生成模块

职责：

1. 统计测试用例总数。
2. 统计通过和失败数量。
3. 汇总缺陷。
4. 输出测试结论。

本项目最小实现：

根据 pytest 输出和追踪关系生成 `ai-testflow-runs/latest/generated-test-report.md`。

### 3.7 Bug 单生成模块

职责：

1. 从失败用例中提取缺陷标题。
2. 汇总复现步骤。
3. 生成期望结果和实际结果。
4. 绑定需求、规则、验收标准和测试用例。

本项目最小实现：

根据 TC-REG-003 的执行结果生成 `ai-testflow-runs/latest/generated-bug-report.md`。

### 3.8 Bug 推送模块

职责：

1. 将 Bug 单转换为目标系统字段。
2. 调用 Bug 系统 API 创建缺陷。
3. 回写外部 Bug 编号。

本项目最小实现：

当前不接入外部系统，先输出 Markdown Bug 单。后续可对接 Jira、禅道、飞书多维表格或企业内部缺陷系统。

## 4. 最小数据流

```text
docs/prd.md
  -> docs/requirement-spec.md
  -> docs/test-cases.md
  -> agents/ai-testflow-agent.yaml
  -> ai-testflow.yml
  -> python -m ai_testflow run-all
  -> ai-testflow-runs/latest/prd-analysis.json
  -> ai-testflow-runs/latest/requirements.json
  -> ai-testflow-runs/latest/generated-test-cases.md
  -> ai-testflow-runs/latest/generated_api_tests.py
  -> ai-testflow-runs/latest/inspection-summary.json
  -> ai-testflow-runs/latest/generated-test-report.md
  -> ai-testflow-runs/latest/generated-bug-report.md
```

## 5. 原型任务拆解

| 任务编号 | 任务 | 当前实现 |
| --- | --- | --- |
| PLUGIN-TASK-000 | Agent 编排入口 | 已输出 `agents/ai-testflow-agent.md`、`agents/ai-testflow-agent.yaml` |
| PLUGIN-TASK-001 | 读取 PRD 文本 | 使用 Markdown 文档作为输入 |
| PLUGIN-TASK-002 | 提取需求编号和规则 | 已输出 `prd-analysis.json`、`requirements.json` |
| PLUGIN-TASK-003 | 生成测试用例 | 已输出 `generated-test-cases.md` |
| PLUGIN-TASK-004 | 生成接口自动化测试脚本 | 已输出 `generated_api_tests.py` |
| PLUGIN-TASK-005 | 执行接口测试 | 已实现 CLI 调用 pytest |
| PLUGIN-TASK-006 | 汇总执行结果 | 已输出 `inspection-summary.json` |
| PLUGIN-TASK-007 | 生成测试报告 | 已输出 `generated-test-report.md` |
| PLUGIN-TASK-008 | 生成 Bug 单 | 已输出 `generated-bug-report.md` |
| PLUGIN-TASK-009 | 推送 Bug | 当前以 Markdown 模拟外部系统记录 |

## 6. 后续扩展方向

1. 增加 PRD Markdown 自动解析脚本。
2. 增加结构化 JSON 输出，供插件内部流程流转。
3. 增加 Playwright 页面自动化执行。
4. 增加接口测试用例自动生成。
5. 增加测试报告模板渲染。
6. 增加外部 Bug 系统 API 推送。
7. 增加需求变更后的用例差异分析。
8. 将本地 Agent 原型发布为 Workspace Agent 或 IDE Agent。

## 7. 原型验收标准

1. 能从 PRD 明确追踪到需求规则。
2. 能从需求规则生成测试用例。
3. 能执行测试并记录实际结果。
4. 能识别实际结果与期望结果不一致的问题。
5. 能生成标准 Bug 单。
6. 能说明后续接入正式插件的模块边界。
