"""Tests for ai_client_configure.config."""

import json
from pathlib import Path

import pytest

from ai_client_configure.config import (
    ClientConfiguration,
    ConfigError,
    dump_configuration,
    load_configuration,
)


@pytest.fixture()
def tmp_config_path(tmp_path: Path) -> Path:
    return tmp_path / "config.json"


def test_dump_and_load_round_trip(tmp_config_path: Path) -> None:
    config = ClientConfiguration(model="gpt-4.1-mini", temperature=0.5, max_output_tokens=256)
    dump_configuration(config, tmp_config_path)

    loaded = load_configuration(tmp_config_path)
    assert loaded.model == "gpt-4.1-mini"
    assert loaded.temperature == pytest.approx(0.5)
    assert loaded.max_output_tokens == 256


def test_load_configuration_requires_valid_json(tmp_config_path: Path) -> None:
    tmp_config_path.write_text("not json")

    with pytest.raises(ConfigError):
        load_configuration(tmp_config_path)


def test_from_dict_requires_model_key() -> None:
    with pytest.raises(ConfigError) as exc:
        ClientConfiguration.from_dict({})

    assert "`model` is required" in str(exc.value)


def test_from_dict_rejects_empty_model() -> None:
    with pytest.raises(ConfigError) as exc:
        ClientConfiguration.from_dict({"model": "   "})

    assert "`model` cannot be empty" in str(exc.value)


def test_load_configuration_requires_object(tmp_config_path: Path) -> None:
    tmp_config_path.write_text(json.dumps([1, 2, 3]))

    with pytest.raises(ConfigError):
        load_configuration(tmp_config_path)


def test_load_configuration_missing_file(tmp_config_path: Path) -> None:
    missing_path = tmp_config_path

    with pytest.raises(ConfigError):
        load_configuration(missing_path)


def test_validation_rejects_unknown_model() -> None:
    with pytest.raises(ConfigError):
        ClientConfiguration.from_dict({"model": "unknown"})


def test_validation_enforces_temperature_range() -> None:
    with pytest.raises(ConfigError):
        ClientConfiguration.from_dict({"model": "gpt-4.1-mini", "temperature": 10})


@pytest.mark.parametrize(
    "key,value,error",
    [
        ("max_output_tokens", 0, "`max_output_tokens` must be positive."),
        ("top_p", 2, "`top_p` must be between 0 (exclusive) and 1 (inclusive)."),
        ("endpoint", "", "`endpoint` cannot be empty."),
        ("api_key_env", "", "`api_key_env` cannot be empty."),
    ],
)
def test_validation_various_error_paths(key: str, value: object, error: str) -> None:
    data = {"model": "gpt-4.1-mini", key: value}

    with pytest.raises(ConfigError) as exc:
        ClientConfiguration.from_dict(data)

    assert error in str(exc.value)


def test_validation_reports_coercion_errors() -> None:
    with pytest.raises(ConfigError) as exc:
        ClientConfiguration.from_dict({"model": "gpt-4.1-mini", "temperature": "hot"})

    assert "must be a number" in str(exc.value)

    with pytest.raises(ConfigError) as exc:
        ClientConfiguration.from_dict({"model": "gpt-4.1-mini", "max_output_tokens": "many"})

    assert "must be an integer" in str(exc.value)


def test_show_includes_extras(tmp_config_path: Path) -> None:
    config = ClientConfiguration(model="gpt-4.1-mini", extras={"timeout": 30})
    dump_configuration(config, tmp_config_path)

    data = json.loads(tmp_config_path.read_text())
    assert data["timeout"] == 30


def test_to_dict_includes_standard_fields() -> None:
    config = ClientConfiguration(model="gpt-4.1-mini", temperature=0.3, extras={"timeout": 5})

    payload = config.to_dict()

    assert payload["model"] == "gpt-4.1-mini"
    assert payload["temperature"] == pytest.approx(0.3)
    assert payload["timeout"] == 5
