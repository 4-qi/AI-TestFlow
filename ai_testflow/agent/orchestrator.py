from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ..config import TestFlowConfig
from .agents.analysis_agent import run_analysis_agent
from .agents.api_agent import run_api_agent
from .agents.automation_agent import run_automation_agent
from .agents.browser_agent import run_browser_agent
from .agents.bug_agent import run_bug_agent
from .agents.knowledge_agent import run_knowledge_agent
from .agents.prd_agent import run_prd_agent
from .agents.report_agent import run_report_agent
from .agents.requirement_agent import run_requirement_agent
from .agents.test_design_agent import run_test_design_agent
from .llm_client import LlmSettings, OpenAILlmClient
from .runtime import TargetServices


@dataclass(frozen=True)
class AgentRunResult:
    summary: dict[str, Any]
    output_files: dict[str, Path]


def run_agent_workflow(
    config: TestFlowConfig,
    project_root: Path,
    progress: Callable[[str], None] | None = None,
) -> AgentRunResult:
    output_dir = project_root / config.output_dir
    _prepare_output_dir(output_dir, project_root)
    prompts_dir = Path(__file__).parent / "prompts"
    client = OpenAILlmClient(
        LlmSettings(
            provider=config.llm_provider,
            model=config.llm_model,
            api_key_env=config.llm_api_key_env,
            base_url=config.llm_base_url,
            raw_output_dir=output_dir,
            request_timeout_seconds=config.llm_request_timeout_seconds,
            max_retries=config.llm_max_retries,
        )
    )
    _emit(progress, f"LLM provider: {config.llm_provider} | model: {config.llm_model}")
    _emit(progress, f"Input PRD: {config.prd_path}")
    prd_text = (project_root / config.prd_path).read_text(encoding="utf-8")
    workflow_state: dict[str, Any] = {
        "project_name": config.project_name,
        "status": "running",
        "stages": [],
        "source_files_read": [str(config.prd_path)],
        "policy": {
            "first_execution": "live_tools",
            "browser_observation_mode": config.browser_runtime.observation_mode,
            "automation": "passed_execution_traces_only",
        },
    }

    _emit(progress, "[1/10] PRD Agent - analyzing requirements document")
    prd_analysis = run_prd_agent(client, _prompt(prompts_dir, "prd_agent.md"), prd_text)
    _mark_stage(workflow_state, "PRD Agent")

    _emit(progress, "[2/10] Knowledge Agent - retrieving testing heuristics")
    knowledge_context = run_knowledge_agent(
        project_root / config.knowledge_base.path,
        prd_analysis,
        config.knowledge_base.top_k,
    )
    workflow_state["source_files_read"].extend(
        item["source_path"] for item in knowledge_context["selected_items"]
    )
    _mark_stage(workflow_state, "Knowledge Agent")

    _emit(progress, "[3/10] Requirement Agent - breaking down requirements and risks")
    requirement_breakdown = run_requirement_agent(
        client,
        _prompt(prompts_dir, "requirement_agent.md"),
        prd_analysis,
        knowledge_context,
    )
    _mark_stage(workflow_state, "Requirement Agent")

    _emit(progress, "[4/10] Test Design Agent - creating exploratory test charters")
    test_design = run_test_design_agent(
        client,
        _prompt(prompts_dir, "test_design_agent.md"),
        requirement_breakdown,
        knowledge_context,
    )
    _mark_stage(workflow_state, "Test Design Agent")
    all_api_charters = [item for item in test_design["test_charters"] if item["channel"] == "api"]
    all_browser_charters = [item for item in test_design["test_charters"] if item["channel"] == "browser"]
    limit = config.execution_policy.max_charters_per_channel
    api_charters = _select_charters(all_api_charters, limit)
    browser_charters = _select_charters(all_browser_charters, limit)
    selected_api_ids = {item["charter_id"] for item in api_charters}
    selected_browser_ids = {item["charter_id"] for item in browser_charters}
    workflow_state["execution_selection"] = {
        "max_charters_per_channel": limit,
        "api_selected": [item["charter_id"] for item in api_charters],
        "api_not_executed": [item["charter_id"] for item in all_api_charters if item["charter_id"] not in selected_api_ids],
        "browser_selected": [item["charter_id"] for item in browser_charters],
        "browser_not_executed": [
            item["charter_id"]
            for item in all_browser_charters
            if item["charter_id"] not in selected_browser_ids
        ],
    }

    system_context = {
        "business_goal": prd_analysis["business_goal"],
        "interface_scope": prd_analysis["interface_scope"],
        "functional_requirements": prd_analysis["functional_requirements"],
    }
    with TargetServices(config.target_runtime, project_root, output_dir):
        _emit(progress, "[5/10] API Agent - executing live HTTP exploration")
        api_execution = run_api_agent(
            client,
            _prompt(prompts_dir, "api_agent.md"),
            api_charters,
            config.api_runtime,
            system_context=system_context,
            progress=progress,
        )
        _mark_stage(workflow_state, "API Agent")

        _emit(progress, "[6/10] Browser Agent - observing and operating the live browser")
        browser_execution = run_browser_agent(
            client,
            _prompt(prompts_dir, "browser_agent.md"),
            browser_charters,
            config.browser_runtime,
            project_root,
            output_dir,
            system_context=system_context,
            progress=progress,
        )
        _mark_stage(workflow_state, "Browser Agent")

    execution_result = {"api": api_execution, "browser": browser_execution}
    _emit(progress, "[7/10] Analysis Agent - classifying execution results")
    defect_analysis = run_analysis_agent(
        client,
        _prompt(prompts_dir, "analysis_agent.md"),
        requirement_breakdown,
        test_design,
        execution_result,
    )
    defect_analysis = _filter_defects_to_execution_evidence(defect_analysis, execution_result)
    _mark_stage(workflow_state, "Analysis Agent")

    report_context = {
        "prd_analysis": prd_analysis,
        "knowledge_context": knowledge_context,
        "requirements": requirement_breakdown,
        "test_charters": test_design,
        "execution_result": execution_result,
        "defect_analysis": defect_analysis,
    }
    _emit(progress, "[8/10] Report Agent - generating test report")
    test_report = run_report_agent(client, _prompt(prompts_dir, "report_agent.md"), report_context)
    _mark_stage(workflow_state, "Report Agent")

    _emit(progress, "[9/10] Bug Agent - generating evidence-backed bug report")
    bug_report = run_bug_agent(client, _prompt(prompts_dir, "bug_agent.md"), report_context)
    _mark_stage(workflow_state, "Bug Agent")

    _emit(progress, "[10/10] Automation Agent - persisting passed traces as regression scripts")
    automation_manifest = run_automation_agent(
        config.automation,
        api_execution,
        browser_execution,
        config.api_runtime.base_url,
        config.browser_runtime.base_url,
        config.browser_runtime.playwright_cwd,
        project_root,
    )
    _mark_stage(workflow_state, "Automation Agent")

    summary = _build_summary(
        config,
        requirement_breakdown,
        test_design,
        api_execution,
        browser_execution,
        defect_analysis,
        automation_manifest,
        getattr(client, "metrics", {}),
        workflow_state["execution_selection"],
    )
    workflow_state["status"] = summary["status"]
    workflow_state["llm_metrics"] = summary["llm_metrics"]
    output_files = _write_outputs(
        output_dir,
        workflow_state,
        prd_analysis,
        knowledge_context,
        requirement_breakdown,
        test_design,
        api_execution,
        browser_execution,
        execution_result,
        defect_analysis,
        test_report,
        bug_report,
        automation_manifest,
        summary,
    )
    _emit(progress, f"Artifacts written: {config.output_dir}")
    return AgentRunResult(summary=summary, output_files=output_files)


