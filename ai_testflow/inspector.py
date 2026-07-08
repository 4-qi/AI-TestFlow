from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .agent_designer import design_requirements_from_prd, design_test_cases_from_requirements
from .analyzer import analyze_prd
from .config import TestFlowConfig
from .pytest_runner import PytestResult, run_pytest
from .report_writer import build_bug_report, build_generated_test_cases, build_test_report
from .test_generator import render_generated_api_tests


KNOWN_DEFECTS = [
    {
        "requirement_id": "PRD-FR-003",
        "rule_id": "REG-002",
        "acceptance_id": "AC-003",
        "test_case_id": "TC-REG-003",
        "bug_id": "BUG-001",
        "failed_test_name": "test_register_rejects_short_username_by_requirement",
        "generated_failed_test_name": "test_generated_register_rejects_short_username",
        "expected": "用户名长度小于 6 位时注册失败，HTTP 400",
        "actual": "用户名长度小于 6 位时注册成功，HTTP 200",
        "title": "注册接口未校验用户名长度，短用户名可注册成功",
    }
]

TRACEABILITY = {
    "requirement_id": "PRD-FR-003",
    "rule_id": "REG-002",
    "acceptance_id": "AC-003",
    "test_case_id": "TC-REG-003",
    "bug_id": "BUG-001",
    "failed_test_name": "test_generated_register_rejects_short_username",
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
    prd_analysis = analyze_prd(source_context[str(config.prd_path)])
    requirements = design_requirements_from_prd(prd_analysis)
    test_cases = design_test_cases_from_requirements(requirements)
    generated_test_cases = build_generated_test_cases(test_cases)
    generated_api_tests = render_generated_api_tests(test_cases)
    _write_generated_api_tests(config, project_root, generated_api_tests)
    pytest_result = run_pytest(config.generated_pytest_command, project_root)
    defects_found = pytest_result.failed_tests > 0
    defects = _map_defects(pytest_result.failed_test_names)
    workflow_stages = _build_workflow_stages(requirements, test_cases, pytest_result, defects)

    traceability = {
        "status": "failed" if defects_found else "passed",
        "requirements": requirements,
        "test_cases": test_cases,
        "defects": defects,
        "demo_traceability_example": TRACEABILITY,
        "source_files_read": sorted(source_context),
    }
    summary = {
        "project_name": config.project_name,
        "status": "defects_found" if defects_found else "passed",
        "pytest_exit_code": pytest_result.exit_code,
        "requirements_count": len(requirements),
        "test_cases_count": len(test_cases),
        "passed_tests": pytest_result.passed_tests,
        "failed_tests": pytest_result.failed_tests,
        "failed_test_names": pytest_result.failed_test_names,
        "defects": defects,
        "bug_id": defects[0]["bug_id"] if defects else None,
        "requirement_id": defects[0]["requirement_id"] if defects else None,
        "test_case_id": defects[0]["test_case_id"] if defects else None,
        "workflow_stages": workflow_stages,
        "output_dir": str(config.output_dir),
    }

    generated_test_report = build_test_report(summary, traceability, pytest_result)
    generated_bug_report = build_bug_report(summary, traceability, pytest_result)
    output_files = _write_outputs(
        config,
        project_root,
        summary,
        traceability,
        pytest_result,
        prd_analysis,
        generated_test_cases,
        generated_api_tests,
        generated_test_report,
        generated_bug_report,
    )

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
    prd_analysis: dict[str, Any],
    generated_test_cases: str,
    generated_api_tests: str,
    generated_test_report: str,
    generated_bug_report: str,
) -> dict[str, Path]:
    output_dir = project_root / config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "inspection_summary": output_dir / "inspection-summary.json",
        "prd_analysis": output_dir / "prd-analysis.json",
        "requirements": output_dir / "requirements.json",
        "pytest_output": output_dir / "pytest-output.txt",
        "traceability": output_dir / "traceability.json",
        "generated_test_cases": output_dir / "generated-test-cases.md",
        "generated_api_tests": output_dir / "generated_api_tests.py",
        "generated_test_report": output_dir / "generated-test-report.md",
        "generated_bug_report": output_dir / "generated-bug-report.md",
    }
    files["inspection_summary"].write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files["prd_analysis"].write_text(json.dumps(prd_analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files["requirements"].write_text(json.dumps(traceability["requirements"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files["pytest_output"].write_text(pytest_result.combined_output, encoding="utf-8")
    files["traceability"].write_text(json.dumps(traceability, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files["generated_test_cases"].write_text(generated_test_cases, encoding="utf-8")
    files["generated_api_tests"].write_text(generated_api_tests, encoding="utf-8")
    files["generated_test_report"].write_text(generated_test_report, encoding="utf-8")
    files["generated_bug_report"].write_text(generated_bug_report, encoding="utf-8")
    return files


def _map_defects(failed_test_names: list[str]) -> list[dict[str, str]]:
    defects: list[dict[str, str]] = []
    for failed_test_name in failed_test_names:
        for defect in KNOWN_DEFECTS:
            if failed_test_name in {defect["failed_test_name"], defect["generated_failed_test_name"]}:
                mapped = dict(defect)
                mapped["failed_test_name"] = failed_test_name
                defects.append(mapped)
    return defects


def _build_workflow_stages(
    requirements: list[dict[str, str]],
    test_cases: list[dict[str, str]],
    pytest_result: PytestResult,
    defects: list[dict[str, str]],
) -> list[dict[str, str | int]]:
    return [
        {"stage": "PRD分析", "status": "completed", "output": "需求原文已读取"},
        {"stage": "需求拆解", "status": "completed", "output": len(requirements)},
        {"stage": "测试用例设计", "status": "completed", "output": len(test_cases)},
        {"stage": "自动化测试脚本生成", "status": "completed", "output": "generated_api_tests.py"},
        {"stage": "用例执行", "status": "completed", "output": pytest_result.failed_tests + pytest_result.passed_tests},
        {"stage": "测试报告生成", "status": "completed", "output": "generated-test-report.md"},
        {"stage": "自动提Bug", "status": "completed" if defects else "skipped", "output": len(defects)},
    ]


def _write_generated_api_tests(config: TestFlowConfig, project_root: Path, generated_api_tests: str) -> None:
    target = project_root / config.generated_tests_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(generated_api_tests, encoding="utf-8")
