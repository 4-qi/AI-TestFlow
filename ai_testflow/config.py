from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class KnowledgeBaseConfig:
    path: Path
    top_k: int


@dataclass(frozen=True)
class ServiceConfig:
    name: str
    cwd: Path
    command: list[str]
    ready_url: str


@dataclass(frozen=True)
class TargetRuntimeConfig:
    startup_timeout_seconds: float
    services: list[ServiceConfig]


@dataclass(frozen=True)
class ApiRuntimeConfig:
    enabled: bool
    base_url: str
    request_timeout_seconds: float
    max_steps_per_charter: int


@dataclass(frozen=True)
class BrowserRuntimeConfig:
    enabled: bool
    base_url: str
    browser: str
    headless: bool
    observation_mode: str
    max_steps_per_charter: int
    action_timeout_ms: int
    playwright_cwd: Path
    screenshot: str


@dataclass(frozen=True)
class AutomationConfig:
    enabled: bool
    output_dir: Path


@dataclass(frozen=True)
class ExecutionPolicyConfig:
    max_charters_per_channel: int


@dataclass(frozen=True)
class TestFlowConfig:
    project_name: str
    prd_path: Path
    output_dir: Path
    llm_provider: str
    llm_model: str
    llm_api_key_env: str
    llm_base_url: str | None
    llm_request_timeout_seconds: float
    llm_max_retries: int
    knowledge_base: KnowledgeBaseConfig
    target_runtime: TargetRuntimeConfig
    api_runtime: ApiRuntimeConfig
    browser_runtime: BrowserRuntimeConfig
    automation: AutomationConfig
    execution_policy: ExecutionPolicyConfig


