from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config import TestFlowConfig
from ..pytest_runner import PytestResult
from .agents.analysis_agent import run_analysis_agent
from .agents.bug_agent import run_bug_agent
from .agents.execute_agent import run_execute_agent
from .agents.prd_agent import run_prd_agent
from .agents.report_agent import run_report_agent
from .agents.requirement_agent import run_requirement_agent
from .agents.script_agent import run_script_agent
from .agents.test_case_agent import run_test_case_agent
from .llm_client import LlmSettings, OpenAILlmClient


@dataclass(frozen=True)
class AgentRunResult:
    summary: dict[str, Any]
    output_files: dict[str, Path]
    pytest_result: PytestResult


def run_agent_workflow(config: TestFlowConfig, project_root: Path) -> AgentRunResult:
    output_dir = project_root / config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir = Path(__file__).parent / "prompts"

    llm_settings = LlmSettings(
        provider=config.llm_provider,
        model=config.llm_model,
        api_key_env=config.llm_api_key_env,
    )
    client = OpenAILlmClient(llm_settings)

    prd_text = (project_root / config.prd_path).read_text(encoding="utf-8")
    backend_source = (project_root / config.backend_source_path).read_text(encoding="utf-8")

    workflow_state: dict[str, Any] = {
        "project_name": config.project_name,
        "status": "running",
        "stages": [],
        "source_files_read": [str(config.prd_path), str(config.backend_source_path)],
    }

    prd_analysis = run_prd_agent(client, _prompt(prompts_dir, "prd_agent.md"), prd_text)
    _mark_stage(workflow_state, "PRD Agent", "completed")

    requirement_breakdown = run_requirement_agent(client, _prompt(prompts_dir, "requirement_agent.md"), prd_analysis)
    _mark_stage(workflow_state, "Requirement Agent", "completed")

    test_case_design = run_test_case_agent(client, _prompt(prompts_dir, "test_case_agent.md"), requirement_breakdown)
    _mark_stage(workflow_state, "Test Case Agent", "completed")

    script_files = run_script_agent(
        client,
        _prompt(prompts_dir, "script_agent.md"),
        test_case_design["test_cases"],
        project_root / config.generated_tests_path,
        project_root / config.generated_playwright_tests_path,
    )
    _mark_stage(workflow_state, "Script Agent", "completed")

    pytest_result, playwright_output = run_execute_agent(
        config.generated_pytest_command,
        config.playwright_command,
        project_root,
    )
    _mark_stage(workflow_state, "Execute Agent", "completed")

    execution_result = {
        "pytest": {
            "command": pytest_result.command,
            "exit_code": pytest_result.exit_code,
            "passed_tests": pytest_result.passed_tests,
            "failed_tests": pytest_result.failed_tests,
            "failed_test_names": pytest_result.failed_test_names,
            "output": pytest_result.combined_output,
        },
        "playwright": {
            "command": config.playwright_command or [],
            "output": playwright_output,
        },
    }

    defect_analysis = run_analysis_agent(
        client,
        _prompt(prompts_dir, "analysis_agent.md"),
        requirement_breakdown,
        test_case_design,
        execution_result,
    )
    _mark_stage(workflow_state, "Analysis Agent", "completed")

    report_context = {
        "prd_analysis": prd_analysis,
        "requirements": requirement_breakdown,
        "test_cases": test_case_design,
        "execution_result": execution_result,
        "defect_analysis": defect_analysis,
    }
    test_report = run_report_agent(client, _prompt(prompts_dir, "report_agent.md"), report_context)
    _mark_stage(workflow_state, "Report Agent", "completed")

    bug_report = run_bug_agent(client, _prompt(prompts_dir, "bug_agent.md"), report_context)
    _mark_stage(workflow_state, "Bug Agent", "completed")

    status = "defects_found" if defect_analysis.get("defects") else "passed"
    workflow_state["status"] = status
    summary = {
        "project_name": config.project_name,
        "status": status,
        "requirements_count": len(requirement_breakdown["requirements"]),
        "test_points_count": len(requirement_breakdown["test_points"]),
        "test_cases_count": len(test_case_design["test_cases"]),
        "passed_tests": pytest_result.passed_tests,
        "failed_tests": pytest_result.failed_tests,
        "failed_test_names": pytest_result.failed_test_names,
        "defects": defect_analysis.get("defects", []),
        "output_dir": str(config.output_dir),
    }
    workflow_state["script_files"] = script_files

    output_files = _write_agent_outputs(
        output_dir=output_dir,
        workflow_state=workflow_state,
        prd_analysis=prd_analysis,
        requirement_breakdown=requirement_breakdown,
        test_case_design=test_case_design,
        script_files=script_files,
        execution_result=execution_result,
        defect_analysis=defect_analysis,
        test_report=test_report,
        bug_report=bug_report,
        summary=summary,
    )
    return AgentRunResult(summary=summary, output_files=output_files, pytest_result=pytest_result)


def _prompt(prompts_dir: Path, name: str) -> str:
    return (prompts_dir / name).read_text(encoding="utf-8")


def _mark_stage(workflow_state: dict[str, Any], stage: str, status: str) -> None:
    workflow_state["stages"].append({"stage": stage, "status": status})


def _write_agent_outputs(
    *,
    output_dir: Path,
    workflow_state: dict[str, Any],
    prd_analysis: dict[str, Any],
    requirement_breakdown: dict[str, Any],
    test_case_design: dict[str, Any],
    script_files: dict[str, str],
    execution_result: dict[str, Any],
    defect_analysis: dict[str, Any],
    test_report: str,
    bug_report: str,
    summary: dict[str, Any],
) -> dict[str, Path]:
    files = {
        "workflow_state": output_dir / "workflow-state.json",
        "inspection_summary": output_dir / "inspection-summary.json",
        "prd_analysis": output_dir / "prd-analysis.json",
        "requirements": output_dir / "requirements.json",
        "test_points": output_dir / "test-points.json",
        "test_cases": output_dir / "test-cases.json",
        "script_plan": output_dir / "script-plan.json",
        "execution_result": output_dir / "execution-result.json",
        "defect_analysis": output_dir / "defect-analysis.json",
        "pytest_output": output_dir / "pytest-output.txt",
        "playwright_output": output_dir / "playwright-output.txt",
        "generated_test_report": output_dir / "generated-test-report.md",
        "generated_bug_report": output_dir / "generated-bug-report.md",
    }
    files["workflow_state"].write_text(_json(workflow_state), encoding="utf-8")
    files["inspection_summary"].write_text(_json(summary), encoding="utf-8")
    files["prd_analysis"].write_text(_json(prd_analysis), encoding="utf-8")
    files["requirements"].write_text(_json(requirement_breakdown["requirements"]), encoding="utf-8")
    files["test_points"].write_text(_json(requirement_breakdown["test_points"]), encoding="utf-8")
    files["test_cases"].write_text(_json(test_case_design["test_cases"]), encoding="utf-8")
    files["script_plan"].write_text(_json(script_files["script_plan"]), encoding="utf-8")
    files["execution_result"].write_text(_json(execution_result), encoding="utf-8")
    files["defect_analysis"].write_text(_json(defect_analysis), encoding="utf-8")
    files["pytest_output"].write_text(execution_result["pytest"]["output"], encoding="utf-8")
    files["playwright_output"].write_text(execution_result["playwright"]["output"], encoding="utf-8")
    files["generated_test_report"].write_text(test_report, encoding="utf-8")
    files["generated_bug_report"].write_text(bug_report, encoding="utf-8")
    return files


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
