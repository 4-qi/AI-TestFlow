# AI-TestFlow AI 检验流程入口

## 1. 这个入口解决什么问题

本项目已经具备登录注册 Demo、PRD、需求规格、测试用例、测试执行记录、测试报告和 Bug 单。

但如果要让 AI 按“自动化测试插件”的方式完成检验，需要一个明确入口，告诉 AI：

1. 从哪里开始读取。
2. 读取哪些文件。
3. 按什么顺序分析。
4. 运行什么测试命令。
5. 如何判断系统是否存在 Bug。
6. 如何更新测试报告和 Bug 单。

本文件就是 AI 检验流程的总入口。

## 2. 当前原型的 AI 使用方式

当前项目的 AI 检验流程是“Agent + CLI 插件原型”。

也就是说，现在还不是一个已经打包发布的浏览器插件、IDE 插件或测试平台插件，而是在仓库内用 Agent 配置定义 AI 执行器，再通过 CLI 命令完成自动化测试插件应该完成的事情。

AI 在这个流程中扮演的角色是：

```text
Agent 编排器
  + PRD 分析器
  + 需求拆解器
  + 测试用例设计器
  + 自动化测试脚本生成器
  + 自动化测试执行器
  + 测试报告生成器
  + Bug 单生成器
```

## 3. AI 检验流程总链路

AI 应先读取 Agent 原型：

```text
agents/ai-testflow-agent.md
agents/ai-testflow-agent.yaml
```

然后运行 CLI 执行入口：

```bash
conda run -n AI-TestFlow python -m ai_testflow run-all
```

CLI 插件内部按以下链路执行：

```text
读取 PRD
  -> 读取需求规格
  -> 读取测试用例
  -> 读取后端实现
  -> 分析 PRD 需求编号
  -> 生成结构化需求
  -> 生成测试用例清单
  -> 生成接口自动化测试脚本
  -> 运行 pytest
  -> 分析失败用例
  -> 对齐需求编号
  -> 生成执行记录
  -> 生成测试报告
  -> 生成 Bug 单
```

运行产物输出到：

```text
ai-testflow-runs/latest/
```

## 4. AI 必须读取的文件

AI 执行检验前，必须按顺序读取以下文件：

```text
agents/ai-testflow-agent.md
agents/ai-testflow-agent.yaml
ai-testflow.yml
docs/prd.md
docs/requirement-spec.md
docs/test-cases.md
backend/app.py
backend/tests/test_api.py
docs/api-test-execution.md
docs/test-report.md
docs/bug-report.md
```

读取目的：

| 文件 | 读取目的 |
| --- | --- |
| `agents/ai-testflow-agent.md` | 获取 Agent 角色、流程和行为约束 |
| `agents/ai-testflow-agent.yaml` | 获取 Agent 结构化输入、输出和执行契约 |
| `ai-testflow.yml` | 获取 CLI 精确路径和命令 |
| `docs/prd.md` | 获取原始需求和业务规则 |
| `docs/requirement-spec.md` | 获取结构化需求、接口规格、验收标准 |
| `docs/test-cases.md` | 获取测试用例和需求追踪关系 |
| `backend/app.py` | 获取真实后端实现 |
| `backend/tests/test_api.py` | 获取历史自动化测试和真实断言风格 |
| `docs/api-test-execution.md` | 获取接口测试执行记录格式 |
| `docs/test-report.md` | 获取测试报告格式 |
| `docs/bug-report.md` | 获取 Bug 单格式 |

## 5. AI 必须运行的命令

在项目根目录执行：

```bash
conda run -n AI-TestFlow python -m ai_testflow run-all
```

CLI 内部会运行：

```bash
conda run -n AI-TestFlow python -m pytest -q ai-testflow-runs/latest/generated_api_tests.py
```

当前系统保留预埋缺陷，因此 CLI 摘要应包含：

```text
Status: defects_found
Passed tests: 11
Failed tests: 1
Bug: BUG-001
Requirement: PRD-FR-003
Test case: TC-REG-003
```

pytest 真实结果应包含：

```text
1 failed, 11 passed
```

失败用例应为：

```text
test_generated_register_rejects_short_username
```

失败原因应为：

```text
期望 HTTP 400，实际 HTTP 200
```

## 6. AI 判断缺陷的规则

AI 不允许只根据测试状态判断问题，必须回到需求链路判断。

