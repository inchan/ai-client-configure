# ai-client-configure

`ai-client-configure` is a lightweight command line utility that helps teams create,
validate, and inspect configuration files for AI chat clients. The tool embraces a
step-by-step workflow documented in `docs/PROJECT_PLAN.md` so contributors can follow
a predictable process when extending the project.

## Features

- Scaffold a default configuration file with sensible defaults.
- Validate configuration files against a strict schema.
- Display configuration details as a summary table or JSON.

## Installation

The project is packaged with a `pyproject.toml` file. You can install it locally in
editable mode while developing:

```bash
pip install -e .
```

Install the optional development dependencies to run linters locally:

```bash
pip install -e .[dev]
```

Alternatively you can execute the CLI directly without installing:

```bash
python -m ai_client_configure --help
```

## Usage

All commands share the `--config` option which defaults to `ai_client_config.json` in
the current directory.

### Initialize a configuration file

```bash
ai-client-configure init
```

Use `--force` to overwrite an existing file.

### Validate a configuration file

```bash
ai-client-configure validate
```

### Show a configuration summary

```bash
ai-client-configure show
```

Pass `--as-json` to view the raw JSON output.

## Development workflow

1. Review the staged approach documented in `docs/PROJECT_PLAN.md`.
2. Run static analysis and the test suite before committing changes:

   ```bash
   ruff check .
   pytest
   ```

3. Update the documentation when adding new CLI commands or configuration options.

## License

MIT
