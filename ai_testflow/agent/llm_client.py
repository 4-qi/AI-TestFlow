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
    base_url: str | None = None


class OpenAILlmClient:
    def __init__(self, settings: LlmSettings):
        if settings.provider not in {"openai", "deepseek"}:
            raise ValueError(f"Unsupported LLM provider: {settings.provider}")
        api_key = os.environ.get(settings.api_key_env)
        if not api_key:
            raise RuntimeError(f"{settings.api_key_env} is required for agent-run")
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            raise RuntimeError("openai package is required for agent-run. Install backend/requirements.txt.") from exc
        base_url = settings.base_url or ("https://api.deepseek.com" if settings.provider == "deepseek" else None)
        self._client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        self._provider = settings.provider
        self._model = settings.model

    def generate_json(self, *, name: str, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        if self._provider == "deepseek":
            return self._generate_deepseek_json(
                name=name,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema,
            )
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
        return _unwrap_named_object(name, json.loads(response.output_text))

    def _generate_deepseek_json(self, *, name: str, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        schema_text = json.dumps(schema, ensure_ascii=False, indent=2)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"{system_prompt}\n\n"
                        "You must output valid JSON only. "
                        f"The JSON object name is {name}. "
                        "The JSON must satisfy this JSON Schema:\n"
                        f"{schema_text}"
                    ),
                },
                {"role": "user", "content": f"{user_prompt}\n\n请只输出 json 对象，不要输出 Markdown。"},
            ],
            response_format={"type": "json_object"},
            stream=False,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("DeepSeek returned empty JSON content")
        return _unwrap_named_object(name, json.loads(content))


def _unwrap_named_object(name: str, data: dict[str, Any]) -> dict[str, Any]:
    if name in data and isinstance(data[name], dict):
        return data[name]
    return data
