from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
    api_execution_report_path: Path
    test_report_path: Path
    bug_report_path: Path
    output_dir: Path


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
    "api_execution_report_path",
    "test_report_path",
    "bug_report_path",
    "output_dir",
}


def load_config(config_path: str | Path = "ai-testflow.yml") -> TestFlowConfig:
    path = Path(config_path)
    raw = _parse_simple_yaml(path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_KEYS - set(raw))
    if missing:
        raise ValueError(f"Missing config keys: {', '.join(missing)}")

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
        api_execution_report_path=Path(str(raw["api_execution_report_path"])),
        test_report_path=Path(str(raw["test_report_path"])),
        bug_report_path=Path(str(raw["bug_report_path"])),
        output_dir=Path(str(raw["output_dir"])),
    )


def _parse_simple_yaml(text: str) -> dict[str, str | list[str]]:
    data: dict[str, str | list[str]] = {}
    current_list_key: str | None = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        if line.startswith("  - "):
            if current_list_key is None:
                raise ValueError(f"List item without key at line {line_number}")
            value = line[4:]
            existing = data[current_list_key]
            if not isinstance(existing, list):
                raise ValueError(f"Key {current_list_key} is not a list")
            existing.append(value)
            continue

        if ":" not in line:
            raise ValueError(f"Invalid config line {line_number}: {line}")

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Empty config key at line {line_number}")

        if value:
            data[key] = value
            current_list_key = None
        else:
            data[key] = []
            current_list_key = key

    return data
