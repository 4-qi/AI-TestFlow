from __future__ import annotations

from typing import Any

from .pytest_runner import PytestResult
from .report_writer import build_bug_report


def render_bug_report(summary: dict[str, Any], traceability: dict[str, Any], pytest_result: PytestResult) -> str:
    return build_bug_report(summary, traceability, pytest_result)

