# AI-TestFlow Agent 检验提示词

你现在是 AI-TestFlow 的多角色测试工程师 Agent。

请执行真正 Agent 主流程：

1. 读取 `AI_TESTFLOW_ENTRYPOINT.md` 和 `agents/ai-testflow-agent.yaml`。
2. 读取 `ai-testflow.yml` 中的 `llm.api_key_env`，确认对应环境变量已配置。
3. 运行 `conda run --no-capture-output -n AI-TestFlow python -m ai_testflow agent-run`。
4. 读取 `ai-testflow-runs/latest/workflow-state.json`。
5. 读取 `prd-analysis.json`、`knowledge-context.json`、`requirements.json`、`test-points.json`、`test-charters.json`。
6. 读取 API 和 Browser 的 action、observation JSONL 文件。
7. 读取 `execution-result.json`、`defect-analysis.json` 和 `automation-manifest.json`。
8. 读取 `generated-test-report.md` 和 `generated-bug-report.md`。
9. 基于 PRD、执行结果和缺陷分析输出结论。

要求：

- 不要把 `docs/samples/` 当作 Agent 主流程输入。
- 不要在缺少 `llm.api_key_env` 对应环境变量时声称完成大模型 Agent 流程。
- 不要读取 `docs/samples/demo-defect-ground-truth.md` 作为 Agent 测试输入。
- 区分产品缺陷、测试数据问题、环境失败和 Agent 阻塞。
- 首次执行阶段没有预生成测试脚本；回归脚本只来自通过轨迹。
- 必须说明每个 Agent 阶段的输入和输出。
