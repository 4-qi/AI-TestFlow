from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .agent.orchestrator import run_agent_workflow


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ai_testflow", description="AI-TestFlow CLI plugin prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)

    command_parser = subparsers.add_parser("agent-run", help="Run the live AI testing engineer workflow")
    command_parser.add_argument("--config", default="ai-testflow.yml", help="Path to ai-testflow.yml")

    args = parser.parse_args(argv)
    if args.command == "agent-run":
        return _agent_run(args.config)
    parser.error(f"Unsupported command: {args.command}")
    return 2


def _agent_run(config_path: str) -> int:
    project_root = Path.cwd()
    config = load_config(config_path)
    try:
        _print_agent_header(config_path, config.output_dir)
        result = run_agent_workflow(config, project_root, progress=_print_progress)
    except Exception as exc:
        print(f"AI-TestFlow Agent workflow failed: {exc}")
        return 1

    _print_agent_summary(result.summary, config.output_dir)
    return 0


def _print_agent_header(config_path: str, output_dir: Path) -> None:
    print("AI-TestFlow Agent Workflow", flush=True)
    print(f"- Config: {config_path}", flush=True)
    print(f"- Output directory: {output_dir}", flush=True)
    print("", flush=True)


def _print_agent_summary(summary: dict, output_dir: Path) -> None:
    print("")
    print("AI-TestFlow Result")
    print(f"- Status: {summary['status']}")
    print(f"- Requirements: {summary['requirements_count']}")
    print(f"- Test points: {summary['test_points_count']}")
    print(f"- Test charters: {summary['test_charters_count']}")
    api = summary["api"]
    browser = summary["browser"]
    print(f"- API: passed={api['passed']} failed={api['failed']} blocked={api['blocked']}")
    print(
        "- Browser: "
        f"passed={browser['passed']} failed={browser['failed']} blocked={browser['blocked']}"
    )
    print(f"- Automated passed charters: {summary['automated_charters_count']}")
    print(f"- Automation status: {summary['automation_status']}")
    print(f"- LLM calls: {summary.get('llm_metrics', {}).get('llm_calls', 0)}")
    selection = summary.get("execution_selection", {})
    api_not_executed = selection.get("api_not_executed", [])
    browser_not_executed = selection.get("browser_not_executed", [])
    if api_not_executed or browser_not_executed:
        print(
            "- Not executed by configured budget: "
            f"api={len(api_not_executed)} browser={len(browser_not_executed)}"
        )

    defects = summary.get("defects", [])
    if defects:
        print("- Defects:")
        for defect in defects:
            bug_id = defect.get("bug_id")
            requirement_id = defect.get("requirement_id")
            charter_id = defect.get("charter_id")
            execution_type = defect.get("execution_type")
            execution_id = defect.get("execution_id")
            detail = (
                f"  - {bug_id} | requirement={requirement_id} | charter={charter_id} "
                f"| execution={execution_type}:{execution_id}"
            )
            print(detail)
    else:
        print("- Defects: none")
    print(f"- Output directory: {output_dir}")


def _print_progress(message: str) -> None:
    print(f"[AI-TestFlow] {message}", flush=True)