REQUIRED_KEYS = {
    "project_name",
    "prd_path",
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
    return TestFlowConfig(
        project_name=str(raw["project_name"]),
        prd_path=Path(str(raw["prd_path"])),
        output_dir=Path(str(raw["output_dir"])),
        llm_provider=str(llm.get("provider", "deepseek")),
        llm_model=str(llm.get("model", "deepseek-v4-pro")),
        llm_api_key_env=str(llm.get("api_key_env", "DEEPSEEK_API_KEY")),
        llm_base_url=str(llm["base_url"]) if "base_url" in llm else None,
        llm_request_timeout_seconds=_positive_float(
            llm.get("request_timeout_seconds", 120), "llm.request_timeout_seconds"
        ),
        llm_max_retries=_non_negative_int(llm.get("max_retries", 1), "llm.max_retries"),
        knowledge_base=_load_knowledge_base(raw.get("knowledge_base")),
        target_runtime=_load_target_runtime(raw.get("target_runtime")),
        api_runtime=_load_api_runtime(raw.get("api_runtime")),
        browser_runtime=_load_browser_runtime(raw.get("browser_runtime")),
        automation=_load_automation(raw.get("automation")),
        execution_policy=_load_execution_policy(raw.get("execution_policy")),
    )


def _mapping(value: Any, key: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Config key {key} must be a mapping")
    return value


def _require(raw: dict[str, Any], key: str, fields: set[str]) -> None:
    missing = sorted(fields - set(raw))
    if missing:
        raise ValueError(f"Missing {key} keys: {', '.join(missing)}")


def _positive_int(value: Any, key: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise ValueError(f"Config key {key} must be greater than 0")
    return parsed


def _positive_float(value: Any, key: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise ValueError(f"Config key {key} must be greater than 0")
    return parsed


def _non_negative_int(value: Any, key: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise ValueError(f"Config key {key} must be greater than or equal to 0")
    return parsed


def _load_knowledge_base(value: Any) -> KnowledgeBaseConfig:
    raw = _mapping(value, "knowledge_base")
    _require(raw, "knowledge_base", {"path", "top_k"})
    return KnowledgeBaseConfig(
        path=Path(str(raw["path"])),
        top_k=_positive_int(raw["top_k"], "knowledge_base.top_k"),
    )


def _load_target_runtime(value: Any) -> TargetRuntimeConfig:
    raw = _mapping(value, "target_runtime")
    _require(raw, "target_runtime", {"startup_timeout_seconds", "services"})
    services_raw = raw["services"]
    if not isinstance(services_raw, list):
        raise ValueError("Config key target_runtime.services must be a list")
    services: list[ServiceConfig] = []
    for index, service_value in enumerate(services_raw):
        service = _mapping(service_value, f"target_runtime.services[{index}]")
        _require(service, f"target_runtime.services[{index}]", {"name", "cwd", "command", "ready_url"})
        command = service["command"]
        if not isinstance(command, list) or not command:
            raise ValueError(f"Config key target_runtime.services[{index}].command must be a non-empty list")
        services.append(
            ServiceConfig(
                name=str(service["name"]),
                cwd=Path(str(service["cwd"])),
                command=[str(item) for item in command],
                ready_url=str(service["ready_url"]),
            )
        )
    return TargetRuntimeConfig(
        startup_timeout_seconds=_positive_float(
            raw["startup_timeout_seconds"], "target_runtime.startup_timeout_seconds"
        ),
        services=services,
    )


def _load_api_runtime(value: Any) -> ApiRuntimeConfig:
    raw = _mapping(value, "api_runtime")
    _require(raw, "api_runtime", {"enabled", "base_url", "request_timeout_seconds", "max_steps_per_charter"})
    if not isinstance(raw["enabled"], bool):
        raise ValueError("Config key api_runtime.enabled must be a boolean")
    return ApiRuntimeConfig(
        enabled=raw["enabled"],
        base_url=str(raw["base_url"]).rstrip("/"),
        request_timeout_seconds=_positive_float(raw["request_timeout_seconds"], "api_runtime.request_timeout_seconds"),
        max_steps_per_charter=_positive_int(raw["max_steps_per_charter"], "api_runtime.max_steps_per_charter"),
    )


def _load_browser_runtime(value: Any) -> BrowserRuntimeConfig:
    raw = _mapping(value, "browser_runtime")
    _require(
        raw,
        "browser_runtime",
        {
            "enabled",
            "base_url",
            "browser",
            "headless",
            "observation_mode",
            "max_steps_per_charter",
            "action_timeout_ms",
            "playwright_cwd",
            "screenshot",
        },
    )
    if not isinstance(raw["enabled"], bool) or not isinstance(raw["headless"], bool):
        raise ValueError("Config keys browser_runtime.enabled and browser_runtime.headless must be booleans")
    browser = str(raw["browser"])
    if browser not in {"chromium", "firefox", "webkit"}:
        raise ValueError("Config key browser_runtime.browser must be chromium, firefox, or webkit")
    observation_mode = str(raw["observation_mode"])
    if observation_mode != "structured":
        raise ValueError("Only browser_runtime.observation_mode=structured is implemented")
    screenshot = str(raw["screenshot"])
    if screenshot not in {"always", "on_finish", "off"}:
        raise ValueError("Config key browser_runtime.screenshot must be always, on_finish, or off")
    return BrowserRuntimeConfig(
        enabled=raw["enabled"],
        base_url=str(raw["base_url"]).rstrip("/"),
        browser=browser,
        headless=raw["headless"],
        observation_mode=observation_mode,
        max_steps_per_charter=_positive_int(
            raw["max_steps_per_charter"], "browser_runtime.max_steps_per_charter"
        ),
        action_timeout_ms=_positive_int(raw["action_timeout_ms"], "browser_runtime.action_timeout_ms"),
        playwright_cwd=Path(str(raw["playwright_cwd"])),
        screenshot=screenshot,
    )


def _load_automation(value: Any) -> AutomationConfig:
    raw = _mapping(value, "automation")
    _require(raw, "automation", {"enabled", "output_dir"})
    if not isinstance(raw["enabled"], bool):
        raise ValueError("Config key automation.enabled must be a boolean")
    return AutomationConfig(enabled=raw["enabled"], output_dir=Path(str(raw["output_dir"])))


def _load_execution_policy(value: Any) -> ExecutionPolicyConfig:
    raw = _mapping(value, "execution_policy")
    _require(raw, "execution_policy", {"max_charters_per_channel"})
    return ExecutionPolicyConfig(
        max_charters_per_channel=_positive_int(
            raw["max_charters_per_channel"], "execution_policy.max_charters_per_channel"
        )
    )
