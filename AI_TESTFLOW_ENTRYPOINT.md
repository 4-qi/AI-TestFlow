# AI-TestFlow Agent 运行入口

## 1. 主命令

在项目根目录执行：

```bash
conda run --no-capture-output -n AI-TestFlow python -m ai_testflow agent-run
```

`--no-capture-output` 用于实时显示每个 Agent 的运行阶段。运行前必须在 `.env` 中配置 `ai-testflow.yml` 的 `llm.api_key_env` 所指向的 Key。

## 2. 执行流程

```text
读取 PRD
  -> 检索本地测试知识
  -> 拆解需求与风险
  -> 生成 API / Browser 探索任务
  -> 启动被测服务
  -> API Agent 实时发送请求
  -> Browser Agent 实时观察和操作浏览器
  -> 分类执行结果并确认产品缺陷
  -> 将 passed 轨迹沉淀为回归脚本
  -> 生成测试报告和 Bug 单
```

首次执行阶段不会生成 pytest 或 Playwright 脚本。页面截图只保存为证据，不会发送给当前文本模型。

## 3. 读取结果

运行结束后先读取：

```text
ai-testflow-runs/latest/inspection-summary.json
ai-testflow-runs/latest/execution-result.json
ai-testflow-runs/latest/defect-analysis.json
ai-testflow-runs/latest/generated-test-report.md
ai-testflow-runs/latest/generated-bug-report.md
ai-testflow-runs/latest/automation-manifest.json
```

需要审计具体过程时，再读取 API 和 Browser 的 action、observation JSONL 文件及 `screenshots/`。

## 4. 状态含义

- `passed`：所有已执行任务通过。
- `defects_found`：发现证据完整的产品缺陷，工作流本身执行成功。
- `execution_blocked`：没有确认产品缺陷，但存在无法完成的任务。

只有配置、服务启动、LLM 或框架自身失败时命令返回非零状态码。
