from __future__ import annotations

from typing import Any

from ..llm_client import OpenAILlmClient
from ..schemas import MARKDOWN_DOCUMENT_SCHEMA, validate_required_keys


def run_bug_agent(client: OpenAILlmClient, prompt: str, context: dict[str, Any]) -> str:
    data = client.generate_json(
        name="bug_report",
        system_prompt=prompt,
        user_prompt=f"请生成标准 Bug 单 Markdown。\n\n{context}",
        schema=MARKDOWN_DOCUMENT_SCHEMA,
    )
    validate_required_keys("bug_report", data, MARKDOWN_DOCUMENT_SCHEMA)
    return str(data["markdown"])
