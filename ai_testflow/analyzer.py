from __future__ import annotations

import re
from typing import Any


def analyze_prd(prd_text: str) -> dict[str, Any]:
    return {
        "functional_requirements": _extract_prd_sections(prd_text, "PRD-FR-"),
        "non_functional_requirements": _extract_prd_sections(prd_text, "PRD-NFR-"),
        "interfaces": _extract_interface_rows(prd_text),
    }


def extract_requirement_rows(requirement_spec: str) -> list[dict[str, str]]:
    requirements: list[dict[str, str]] = []
    for line in requirement_spec.splitlines():
        cells = markdown_cells(line)
        if len(cells) == 4 and cells[0].startswith("PRD-"):
            requirements.append(
                {
                    "requirement_id": cells[0],
                    "module_id": cells[1],
                    "description": cells[2],
                    "test_focus": cells[3],
                }
            )
    return requirements


def extract_test_case_rows(test_cases_doc: str) -> list[dict[str, str]]:
    test_cases: list[dict[str, str]] = []
    for line in test_cases_doc.splitlines():
        cells = markdown_cells(line)
        if len(cells) == 7 and cells[0].startswith("TC-"):
            test_cases.append(
                {
                    "test_case_id": cells[0],
                    "requirement_id": cells[1],
                    "title": cells[2],
                    "precondition": cells[3],
                    "test_data": cells[4],
                    "expected_result": cells[5],
                    "priority": cells[6],
                }
            )
    return test_cases


def build_requirements(prd_analysis: dict[str, Any], requirement_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    spec_by_id = {item["requirement_id"]: item for item in requirement_rows}
    requirements: list[dict[str, str]] = []
    for item in prd_analysis["functional_requirements"]:
        spec = spec_by_id.get(item["requirement_id"], {})
        requirements.append(
            {
                "requirement_id": item["requirement_id"],
                "title": item["title"],
                "description": item["description"],
                "module_id": spec.get("module_id", ""),
                "test_focus": spec.get("test_focus", ""),
                "source": "docs/prd.md",
            }
        )
    return requirements


def markdown_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _extract_prd_sections(prd_text: str, prefix: str) -> list[dict[str, str]]:
    pattern = re.compile(rf"^###\s+({re.escape(prefix)}[0-9]+)\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(prd_text))
    items: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(prd_text)
        body = prd_text[start:end].strip()
        description = _first_nonempty_line(body)
        items.append(
            {
                "requirement_id": match.group(1),
                "title": match.group(2).strip(),
                "description": description,
            }
        )
    return items


def _extract_interface_rows(prd_text: str) -> list[dict[str, str]]:
    interfaces: list[dict[str, str]] = []
    for line in prd_text.splitlines():
        cells = markdown_cells(line)
        if len(cells) == 3 and cells[0].startswith("`/api/"):
            interfaces.append({"path": cells[0].strip("`"), "method": cells[1], "description": cells[2]})
    return interfaces


def _first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("###"):
            return stripped
    return ""
