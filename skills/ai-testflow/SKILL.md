---
name: ai-testflow
description: Run and explain the AI-TestFlow one-stop automated testing workflow for this repository. Use when the user asks to inspect the AI-TestFlow project, run the AI-driven testing flow, analyze PRD-to-test-to-bug traceability, generate or explain test reports, validate the React+Flask login/register demo defect, or demonstrate the dedicated AI testing plugin prototype.
---

# AI-TestFlow

## Overview

Use this skill as the dedicated AI component for the AI-TestFlow project. The skill wraps the repository's CLI tool and gives Codex the exact workflow for PRD analysis, requirement traceability, test execution, report generation, and Bug explanation.

## Required Workflow

1. Read `ai-testflow.yml` to get exact paths and commands.
2. Read `references/workflow.md` for the end-to-end execution contract.
3. Read `references/traceability.md` before explaining defect mappings.
4. Run `scripts/run_ai_testflow.py` from the repository root to execute the CLI plugin.
5. Inspect generated outputs under `ai-testflow-runs/latest/`.
6. Explain the full workflow stages and then explain each defect in `traceability.json`.

Do not infer identifiers, paths, fields, or test names. If a required file is missing, report the missing path and stop.

## Execution Command

From the repository root:

```bash
python skills/ai-testflow/scripts/run_ai_testflow.py
```

The script calls:

```bash
conda run -n AI-TestFlow python -m ai_testflow run
```

## Expected Output Contract

After a successful skill run, these files must exist:

```text
ai-testflow-runs/latest/inspection-summary.json
ai-testflow-runs/latest/requirements.json
ai-testflow-runs/latest/pytest-output.txt
ai-testflow-runs/latest/traceability.json
ai-testflow-runs/latest/generated-test-cases.md
ai-testflow-runs/latest/generated-test-report.md
ai-testflow-runs/latest/generated-bug-report.md
```

The CLI command should exit successfully even when it detects the known product defect. The expected project status is `defects_found`, not a tool failure.

## Reporting Rules

When reporting to the user:

1. State whether the skill/CLI execution completed.
2. Report `status`, `requirements_count`, `test_cases_count`, `passed_tests`, `failed_tests`, and `defects` from `inspection-summary.json`.
3. Mention the failing pytest test from `pytest-output.txt`.
4. Explain the one-stop workflow stages from `inspection-summary.json`.
5. Explain each item in `traceability.json` under `defects`.
6. For the current Demo defect, use this exact example chain:

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

7. Distinguish the tool result from the product result:
   - Tool result: CLI/skill execution completed.
   - Product result: known login/register Demo defect found.