def _prepare_output_dir(output_dir: Path, project_root: Path) -> None:
    resolved_root = project_root.resolve()
    resolved_output = output_dir.resolve()
    if resolved_output == resolved_root or resolved_root not in resolved_output.parents:
        raise ValueError(f"Output directory must be inside the project root: {output_dir}")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def _filter_defects_to_execution_evidence(
    analysis: dict[str, Any], execution_result: dict[str, Any]
) -> dict[str, Any]:
    failed = {
        result["execution_id"]
        for channel in ["api", "browser"]
        for result in execution_result[channel]["results"]
        if result["status"] == "failed"
    }
    product_defects = {
        item["execution_id"]
        for item in analysis.get("classifications", [])
        if item["classification"] == "product_defect"
    }
    defects = [
        defect
        for defect in analysis.get("defects", [])
        if defect["execution_id"] in failed and defect["execution_id"] in product_defects
    ]
    return {
        "status": "has_defects" if defects else "no_product_defects",
        "classifications": analysis.get("classifications", []),
        "defects": defects,
    }


def _build_summary(
    config: TestFlowConfig,
    requirements: dict[str, Any],
    test_design: dict[str, Any],
    api_execution: dict[str, Any],
    browser_execution: dict[str, Any],
    defect_analysis: dict[str, Any],
    automation_manifest: dict[str, Any],
    llm_metrics: dict[str, Any],
    execution_selection: dict[str, Any],
) -> dict[str, Any]:
    api_counts = _status_counts(api_execution["results"])
    browser_counts = _status_counts(browser_execution["results"])
    defects = defect_analysis["defects"]
    if defects:
        status = "defects_found"
    elif api_counts["blocked"] or browser_counts["blocked"]:
        status = "execution_blocked"
    else:
        status = "passed"
    return {
        "project_name": config.project_name,
        "status": status,
        "requirements_count": len(requirements["requirements"]),
        "test_points_count": len(requirements["test_points"]),
        "test_charters_count": len(test_design["test_charters"]),
        "api": api_counts,
        "browser": browser_counts,
        "defects": defects,
        "automation_status": automation_manifest["status"],
        "automated_charters_count": len(automation_manifest["generated_charters"]),
        "llm_metrics": llm_metrics,
        "execution_selection": execution_selection,
        "output_dir": str(config.output_dir),
    }


