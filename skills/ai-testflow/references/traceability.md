# AI-TestFlow Traceability

Use this contract only after the current Agent run has completed.

Every reported product defect must link:

```text
requirement_id
  -> test_point_id
  -> charter_id
  -> execution_id
  -> evidence_paths
  -> bug_id
```

The exact identifiers must come from `requirements.json`, `test-points.json`, `test-charters.json`, `defect-analysis.json` and the action/observation logs. Do not reuse identifiers from previous runs and do not read `docs/samples/demo-defect-ground-truth.md` before testing.

Only an execution with status `failed` and Analysis classification `product_defect` may appear in the generated Bug report. `test_data_issue`, `environment_failure` and `agent_blocked` remain execution findings rather than product Bugs.
