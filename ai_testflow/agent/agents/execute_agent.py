from __future__ import annotations

from pathlib import Path

from ...pytest_runner import PytestResult, run_pytest


def run_execute_agent(
    pytest_command: list[str],
    playwright_command: list[str] | None,
    project_root: Path,
) -> tuple[PytestResult, PytestResult | None]:
    pytest_result = run_pytest(pytest_command, project_root)
    if not playwright_command:
        return pytest_result, None
    playwright_result = run_pytest(playwright_command, project_root)
    return pytest_result, playwright_result
