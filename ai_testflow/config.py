from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class TestFlowConfig:
    project_name: str
    prd_path: Path
    requirement_spec_path: Path
    test_cases_path: Path
    backend_source_path: Path
    pytest_path: Path
    pytest_command: list[str]
    generated_tests_path: Path
    generated_pytest_command: list[str]
    generated_playwright_tests_path: Path
    playwright_command: list[str] | None
    api_execution_report_path: Path
    test_report_path: Path
    bug_report_path: Path
    output_dir: Path
    llm_provider: str
    llm_model: str
    llm_api_key_env: str
    llm_base_url: str | None
    api_test_runtime: dict[str, str]


REQUIRED_KEYS = {
    "project_name",
    "prd_path",
    "requirement_spec_path",
    "test_cases_path",
    "backend_source_path",
    "pytest_path",
    "pytest_command",
    "generated_tests_path",
    "generated_pytest_command",
    "generated_playwright_tests_path",
    "api_execution_report_path",
    "test_report_path",
    "bug_report_path",
    "output_dir",
}


def load_config(config_path: str | Path = "ai-testflow.yml") -> TestFlowConfig:
    path = Path(config_path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Config root must be a mapping")
    missing = sorted(REQUIRED_KEYS - set(raw))
    if missing:
        raise ValueError(f"Missing config keys: {', '.join(missing)}")
    llm = raw.get("llm", {})
    if not isinstance(llm, dict):
        raise ValueError("Config key llm must be a mapping")
    api_test_runtime = raw.get("api_test_runtime", {"mode": "flask_app", "app_factory": "backend.app:create_app"})
    if not isinstance(api_test_runtime, dict):
        raise ValueError("Config key api_test_runtime must be a mapping")

    return TestFlowConfig(
        project_name=str(raw["project_name"]),
        prd_path=Path(str(raw["prd_path"])),
        requirement_spec_path=Path(str(raw["requirement_spec_path"])),
        test_cases_path=Path(str(raw["test_cases_path"])),
        backend_source_path=Path(str(raw["backend_source_path"])),
        pytest_path=Path(str(raw["pytest_path"])),
        pytest_command=[str(item) for item in raw["pytest_command"]],
        generated_tests_path=Path(str(raw["generated_tests_path"])),
        generated_pytest_command=[str(item) for item in raw["generated_pytest_command"]],
        generated_playwright_tests_path=Path(str(raw["generated_playwright_tests_path"])),
        playwright_command=[str(item) for item in raw.get("playwright_command", [])] or None,
        api_execution_report_path=Path(str(raw["api_execution_report_path"])),
        test_report_path=Path(str(raw["test_report_path"])),
        bug_report_path=Path(str(raw["bug_report_path"])),
        output_dir=Path(str(raw["output_dir"])),
        llm_provider=str(llm.get("provider", "deepseek")),
        llm_model=str(llm.get("model", "deepseek-v4-flash")),
        llm_api_key_env=str(llm.get("api_key_env", "DEEPSEEK_API_KEY")),
        llm_base_url=str(llm["base_url"]) if "base_url" in llm else None,
        api_test_runtime={str(key): str(value) for key, value in api_test_runtime.items()},
    )