本项目当前 Demo 缺陷示例链路是：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

含义：

| 编号 | 含义 |
| --- | --- |
| `PRD-FR-003` | 用户注册时，用户名长度必须大于等于 6 位 |
| `REG-002` | `username` 长度必须大于等于 6 位 |
| `AC-003` | 用户名长度小于 6 位时注册失败 |
| `TC-REG-003` | 用户名长度小于 6 位注册失败 |
| `BUG-001` | 注册接口未校验用户名长度，短用户名可注册成功 |

通用能力来自 `traceability.json` 中的 `defects` 列表；下面这条链是当前登录注册 Demo 中被自动化测试发现的缺陷实例。如果测试请求：

```json
{
  "username": "abc",
  "password": "Password123",
  "confirm_password": "Password123"
}
```

实际返回注册成功，则 AI 必须判断为业务规则缺陷。

## 7. AI 应输出什么

AI 完成检验后，应输出以下内容：

1. 测试命令。
2. CLI 真实输出摘要。
3. pytest 真实输出摘要。
4. 一站式流程阶段完成情况。
5. 结构化需求数量。
6. 结构化测试用例数量。
7. 失败用例名称。
8. 失败断言。
9. 缺陷列表中的关联需求编号、测试用例编号和 Bug 编号。
10. 生成产物路径。
11. 需要更新的文档路径。
12. 项目当前结论。

标准结论格式：

```text
本轮 AI 检验确认：登录注册 Demo 主流程可运行；PRD-FR-003 对应的用户名长度规则未在后端注册接口实现；TC-REG-003 自动化测试失败；该失败已形成 BUG-001。
```

## 8. 对 AI 发起检验的提示词

可以直接把下面这段发给 AI：

```text
你现在是 AI-TestFlow 项目的自动化测试插件执行器。

请按以下流程完成一次真实 AI 检验：

1. 读取 docs/prd.md，提取原始需求。
2. 读取 docs/requirement-spec.md，提取结构化需求、接口规格和验收标准。
3. 读取 docs/test-cases.md，确认测试用例与需求编号的追踪关系。
4. 读取 backend/app.py，确认当前后端真实实现。
5. 读取 backend/tests/test_api.py，确认自动化测试真实断言。
6. 运行 conda run -n AI-TestFlow python -m ai_testflow run-all。
7. 读取 ai-testflow-runs/latest/inspection-summary.json、prd-analysis.json、requirements.json、pytest-output.txt、traceability.json、generated-test-cases.md、generated_api_tests.py、generated-test-report.md 和 generated-bug-report.md。
8. 分析 inspection-summary.json 中的 workflow_stages、requirements_count、test_cases_count 和 defects。
9. 分析 pytest 输出中的失败用例。
10. 将失败用例回溯到 traceability.json 中的缺陷列表；当前 Demo 缺陷实例为 PRD-FR-003、REG-002、AC-003、TC-REG-003 和 BUG-001。
11. 如执行结果与 docs/api-test-execution.md、docs/test-report.md、docs/bug-report.md 不一致，请更新这些文档。
12. 最后输出本轮 AI 检验结论。

要求：

- 不要凭记忆判断需求。
- 不要跳过文件读取。
- 不要把预埋 Bug 当成测试脚本错误。
- 必须用真实测试输出支撑结论。
- 必须说明失败用例和需求编号之间的追踪关系。
```

## 9. 人工怎么验证 AI 检验结果

人工只需要看三处：

1. `backend/tests/test_api.py` 中是否存在按需求断言的短用户名测试。
2. pytest 输出是否出现 `test_generated_register_rejects_short_username` 失败。
3. `docs/bug-report.md` 是否记录 `BUG-001` 并关联 `PRD-FR-003`、`REG-002`、`AC-003`、`TC-REG-003`。

如果这三处都一致，说明 AI 检验流程跑通。

## 10. 后续如何升级成真正插件

当前入口是 CLI 插件流程。后续可以升级为以下形式：

1. 安装为系统命令：`ai-testflow run`
2. Web 页面入口：上传 PRD 后点击开始检验。
3. IDE 插件入口：在项目中右键运行 AI 检验。
4. CI 入口：提交代码后自动运行 AI 检验。

无论入口形式如何变化，核心流程保持不变：

```text
读需求 -> 读实现 -> 跑测试 -> 对比期望和实际 -> 生成报告 -> 生成 Bug 单
```
