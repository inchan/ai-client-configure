"""Core configuration dataclasses and helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

SUPPORTED_MODELS = {
    "gpt-4.1-mini",
    "gpt-4o",
    "claude-3-sonnet",
}


def _coerce_float(value: Any, name: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError) as exc:
        raise ConfigError(f"{name} must be a number, received {value!r}") from exc


def _coerce_int(value: Any, name: str) -> int:
    try:
        return int(value)
    except (ValueError, TypeError) as exc:
        raise ConfigError(f"{name} must be an integer, received {value!r}") from exc


class ConfigError(ValueError):
    """Raised when a configuration file cannot be parsed or validated."""


@dataclass(slots=True)
class ClientConfiguration:
    """Represents configuration values for an AI client."""

    model: str
    temperature: float = 0.7
    max_output_tokens: int = 1024
    top_p: float = 0.95
    endpoint: str = "https://api.openai.com/v1/chat/completions"
    api_key_env: str = "OPENAI_API_KEY"
    extras: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the configuration to a dictionary suitable for JSON."""

        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "top_p": self.top_p,
            "endpoint": self.endpoint,
            "api_key_env": self.api_key_env,
        }
        payload.update(self.extras)
        return payload

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "ClientConfiguration":
        """Construct a configuration from a dictionary."""

        if "model" not in raw:
            raise ConfigError("`model` is required in the configuration file.")
        model = str(raw["model"]).strip()
        if not model:
            raise ConfigError("`model` cannot be empty.")
        if SUPPORTED_MODELS and model not in SUPPORTED_MODELS:
            raise ConfigError(
                f"`model` must be one of {sorted(SUPPORTED_MODELS)}, received {model!r}."
            )

        temperature = _coerce_float(raw.get("temperature", 0.7), "temperature")
        if not 0 <= temperature <= 2:
            raise ConfigError("`temperature` must be between 0 and 2.")

        max_output_tokens = _coerce_int(raw.get("max_output_tokens", 1024), "max_output_tokens")
        if max_output_tokens <= 0:
            raise ConfigError("`max_output_tokens` must be positive.")

        top_p = _coerce_float(raw.get("top_p", 0.95), "top_p")
        if not 0 < top_p <= 1:
            raise ConfigError("`top_p` must be between 0 (exclusive) and 1 (inclusive).")

        endpoint = str(raw.get("endpoint", "https://api.openai.com/v1/chat/completions"))
        if not endpoint:
            raise ConfigError("`endpoint` cannot be empty.")

        api_key_env = str(raw.get("api_key_env", "OPENAI_API_KEY"))
        if not api_key_env:
            raise ConfigError("`api_key_env` cannot be empty.")

        extras: Dict[str, Any] = {
            key: value
            for key, value in raw.items()
            if key
            not in {"model", "temperature", "max_output_tokens", "top_p", "endpoint", "api_key_env"}
        }

        return cls(
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            endpoint=endpoint,
            api_key_env=api_key_env,
            extras=extras,
        )


def load_configuration(path: str | Path) -> ClientConfiguration:
    """Load a configuration file from disk."""

    target = Path(path)
    if not target.exists():
        raise ConfigError(f"Configuration file {target} does not exist.")
    try:
        data = json.loads(target.read_text())
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Configuration file {target} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Configuration file must contain a JSON object.")
    return ClientConfiguration.from_dict(data)


def dump_configuration(config: ClientConfiguration, path: str | Path) -> None:
    """Write a configuration to disk as nicely formatted JSON."""

    target = Path(path)
    target.write_text(json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n")
