---
name: ai-testflow
description: Run and explain the AI-TestFlow one-stop automated testing workflow for this repository. Use when the user asks to inspect the AI-TestFlow project, run the AI-driven testing flow, analyze PRD-to-test-to-bug traceability, generate or explain test reports, validate the React+Flask login/register demo defect, or demonstrate the dedicated AI testing plugin prototype.
---

# AI-TestFlow

## Overview

Use this skill as the dedicated AI component for the AI-TestFlow project. The skill invokes the repository's multi-agent CLI entrypoint for knowledge retrieval, exploratory test design, live API and browser execution, defect classification, report generation, and post-validation regression automation.

## Required Workflow

1. Read `ai-testflow.yml` to get exact paths and commands.
2. Read `references/workflow.md` for the end-to-end execution contract.
3. Run `scripts/run_ai_testflow.py` from the repository root to execute the CLI plugin.
4. Inspect generated outputs under `ai-testflow-runs/latest/`.
5. Read `references/traceability.md` before explaining mappings from the current run.
6. Explain the full workflow stages and then explain each defect in `defect-analysis.json`.

Do not infer identifiers, paths, fields, or test names. If a required file is missing, report the missing path and stop.

## Execution Command

From the repository root:

```bash
python skills/ai-testflow/scripts/run_ai_testflow.py
```

The script calls:

```bash
conda run --no-capture-output -n AI-TestFlow python -m ai_testflow agent-run
```

## Expected Output Contract

After a successful skill run, these files must exist:

```text
ai-testflow-runs/latest/inspection-summary.json
ai-testflow-runs/latest/workflow-state.json
ai-testflow-runs/latest/prd-analysis.json
ai-testflow-runs/latest/requirements.json
ai-testflow-runs/latest/test-points.json
ai-testflow-runs/latest/knowledge-context.json
ai-testflow-runs/latest/test-charters.json
ai-testflow-runs/latest/api-action-log.jsonl
ai-testflow-runs/latest/api-observations.jsonl
ai-testflow-runs/latest/browser-action-log.jsonl
ai-testflow-runs/latest/browser-observations.jsonl
ai-testflow-runs/latest/execution-result.json
ai-testflow-runs/latest/defect-analysis.json
ai-testflow-runs/latest/automation-manifest.json
ai-testflow-runs/latest/generated-test-report.md
ai-testflow-runs/latest/generated-bug-report.md
```

The CLI command should exit successfully when the workflow completes and reports product defects. The expected current Demo project status is `defects_found`, not a tool failure.

## Reporting Rules

When reporting to the user:

1. State whether the skill/CLI execution completed.
2. Report `status`, `requirements_count`, `test_charters_count`, API counts, Browser counts, and `defects` from `inspection-summary.json`.
3. Use action and observation logs to explain the real execution evidence.
4. Explain the one-stop workflow stages from `inspection-summary.json`.
5. Explain each item in `defect-analysis.json` under `defects`.
6. Explain every defect chain from `defect-analysis.json`. For the current Demo run, the chain may include `PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001`, but do not treat that as the only possible chain.
7. Distinguish the tool result from the product result:
   - Tool result: CLI/skill execution completed.
   - Product result: based only on the latest live execution and defect classification.
