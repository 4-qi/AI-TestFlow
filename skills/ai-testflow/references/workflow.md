# AI-TestFlow Skill Workflow

## Purpose

The Skill invokes the repository's live testing Agent and explains its persisted evidence. It must not use historical defect knowledge as test input.

## Inputs

Read exact paths from `ai-testflow.yml`:

- `prd_path` for the business requirements.
- `knowledge_base.path` for general testing heuristics.
- `target_runtime` for local service startup.
- `api_runtime` and `browser_runtime` for live execution.
- `output_dir` for current-run artifacts.

Files under `docs/samples/`, including the Demo defect ground truth, are reference and evaluation artifacts rather than Agent inputs.

## Execution

1. Run `python skills/ai-testflow/scripts/run_ai_testflow.py` from the repository root.
2. Read `inspection-summary.json` and `workflow-state.json`.
3. Read PRD analysis, knowledge context, requirements, test points and test charters.
4. Read API and Browser action/observation logs and execution results.
5. Read defect analysis, automation manifest, test report and Bug report.
6. Explain conclusions only from the latest run artifacts.

## Workflow

```text
PRD analysis
  -> testing knowledge retrieval
  -> requirement and risk breakdown
  -> exploratory charter design
  -> live API and browser execution
  -> result classification
  -> passed-trace automation
  -> report and Bug generation
```

The workflow succeeds when the CLI exits with code `0` and all current-run result files exist. `defects_found` is a successful tool execution with a product defect result; `execution_blocked` means at least one task could not be completed and must not be described as a product defect.
