from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PytestResult:
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    combined_output: str
    passed_tests: int
    failed_tests: int
    failed_test_names: list[str]


def run_pytest(command: list[str], cwd: Path) -> PytestResult:
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    combined_output = "\n".join(part for part in [completed.stdout, completed.stderr] if part)
    return parse_pytest_result(command, completed.returncode, completed.stdout, completed.stderr, combined_output)


def parse_pytest_result(
    command: list[str],
    exit_code: int,
    stdout: str,
    stderr: str,
    combined_output: str,
) -> PytestResult:
    passed_tests = _extract_count(combined_output, r"(\d+) passed")
    failed_tests = _extract_count(combined_output, r"(\d+) failed")
    failed_test_names = _extract_failed_test_names(combined_output)

    return PytestResult(
        command=command,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        combined_output=combined_output,
        passed_tests=passed_tests,
        failed_tests=failed_tests,
        failed_test_names=failed_test_names,
    )


def _extract_count(text: str, pattern: str) -> int:
    matches = re.findall(pattern, text)
    if not matches:
        return 0
    return int(matches[-1])


def _extract_failed_test_names(text: str) -> list[str]:
    names: list[str] = []
    for match in re.findall(r"FAILED\s+[\w./-]+::([\w_]+)", text):
        if match not in names:
            names.append(match)
    return names

