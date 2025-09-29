# ai-client-configure

`ai-client-configure` is a lightweight command line utility that helps teams create,
validate, and inspect configuration files for AI chat clients. The tool embraces a
step-by-step workflow documented in `docs/PROJECT_PLAN.md` so contributors can follow
a predictable process when extending the project. Stage 6 expands this repository into
the AI Client 동기화 서비스 by adding a FastAPI backend, Redis broker, and supporting
infrastructure defined in the architecture documents.

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

Install the optional development dependencies to run linters and tests locally:

```bash
pip install -e .[dev]
```

To bootstrap the 동기화 서비스 backend stack, run the helper script which prefers
`uv` when available and falls back to `pip`:

```bash
./scripts/dev_setup.sh
```

The script installs the backend optional dependency group defined in
`pyproject.toml` so the FastAPI app, Redis client, and database stack are ready to
use.

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

## 동기화 서비스 개발 환경

Stage 6 introduces a local web service that monitors MCP/Rule/Allowed-tools 구성 파일
변경을 처리할 준비를 합니다. The following commands align with `ENV-01` in the task
sheet:

1. **Install dependencies**

   ```bash
   ./scripts/dev_setup.sh
   ```

2. **Run the FastAPI backend locally**

   ```bash
   uvicorn sync_service.main:app --reload
   ```

3. **Launch via Docker Compose**

   ```bash
   docker compose up --build
   ```

   The compose stack builds the API container and starts Redis Streams so 실시간
   이벤트 전파 실험을 위한 기반이 마련됩니다.

Once the server is running you can verify the health endpoint:

```bash
curl http://localhost:8000/api/v1/health
```

You should receive `{"status": "ok"}`.

## Development workflow

1. Review the staged approach documented in `docs/PROJECT_PLAN.md`.
2. Run static analysis and the test suite before committing changes:

   ```bash
   ruff check .
   pytest
   ```

3. Update the documentation when adding new CLI commands, 동기화 서비스 기능, or
   infrastructure.

## Design documentation

- **Stage 1 연구 자료**: `docs/research/stage1_technical_research.md`에서 클라이언트별 MCP/Rule/Allowed-tools 구조와 동기화 고려사항을 확인할 수 있습니다.
- **아키텍처 & 기술 스택**: `docs/architecture/architecture_and_stack.md`는 추천 아키텍처와 선택한 스택, 요구사항 대응 전략을 설명합니다.
- **상세 설계**: `docs/design/detailed_design.md`는 컴포넌트/데이터 흐름/DB 설계/UI 흐름/동기화 알고리즘을 포함합니다.
- **Task 관리 시트**: `docs/tasks/task_sheet.md`는 워크플로별 세부 Task, 의존성, 테스트 시나리오를 제공합니다.

## License

MIT
