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
        _print_agent_header(config_path, config.output_dir)
        result = run_agent_workflow(config, project_root, progress=_print_progress)
    except (RuntimeError, ValueError) as exc:
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
    print(f"- Test cases: {summary['test_cases_count']}")
    print(f"- Pytest exit code: {summary.get('pytest_exit_code')}")
    print(f"- Passed tests: {summary['passed_tests']}")
    print(f"- Failed tests: {summary['failed_tests']}")
    print(f"- Playwright exit code: {summary.get('playwright_exit_code')}")
    print(f"- Playwright passed tests: {summary.get('playwright_passed_tests')}")
    print(f"- Playwright failed tests: {summary.get('playwright_failed_tests')}")
    failed_test_names = summary.get("failed_test_names", [])
    if failed_test_names:
        print("- Failed test names:")
        for failed_test_name in failed_test_names:
            print(f"  - {failed_test_name}")
    playwright_failed_test_names = summary.get("playwright_failed_test_names", [])
    if playwright_failed_test_names:
        print("- Playwright failed test names:")
        for failed_test_name in playwright_failed_test_names:
            print(f"  - {failed_test_name}")

    defects = summary.get("defects", [])
    if defects:
        print("- Defects:")
        for defect in defects:
            bug_id = defect.get("bug_id")
            requirement_id = defect.get("requirement_id")
            test_case_id = defect.get("test_case_id")
            failed_test_name = defect.get("failed_test_name")
            detail = f"  - {bug_id} | requirement={requirement_id} | test_case={test_case_id}"
            if failed_test_name:
                detail += f" | failed_test={failed_test_name}"
            print(detail)
    else:
        print("- Defects: none")
    print(f"- Output directory: {output_dir}")


def _print_progress(message: str) -> None:
    print(f"[AI-TestFlow] {message}", flush=True)
