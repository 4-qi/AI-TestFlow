from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import TestFlowConfig
from .pytest_runner import PytestResult, run_pytest
from .report_writer import build_bug_report, build_test_report


TRACEABILITY = {
    "requirement_id": "PRD-FR-003",
    "rule_id": "REG-002",
    "acceptance_id": "AC-003",
    "test_case_id": "TC-REG-003",
    "bug_id": "BUG-001",
    "failed_test_name": "test_register_rejects_short_username_by_requirement",
    "expected": "用户名长度小于 6 位时注册失败，HTTP 400",
    "actual": "用户名长度小于 6 位时注册成功，HTTP 200",
}


@dataclass(frozen=True)
class InspectionResult:
    summary: dict[str, Any]
    traceability: dict[str, Any]
    pytest_result: PytestResult
    generated_test_report: str
    generated_bug_report: str
    output_files: dict[str, Path]


def run_inspection(config: TestFlowConfig, project_root: Path) -> InspectionResult:
    source_context = _read_source_context(config, project_root)
    pytest_result = run_pytest(config.pytest_command, project_root)
    defects_found = pytest_result.failed_tests > 0

    traceability = {
        **TRACEABILITY,
        "status": "failed" if defects_found else "passed",
        "source_files_read": sorted(source_context),
    }
    summary = {
        "project_name": config.project_name,
        "status": "defects_found" if defects_found else "passed",
        "pytest_exit_code": pytest_result.exit_code,
        "passed_tests": pytest_result.passed_tests,
        "failed_tests": pytest_result.failed_tests,
        "failed_test_names": pytest_result.failed_test_names,
        "bug_id": TRACEABILITY["bug_id"] if defects_found else None,
        "requirement_id": TRACEABILITY["requirement_id"] if defects_found else None,
        "test_case_id": TRACEABILITY["test_case_id"] if defects_found else None,
        "output_dir": str(config.output_dir),
    }

    generated_test_report = build_test_report(summary, traceability, pytest_result)
    generated_bug_report = build_bug_report(summary, traceability, pytest_result)
    output_files = _write_outputs(config, project_root, summary, traceability, pytest_result, generated_test_report, generated_bug_report)

    return InspectionResult(
        summary=summary,
        traceability=traceability,
        pytest_result=pytest_result,
        generated_test_report=generated_test_report,
        generated_bug_report=generated_bug_report,
        output_files=output_files,
    )


def _read_source_context(config: TestFlowConfig, project_root: Path) -> dict[str, str]:
    paths = [
        config.prd_path,
        config.requirement_spec_path,
        config.test_cases_path,
        config.backend_source_path,
        config.pytest_path / "test_api.py",
        config.api_execution_report_path,
        config.test_report_path,
        config.bug_report_path,
    ]
    context: dict[str, str] = {}
    for relative_path in paths:
        full_path = project_root / relative_path
        context[str(relative_path)] = full_path.read_text(encoding="utf-8")
    return context


def _write_outputs(
    config: TestFlowConfig,
    project_root: Path,
    summary: dict[str, Any],
    traceability: dict[str, Any],
    pytest_result: PytestResult,
    generated_test_report: str,
    generated_bug_report: str,
) -> dict[str, Path]:
    output_dir = project_root / config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "inspection_summary": output_dir / "inspection-summary.json",
        "pytest_output": output_dir / "pytest-output.txt",
        "traceability": output_dir / "traceability.json",
        "generated_test_report": output_dir / "generated-test-report.md",
        "generated_bug_report": output_dir / "generated-bug-report.md",
    }
    files["inspection_summary"].write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files["pytest_output"].write_text(pytest_result.combined_output, encoding="utf-8")
    files["traceability"].write_text(json.dumps(traceability, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files["generated_test_report"].write_text(generated_test_report, encoding="utf-8")
    files["generated_bug_report"].write_text(generated_bug_report, encoding="utf-8")
    return files

