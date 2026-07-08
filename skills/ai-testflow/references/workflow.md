# AI-TestFlow Skill Workflow

## Purpose

This skill turns the repository into a dedicated AI testing component. It does not replace the CLI; it instructs an AI agent when and how to call the CLI, how to read its outputs, and how to explain the result.

## Fixed Inputs

Read these paths through `ai-testflow.yml`:

| Key | Path |
| --- | --- |
| `prd_path` | `docs/prd.md` |
| `requirement_spec_path` | `docs/requirement-spec.md` |
| `test_cases_path` | `docs/test-cases.md` |
| `backend_source_path` | `backend/app.py` |
| `pytest_path` | `backend/tests` |
| `output_dir` | `ai-testflow-runs/latest` |

## Execution Steps

1. Confirm the working directory is the repository root.
2. Run `python skills/ai-testflow/scripts/run_ai_testflow.py`.
3. Read `ai-testflow-runs/latest/inspection-summary.json`.
4. Read `ai-testflow-runs/latest/traceability.json`.
5. Read `ai-testflow-runs/latest/pytest-output.txt`.
6. Read `ai-testflow-runs/latest/generated-test-report.md` when the user asks for the generated report.
7. Read `ai-testflow-runs/latest/generated-bug-report.md` when the user asks for the generated Bug.

## Success Criteria

The skill execution is successful when:

1. The script exits with code `0`.
2. `inspection-summary.json` exists.
3. `traceability.json` exists.
4. `pytest-output.txt` exists.
5. `inspection-summary.json` contains `status` equal to `defects_found`.

The project is not defect-free. The known defect is expected and should be reported.

## Do Not Do

1. Do not mark the failing pytest result as a broken test script.
2. Do not say all tests pass.
3. Do not invent a different Bug ID.
4. Do not change application code while running the skill.
5. Do not fix `BUG-001` unless the user explicitly asks to repair the Demo bug.

