from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LlmSettings:
    provider: str
    model: str
    api_key_env: str
    base_url: str | None = None
    raw_output_dir: Path | None = None
    request_timeout_seconds: float = 120
    max_retries: int = 1


class LlmJsonParseError(ValueError):
    def __init__(self, name: str, error: json.JSONDecodeError, raw_path: Path | None):
        self.name = name
        self.raw_path = raw_path
        location = f"line {error.lineno} column {error.colno} char {error.pos}"
        message = f"{name} returned invalid JSON at {location}: {error.msg}"
        if raw_path:
            message += f". Raw output saved to {raw_path}"
        super().__init__(message)


class OpenAILlmClient:
    def __init__(self, settings: LlmSettings):
        if settings.provider not in {"openai", "deepseek"}:
            raise ValueError(f"Unsupported LLM provider: {settings.provider}")
        load_env_file(Path(".env"))
        api_key = os.environ.get(settings.api_key_env)
        if not api_key:
            raise RuntimeError(f"{settings.api_key_env} is required for agent-run")
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            raise RuntimeError("openai package is required for agent-run. Install backend/requirements.txt.") from exc
        base_url = settings.base_url or ("https://api.deepseek.com" if settings.provider == "deepseek" else None)
        client_options = {
            "api_key": api_key,
            "timeout": settings.request_timeout_seconds,
            "max_retries": settings.max_retries,
        }
        if base_url:
            client_options["base_url"] = base_url
        self._client = OpenAI(**client_options)
        self._provider = settings.provider
        self._model = settings.model
        self._raw_output_dir = settings.raw_output_dir
        self._call_count = 0

    @property
    def metrics(self) -> dict[str, int]:
        return {"llm_calls": self._call_count}

    def generate_json(self, *, name: str, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        self._call_count += 1
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
        return self._parse_json_response(name, response.output_text)

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
        try:
            return self._parse_json_response(name, content)
        except LlmJsonParseError as first_error:
            repaired = self._repair_deepseek_json(
                name=name,
                invalid_content=content,
                parse_error=str(first_error),
                schema=schema,
            )
            return self._parse_json_response(name, repaired)

    def _parse_json_response(self, name: str, content: str) -> dict[str, Any]:
        try:
            return _unwrap_named_object(name, json.loads(content))
        except json.JSONDecodeError as exc:
            raw_path = _write_raw_llm_output(self._raw_output_dir, name, content)
            raise LlmJsonParseError(name, exc, raw_path) from exc

    def _repair_deepseek_json(self, *, name: str, invalid_content: str, parse_error: str, schema: dict[str, Any]) -> str:
        self._call_count += 1
        schema_text = json.dumps(schema, ensure_ascii=False, indent=2)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You repair invalid JSON for an automated testing agent. "
                        "Output valid JSON only. Do not output Markdown. "
                        f"The JSON object name is {name}. "
                        "The JSON must satisfy this JSON Schema:\n"
                        f"{schema_text}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"JSON parse error:\n{parse_error}\n\n"
                        f"Invalid content:\n{invalid_content}\n\n"
                        "请只输出修复后的 json 对象，不要解释。"
                    ),
                },
            ],
            response_format={"type": "json_object"},
            stream=False,
        )
        repaired = response.choices[0].message.content
        if not repaired:
            raise RuntimeError(f"DeepSeek returned empty repaired JSON content for {name}")
        return repaired


def _unwrap_named_object(name: str, data: dict[str, Any]) -> dict[str, Any]:
    if name in data and isinstance(data[name], dict):
        return data[name]
    return data


def _write_raw_llm_output(raw_output_dir: Path | None, name: str, content: str) -> Path | None:
    if raw_output_dir is None:
        return None
    raw_output_dir.mkdir(parents=True, exist_ok=True)
    base_name = f"llm-raw-{_safe_name(name)}"
    path = raw_output_dir / f"{base_name}.txt"
    index = 2
    while path.exists():
        path = raw_output_dir / f"{base_name}-{index}.txt"
        index += 1
    path.write_text(content, encoding="utf-8")
    return path


def _safe_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value).strip("-") or "response"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)
