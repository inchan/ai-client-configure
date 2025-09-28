"""Command line entry point for ai-client-configure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import ClientConfiguration, ConfigError, dump_configuration, load_configuration

DEFAULT_CONFIG_PATH = Path("ai_client_config.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-client-configure",
        description="Manage configuration files for AI chat clients.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the configuration file (default: ai_client_config.json)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init",
        help="Create a new configuration file with default values.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the file if it already exists.",
    )
    init_parser.set_defaults(func=handle_init)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate the configuration file and report any issues.",
    )
    validate_parser.set_defaults(func=handle_validate)

    show_parser = subparsers.add_parser(
        "show",
        help="Display the configuration in a human readable form.",
    )
    show_parser.add_argument(
        "--as-json",
        action="store_true",
        help="Print the configuration as JSON instead of a summary table.",
    )
    show_parser.set_defaults(func=handle_show)

    return parser


def handle_init(args: argparse.Namespace) -> int:
    config_path: Path = args.config
    if config_path.exists() and not args.force:
        print(
            f"Configuration file {config_path} already exists. Use --force to overwrite.",
            file=sys.stderr,
        )
        return 1

    default_config = ClientConfiguration(model="gpt-4.1-mini")
    dump_configuration(default_config, config_path)
    print(f"Created configuration file at {config_path}")
    return 0


def handle_validate(args: argparse.Namespace) -> int:
    try:
        load_configuration(args.config)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Configuration {args.config} is valid.")
    return 0


def _format_summary(config: ClientConfiguration) -> str:
    rows = [
        ("Model", config.model),
        ("Temperature", f"{config.temperature:.2f}"),
        ("Max tokens", str(config.max_output_tokens)),
        ("Top-p", f"{config.top_p:.2f}"),
        ("Endpoint", config.endpoint),
        ("API key env", config.api_key_env),
    ]
    if config.extras:
        rows.append(("Extras", json.dumps(config.extras, indent=2)))

    label_width = max(len(label) for label, _ in rows)
    lines = [f"{label:<{label_width}} : {value}" for label, value in rows]
    return "\n".join(lines)


def handle_show(args: argparse.Namespace) -> int:
    try:
        config = load_configuration(args.config)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(config.to_dict(), indent=2, sort_keys=True))
    else:
        print(_format_summary(config))
    return 0


def dispatch(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def main(argv: list[str] | None = None) -> None:
    sys.exit(dispatch(argv))


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
