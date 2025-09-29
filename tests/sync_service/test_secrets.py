from __future__ import annotations

from typing import Dict, Tuple

import keyring
import pytest
from keyring.backend import KeyringBackend
from keyring.errors import PasswordDeleteError

from sync_service.config import Settings
from sync_service.secrets import (
    SecretManager,
    SecretNotFoundError,
    get_manager,
    main,
    resolve_key,
)


class InMemoryKeyring(KeyringBackend):
    """간단한 keyring 백엔드 (테스트용)."""

    priority = 1

    def __init__(self) -> None:
        self._values: Dict[Tuple[str, str], str] = {}

    def get_password(self, service: str, username: str) -> str | None:
        return self._values.get((service, username))

    def set_password(self, service: str, username: str, password: str) -> None:
        self._values[(service, username)] = password

    def delete_password(self, service: str, username: str) -> None:
        try:
            del self._values[(service, username)]
        except KeyError as exc:
            raise PasswordDeleteError("Secret not found") from exc


@pytest.fixture(autouse=True)
def patch_keyring() -> InMemoryKeyring:
    backend = InMemoryKeyring()
    keyring.set_keyring(backend)
    return backend


def test_secret_manager_set_get_delete() -> None:
    manager = SecretManager(service_name="test")
    manager.set_secret("token", "abc")
    assert manager.get_secret("token") == "abc"

    manager.delete_secret("token")
    assert manager.get_secret("token") is None

    with pytest.raises(SecretNotFoundError):
        manager.delete_secret("token")


def test_secret_manager_require() -> None:
    manager = SecretManager(service_name="svc")
    manager.set_secret("k1", "v1")
    manager.set_secret("k2", "v2")

    assert manager.require(["k1", "k2"]) == {"k1": "v1", "k2": "v2"}


def test_secret_manager_require_missing() -> None:
    manager = SecretManager(service_name="svc")
    manager.set_secret("k1", "v1")

    with pytest.raises(SecretNotFoundError) as exc:
        manager.require(["k1", "k2"])

    assert "k2" in str(exc.value)


def test_resolve_key_uses_alias() -> None:
    settings = Settings()
    assert resolve_key(settings, "api-token") == settings.api_token_key
    assert resolve_key(settings, "custom") == "custom"


def test_get_manager_uses_settings() -> None:
    settings = Settings(secret_service_name="custom")
    manager = get_manager(settings)
    assert manager.service_name == "custom"


def test_cli_set_and_get(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["set", "api-token", "--value", "secret-value"]) == 0
    captured = capsys.readouterr()
    assert "Stored secret" in captured.out

    assert main(["get", "api-token", "--reveal"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "secret-value"


def test_cli_check_reports_missing(capsys: pytest.CaptureFixture[str]) -> None:
    # Only set one of the required secrets
    main(["set", "api-token", "--value", "value"])  # ensure success
    capsys.readouterr()

    exit_code = main(["check"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Missing secrets" in captured.err


def test_cli_delete_missing(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["delete", "api-token"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "not found" in captured.err
