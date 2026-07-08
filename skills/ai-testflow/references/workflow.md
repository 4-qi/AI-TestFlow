# AI-TestFlow Skill Workflow

## Purpose

This skill turns the repository into a dedicated AI testing component. It does not replace the CLI; it instructs an AI agent when and how to call the CLI, how to read its outputs, and how to explain the result.

## Fixed Inputs

Read these paths through `ai-testflow.yml`:

| Key | Path |
| --- | --- |
| `prd_path` | `docs/prd.md` |
| `backend_source_path` | `backend/app.py` |
| `pytest_path` | `backend/tests` |
| `generated_tests_path` | `ai-testflow-runs/latest/generated_api_tests.py` |
| `output_dir` | `ai-testflow-runs/latest` |

`requirement_spec_path` and `test_cases_path` can exist in `ai-testflow.yml` as reference artifact paths, but the Agent workflow generates runtime requirements and runtime test cases from `docs/prd.md`.

## Execution Steps

1. Confirm the working directory is the repository root.
2. Run `python skills/ai-testflow/scripts/run_ai_testflow.py`.
3. Read `ai-testflow-runs/latest/inspection-summary.json`.
4. Read `ai-testflow-runs/latest/defect-analysis.json`.
5. Read `ai-testflow-runs/latest/pytest-output.txt`.
6. Read `ai-testflow-runs/latest/prd-analysis.json`.
7. Read `ai-testflow-runs/latest/requirements.json`.
8. Read `ai-testflow-runs/latest/test-cases.json`.
9. Read `ai-testflow-runs/latest/generated_api_tests.py`.
10. Read `ai-testflow-runs/latest/generated-test-report.md` when the user asks for the generated report.
11. Read `ai-testflow-runs/latest/generated-bug-report.md` when the user asks for the generated Bug.

## One-Stop Workflow Stages

The skill represents these stages:

```text
PRD分析 -> 需求拆解 -> 测试用例设计 -> 自动化测试脚本生成 -> 用例执行 -> 测试报告生成 -> 自动提Bug
```

`inspection-summary.json` contains `workflow_stages`. Use those stages to explain what the AI component completed.

## Success Criteria

The skill execution is successful when:

1. The script exits with code `0`.
2. `inspection-summary.json` exists.
3. `defect-analysis.json` exists.
4. `pytest-output.txt` exists.
5. `prd-analysis.json` exists.
6. `generated_api_tests.py` exists.
7. `inspection-summary.json` contains `workflow_stages`.
8. `defect-analysis.json` contains `defects`.

The current Demo is not defect-free. The known Demo defect is expected and should be reported as one item in `defects`.

## Do Not Do

1. Do not mark the failing pytest result as a broken test script.
2. Do not say all tests pass.
3. Do not invent a different Bug ID.
4. Do not change application code while running the skill.
5. Do not fix `BUG-001` unless the user explicitly asks to repair the Demo bug.
6. Do not present `BUG-001` as the only kind of defect the workflow can explain; it is the current Demo instance.
