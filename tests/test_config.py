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


def test_validation_rejects_unknown_model() -> None:
    with pytest.raises(ConfigError):
        ClientConfiguration.from_dict({"model": "unknown"})


def test_validation_enforces_temperature_range() -> None:
    with pytest.raises(ConfigError):
        ClientConfiguration.from_dict({"model": "gpt-4.1-mini", "temperature": 10})


def test_show_includes_extras(tmp_config_path: Path) -> None:
    config = ClientConfiguration(model="gpt-4.1-mini", extras={"timeout": 30})
    dump_configuration(config, tmp_config_path)

    data = json.loads(tmp_config_path.read_text())
    assert data["timeout"] == 30
