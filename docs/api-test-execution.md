# 实时 API 测试执行说明

## 1. 执行方式

Agent 主流程中的接口首次测试不再生成 pytest。API Agent 根据测试任务和最新响应，每次输出一个结构化 `request` 或 `finish` 动作；HTTP Controller 负责发送真实请求、维护 Cookie 并记录证据。

运行命令：

```bash
conda run --no-capture-output -n AI-TestFlow python -m ai_testflow agent-run
```

## 2. 运行证据

```text
ai-testflow-runs/latest/api-action-log.jsonl
ai-testflow-runs/latest/api-observations.jsonl
ai-testflow-runs/latest/api-execution-result.json
```

每次请求记录方法、路径、查询参数、请求体、响应状态码、响应体、Cookie 名称和耗时。API Agent 必须基于这些真实观察结束任务为 `passed`、`failed` 或 `blocked`。

## 3. 与回归脚本的区别

首次探索完成后，Automation Agent 只读取 `passed` API 轨迹，并在 `ai-testflow-runs/latest/regression/` 下生成 pytest 回归脚本。缺陷任务需要修复并重新验证通过后才会进入自动化沉淀。

`backend/tests/` 是 Demo 工程自身的历史回归测试，不是实时 Agent 首次测试入口。
