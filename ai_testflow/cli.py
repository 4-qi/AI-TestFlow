from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .agent.orchestrator import run_agent_workflow
from .inspector import run_inspection


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ai_testflow", description="AI-TestFlow CLI plugin prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command_name in ["agent-run", "analyze-prd", "generate-cases", "generate-tests", "execute", "report", "run", "run-all"]:
        command_parser = subparsers.add_parser(command_name, help=f"Run AI-TestFlow {command_name}")
        command_parser.add_argument("--config", default="ai-testflow.yml", help="Path to ai-testflow.yml")

    args = parser.parse_args(argv)
    if args.command == "agent-run":
        return _agent_run(args.config)
    if args.command in {"analyze-prd", "generate-cases", "generate-tests", "execute", "report", "run", "run-all"}:
        return _run(args.config, args.command)

    parser.error(f"Unsupported command: {args.command}")
    return 2


def _run(config_path: str, command_name: str) -> int:
    project_root = Path.cwd()
    config = load_config(config_path)
    result = run_inspection(config, project_root)

    print(f"AI-TestFlow CLI {command_name} completed.")
    print(f"Status: {result.summary['status']}")
    print(f"Requirements: {result.summary['requirements_count']}")
    print(f"Test cases: {result.summary['test_cases_count']}")
    print(f"Passed tests: {result.summary['passed_tests']}")
    print(f"Failed tests: {result.summary['failed_tests']}")
    if result.summary["bug_id"]:
        print(f"Bug: {result.summary['bug_id']}")
        print(f"Requirement: {result.summary['requirement_id']}")
        print(f"Test case: {result.summary['test_case_id']}")
    print(f"Output directory: {config.output_dir}")

    return 0


def _agent_run(config_path: str) -> int:
    project_root = Path.cwd()
    config = load_config(config_path)
    try:
        print("AI-TestFlow Agent workflow started.", flush=True)
        result = run_agent_workflow(config, project_root, progress=_print_progress)
    except (RuntimeError, ValueError) as exc:
        print(f"AI-TestFlow Agent workflow failed: {exc}")
        return 1

    print("AI-TestFlow Agent workflow completed.")
    print(f"Status: {result.summary['status']}")
    print(f"Requirements: {result.summary['requirements_count']}")
    print(f"Test points: {result.summary['test_points_count']}")
    print(f"Test cases: {result.summary['test_cases_count']}")
    print(f"Passed tests: {result.summary['passed_tests']}")
    print(f"Failed tests: {result.summary['failed_tests']}")
    defects = result.summary.get("defects", [])
    if defects:
        first = defects[0]
        print(f"Bug: {first.get('bug_id')}")
        print(f"Requirement: {first.get('requirement_id')}")
        print(f"Test case: {first.get('test_case_id')}")
    print(f"Output directory: {config.output_dir}")
    return 0


def _print_progress(message: str) -> None:
    print(f"[AI-TestFlow] {message}", flush=True)