def _status_counts(results: list[dict[str, Any]]) -> dict[str, int]:
    return {
        status: sum(1 for result in results if result["status"] == status)
        for status in ["passed", "failed", "blocked"]
    }


def _select_charters(charters: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    invalid = sorted({str(item.get("priority")) for item in charters if item.get("priority") not in priority_order})
    if invalid:
        raise ValueError(f"Unsupported test charter priorities: {', '.join(invalid)}")
    requirement_order: list[str] = []
    grouped: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, charter in enumerate(charters):
        requirement_id = charter["requirement_id"]
        if requirement_id not in grouped:
            requirement_order.append(requirement_id)
            grouped[requirement_id] = []
        grouped[requirement_id].append((index, charter))
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    for requirement_id in requirement_order:
        _, charter = min(
            grouped[requirement_id],
            key=lambda entry: (priority_order[entry[1]["priority"]], entry[0]),
        )
        selected.append(charter)
        selected_ids.add(charter["charter_id"])
        if len(selected) == limit:
            return selected
    remaining = sorted(
        (
            (index, charter)
            for entries in grouped.values()
            for index, charter in entries
            if charter["charter_id"] not in selected_ids
        ),
        key=lambda entry: (priority_order[entry[1]["priority"]], entry[0]),
    )
    for _, charter in remaining:
        selected.append(charter)
        if len(selected) == limit:
            break
    return selected


def _write_outputs(
    output_dir: Path,
    workflow_state: dict[str, Any],
    prd_analysis: dict[str, Any],
    knowledge_context: dict[str, Any],
    requirement_breakdown: dict[str, Any],
    test_design: dict[str, Any],
    api_execution: dict[str, Any],
    browser_execution: dict[str, Any],
    execution_result: dict[str, Any],
    defect_analysis: dict[str, Any],
    test_report: str,
    bug_report: str,
    automation_manifest: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Path]:
    files = {
        "workflow_state": output_dir / "workflow-state.json",
        "inspection_summary": output_dir / "inspection-summary.json",
        "prd_analysis": output_dir / "prd-analysis.json",
        "knowledge_context": output_dir / "knowledge-context.json",
        "requirements": output_dir / "requirements.json",
        "test_points": output_dir / "test-points.json",
        "test_charters": output_dir / "test-charters.json",
        "api_actions": output_dir / "api-action-log.jsonl",
        "api_observations": output_dir / "api-observations.jsonl",
        "api_execution": output_dir / "api-execution-result.json",
        "browser_actions": output_dir / "browser-action-log.jsonl",
        "browser_observations": output_dir / "browser-observations.jsonl",
        "browser_execution": output_dir / "browser-execution-result.json",
        "execution_result": output_dir / "execution-result.json",
        "defect_analysis": output_dir / "defect-analysis.json",
        "test_report": output_dir / "generated-test-report.md",
        "bug_report": output_dir / "generated-bug-report.md",
        "automation_manifest": output_dir / "automation-manifest.json",
    }
    files["workflow_state"].write_text(_json(workflow_state), encoding="utf-8")
    files["inspection_summary"].write_text(_json(summary), encoding="utf-8")
    files["prd_analysis"].write_text(_json(prd_analysis), encoding="utf-8")
    files["knowledge_context"].write_text(_json(knowledge_context), encoding="utf-8")
    files["requirements"].write_text(_json(requirement_breakdown["requirements"]), encoding="utf-8")
    files["test_points"].write_text(_json(requirement_breakdown["test_points"]), encoding="utf-8")
    files["test_charters"].write_text(_json(test_design["test_charters"]), encoding="utf-8")
    files["api_actions"].write_text(_jsonl(api_execution["actions"]), encoding="utf-8")
    files["api_observations"].write_text(_jsonl(api_execution["observations"]), encoding="utf-8")
    files["api_execution"].write_text(_json(api_execution), encoding="utf-8")
    files["browser_actions"].write_text(_jsonl(browser_execution["actions"]), encoding="utf-8")
    files["browser_observations"].write_text(_jsonl(browser_execution["observations"]), encoding="utf-8")
    files["browser_execution"].write_text(_json(browser_execution), encoding="utf-8")
    files["execution_result"].write_text(_json(execution_result), encoding="utf-8")
    files["defect_analysis"].write_text(_json(defect_analysis), encoding="utf-8")
    files["test_report"].write_text(test_report, encoding="utf-8")
    files["bug_report"].write_text(bug_report, encoding="utf-8")
    files["automation_manifest"].write_text(_json(automation_manifest), encoding="utf-8")
    return files


def _emit(progress: Callable[[str], None] | None, message: str) -> None:
    if progress:
        progress(message)


def _prompt(prompts_dir: Path, name: str) -> str:
    return (prompts_dir / name).read_text(encoding="utf-8")


def _mark_stage(workflow_state: dict[str, Any], stage: str) -> None:
    workflow_state["stages"].append({"stage": stage, "status": "completed"})


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def _jsonl(items: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in items)
