from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LlmSettings:
    provider: str
    model: str
    api_key_env: str


class OpenAILlmClient:
    def __init__(self, settings: LlmSettings):
        if settings.provider != "openai":
            raise ValueError(f"Unsupported LLM provider: {settings.provider}")
        api_key = os.environ.get(settings.api_key_env)
        if not api_key:
            raise RuntimeError(f"{settings.api_key_env} is required for agent-run")
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            raise RuntimeError("openai package is required for agent-run. Install backend/requirements.txt.") from exc
        self._client = OpenAI(api_key=api_key)
        self._model = settings.model

    def generate_json(self, *, name: str, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        response = self._client.responses.create(
            model=self._model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": name,
                    "schema": schema,
                    "strict": True,
                }
            },
        )
        return json.loads(response.output_text)
