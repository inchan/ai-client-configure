"""Keyring 기반 비밀 관리 및 CLI 유틸리티."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from getpass import getpass
from typing import Iterable, Sequence

import keyring
from keyring.errors import KeyringError, PasswordDeleteError

from .config import Settings, get_settings

_PRESET_KEY_ALIASES: dict[str, str] = {
    "api-token": "api_token_key",
    "admin-password": "admin_password_key",
}


class SecretStoreError(RuntimeError):
    """Keyring 연동 중 발생한 일반적인 오류."""


class SecretNotFoundError(SecretStoreError):
    """요청한 비밀이 존재하지 않을 때 발생."""


@dataclass
class SecretManager:
    """Keyring을 통해 동기화 서비스 비밀을 관리한다."""

    service_name: str

    def set_secret(self, key: str, value: str) -> None:
        """keyring에 비밀을 저장한다."""

        try:
            keyring.set_password(self.service_name, key, value)
        except KeyringError as exc:  # pragma: no cover - keyring backend failure
            raise SecretStoreError("Failed to store secret") from exc

    def get_secret(self, key: str, *, raise_if_missing: bool = False) -> str | None:
        """비밀을 조회한다. 없으면 None 또는 예외를 반환한다."""

        try:
            value = keyring.get_password(self.service_name, key)
        except KeyringError as exc:  # pragma: no cover - keyring backend failure
            raise SecretStoreError("Failed to load secret") from exc

        if value is None and raise_if_missing:
            raise SecretNotFoundError(f"Secret '{key}' not found")
        return value

    def delete_secret(self, key: str, *, missing_ok: bool = False) -> None:
        """keyring에서 비밀을 삭제한다."""

        try:
            keyring.delete_password(self.service_name, key)
        except PasswordDeleteError:
            if missing_ok:
                return
            raise SecretNotFoundError(f"Secret '{key}' not found") from None
        except KeyringError as exc:  # pragma: no cover - keyring backend failure
            raise SecretStoreError("Failed to delete secret") from exc

    def require(self, keys: Iterable[str]) -> dict[str, str]:
        """필수 비밀이 모두 존재하는지 확인하고 반환한다."""

        missing: list[str] = []
        resolved: dict[str, str] = {}
        for key in keys:
            value = self.get_secret(key)
            if value is None:
                missing.append(key)
            else:
                resolved[key] = value

        if missing:
            missing_csv = ", ".join(sorted(missing))
            raise SecretNotFoundError(f"Missing secrets: {missing_csv}")
        return resolved


def resolve_key(settings: Settings, identifier: str) -> str:
    """프리셋 별칭을 실제 keyring 키로 변환한다."""

    attr = _PRESET_KEY_ALIASES.get(identifier)
    if attr is None:
        return identifier
    return getattr(settings, attr)


def get_manager(settings: Settings | None = None) -> SecretManager:
    """설정에서 Keyring 서비스 이름을 읽어 SecretManager를 생성한다."""

    settings = settings or get_settings()
    return SecretManager(service_name=settings.secret_service_name)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage keyring-backed secrets for the sync service.",
    )
    parser.add_argument(
        "--service-name",
        default=None,
        help="Override the keyring service name (defaults to settings value).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    set_parser = subparsers.add_parser("set", help="Store or update a secret.")
    set_parser.add_argument("key", help="Key alias or raw key name.")
    set_parser.add_argument(
        "--value",
        help="Secret value (prompted securely when omitted).",
    )

    get_parser = subparsers.add_parser("get", help="Check or display a secret.")
    get_parser.add_argument("key", help="Key alias or raw key name.")
    get_parser.add_argument(
        "--reveal",
        action="store_true",
        help="Print the secret value instead of a status message.",
    )

    delete_parser = subparsers.add_parser("delete", help="Remove a stored secret.")
    delete_parser.add_argument("key", help="Key alias or raw key name.")

    check_parser = subparsers.add_parser("check", help="Verify that secrets exist.")
    check_parser.add_argument(
        "keys",
        nargs="*",
        help=(
            "Keys or aliases to verify. Defaults to preset api-token and admin-password"
        ),
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI 진입점."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    settings = get_settings()
    if args.service_name:
        manager = SecretManager(service_name=args.service_name)
    else:
        manager = get_manager(settings)

    if args.command == "set":
        key = resolve_key(settings, args.key)
        value = args.value or getpass(f"Enter secret for '{key}': ")
        manager.set_secret(key, value)
        print(f"Stored secret for '{key}' in service '{manager.service_name}'.")
        return 0

    if args.command == "get":
        key = resolve_key(settings, args.key)
        value = manager.get_secret(key)
        if value is None:
            print(f"Secret '{key}' is not set.", file=sys.stderr)
            return 1
        if args.reveal:
            print(value)
        else:
            print(f"Secret '{key}' is set.")
        return 0

    if args.command == "delete":
        key = resolve_key(settings, args.key)
        try:
            manager.delete_secret(key)
        except SecretNotFoundError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Deleted secret '{key}'.")
        return 0

    if args.command == "check":
        identifiers = args.keys or [settings.api_token_key, settings.admin_password_key]
        keys = [resolve_key(settings, identifier) for identifier in identifiers]
        try:
            manager.require(keys)
        except SecretNotFoundError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print("All requested secrets are set.")
        return 0

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
