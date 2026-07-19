from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


REQUIRED_KNOWLEDGE_KEYS = {
    "knowledge_id",
    "title",
    "tags",
    "applicable_channels",
    "heuristics",
    "evidence_requirements",
}


def run_knowledge_agent(
    knowledge_dir: Path,
    prd_analysis: dict[str, Any],
    top_k: int,
) -> dict[str, Any]:
    items = load_knowledge_items(knowledge_dir)
    query = json.dumps(prd_analysis, ensure_ascii=False).lower()
    query_terms = _terms(query)
    ranked: list[tuple[int, str, dict[str, Any], list[str]]] = []
    for item in items:
        matched = _matched_terms(item, query, query_terms)
        score = len(matched)
        if score:
            ranked.append((score, str(item["knowledge_id"]), item, matched))
    ranked.sort(key=lambda entry: (-entry[0], entry[1]))
    selected = [
        {**item, "matched_terms": matched}
        for _, _, item, matched in ranked[:top_k]
    ]
    return {
        "knowledge_base_path": str(knowledge_dir),
        "retrieval_method": "tag_and_keyword",
        "selected_items": selected,
    }


def load_knowledge_items(knowledge_dir: Path) -> list[dict[str, Any]]:
    if not knowledge_dir.is_dir():
        raise ValueError(f"Knowledge base directory does not exist: {knowledge_dir}")
    items: list[dict[str, Any]] = []
    for path in sorted(knowledge_dir.glob("*.yml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"Knowledge file root must be a mapping: {path}")
        missing = sorted(REQUIRED_KNOWLEDGE_KEYS - set(raw))
        if missing:
            raise ValueError(f"Knowledge file {path} missing keys: {', '.join(missing)}")
        for key in ["tags", "applicable_channels", "heuristics", "evidence_requirements"]:
            if not isinstance(raw[key], list) or not all(isinstance(value, str) for value in raw[key]):
                raise ValueError(f"Knowledge file {path} key {key} must be a string list")
        items.append({**raw, "source_path": str(path)})
    if not items:
        raise ValueError(f"Knowledge base contains no .yml files: {knowledge_dir}")
    return items


def _matched_terms(item: dict[str, Any], query: str, query_terms: set[str]) -> list[str]:
    values = [str(item["title"]), *[str(tag) for tag in item["tags"]]]
    matched: set[str] = set()
    for value in values:
        normalized = value.strip().lower()
        if not normalized:
            continue
        if normalized in query or normalized in query_terms:
            matched.add(normalized)
    return sorted(matched)


def _terms(value: str) -> set[str]:
    return {term for term in re.split(r"[^0-9a-zA-Z_\u4e00-\u9fff]+", value) if term}
