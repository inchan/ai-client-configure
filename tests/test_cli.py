"""Tests for ai_client_configure.cli."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from ai_client_configure import cli
from ai_client_configure.config import ClientConfiguration, dump_configuration


@pytest.fixture()
def config_path(tmp_path: Path) -> Path:
    return tmp_path / "config.json"


def _namespace(**kwargs: object) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def test_handle_init_creates_file(config_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    args = _namespace(config=config_path, force=False)

    exit_code = cli.handle_init(args)

    assert exit_code == 0
    assert config_path.exists()
    message = capsys.readouterr().out
    assert "Created configuration file" in message


def test_handle_init_requires_force(config_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    config_path.write_text("existing")
    args = _namespace(config=config_path, force=False)

    exit_code = cli.handle_init(args)

    assert exit_code == 1
    error = capsys.readouterr().err
    assert "Use --force" in error


def test_handle_init_overwrites_with_force(
    config_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config_path.write_text("existing")
    args = _namespace(config=config_path, force=True)

    exit_code = cli.handle_init(args)

    assert exit_code == 0
    assert json.loads(config_path.read_text())["model"] == "gpt-4.1-mini"
    capsys.readouterr()  # flush output to keep captures in sync


def test_handle_validate_success(
    config_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dump_configuration(ClientConfiguration(model="gpt-4.1-mini"), config_path)
    args = _namespace(config=config_path)

    exit_code = cli.handle_validate(args)

    assert exit_code == 0
    assert "is valid" in capsys.readouterr().out


def test_handle_validate_failure(
    config_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config_path.write_text("not json")
    args = _namespace(config=config_path)

    exit_code = cli.handle_validate(args)

    assert exit_code == 1
    assert "not valid JSON" in capsys.readouterr().err


def test_handle_show_summary(
    config_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dump_configuration(
        ClientConfiguration(model="gpt-4.1-mini", extras={"timeout": 5}),
        config_path,
    )
    args = _namespace(config=config_path, as_json=False)

    exit_code = cli.handle_show(args)

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Model" in output
    assert "Extras" in output


def test_handle_show_json(
    config_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dump_configuration(ClientConfiguration(model="gpt-4.1-mini"), config_path)
    args = _namespace(config=config_path, as_json=True)

    exit_code = cli.handle_show(args)

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["model"] == "gpt-4.1-mini"


def test_handle_show_error(config_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    config_path.write_text("not json")
    args = _namespace(config=config_path, as_json=False)

    exit_code = cli.handle_show(args)

    assert exit_code == 1
    assert "not valid JSON" in capsys.readouterr().err


def test_format_summary_includes_all_fields() -> None:
    config = ClientConfiguration(
        model="gpt-4o",
        temperature=0.2,
        max_output_tokens=2048,
        top_p=0.9,
        endpoint="https://example.com",
        api_key_env="API_KEY",
        extras={"timeout": 10},
    )

    summary = cli._format_summary(config)

    assert "Model" in summary
    assert "timeout" in summary


def test_dispatch_invokes_subcommand(monkeypatch: pytest.MonkeyPatch) -> None:
    recorded: dict[str, argparse.Namespace] = {}

    def fake_init(args: argparse.Namespace) -> int:
        recorded["args"] = args
        return 0

    monkeypatch.setattr(cli, "handle_init", fake_init)

    exit_code = cli.dispatch(["init"])

    assert exit_code == 0
    assert isinstance(recorded["args"].config, Path)


def test_main_exits_with_dispatch_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "dispatch", lambda argv=None: 5)

    exit_calls: list[int] = []

    def fake_exit(code: int) -> None:
        exit_calls.append(code)
        raise SystemExit(code)

    monkeypatch.setattr(cli.sys, "exit", fake_exit)

    with pytest.raises(SystemExit):
        cli.main([])

    assert exit_calls == [5]

