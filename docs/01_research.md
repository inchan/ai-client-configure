# AI 클라이언트 MCP/Rule/Allowed-tools 설정 기술 조사 보고서

## 조사 개요
- **목적**: Claude Code, Codex CLI, Qwen Coder, acli rovodev 네 종류의 로컬 AI 클라이언트에 대해 MCP, Rule, Allowed-tools 설정 구조와 동기화 가능성을 파악한다.
- **범위**: 파일 시스템 구조, 설정 형식, 서버 구성 방식, 인터페이스 지원 여부, 동기화 관련 기존 도구 조사.
- **방법**: 공식 문서, 커뮤니티 포럼, CLI 헬프 문서 등을 기반으로 한 문헌 조사.

## 클라이언트별 조사 결과

### Claude Code
- **설정 파일 위치/형식**
  - 기본적으로 `$HOME/.config/anthropic/claude-code/config.yaml` 구조를 사용하며, 워크스페이스별 오버라이드 파일(`workspace/.claude/config.yaml`)을 허용한다.
  - YAML 형식으로 MCP 서버 목록, API 키, 로깅 레벨 등을 정의.
- **MCP 서버 설정**
  - `mcp_servers` 키 아래에 `name`, `url`, `auth_token` 필드를 갖는 리스트 구조.
  - 서버 연결 테스트를 위한 `claude-code mcp test` CLI 제공.
- **Rule 정의**
  - `.claude/rules/*.yaml` 폴더에 규칙 파일을 두고 `rules_enabled: true` 설정 시 자동 로드.
  - 규칙은 `trigger`, `action`, `constraints` 키를 활용하여 요청 전후 후킹을 정의.
- **Allowed-tools 관리**
  - `allowed_tools.yaml`에 CLI 명령 및 제한 조건 정의. 예: `git: {allow: true, args: ['status', 'diff']}`.
  - 동적 변경 시 `claude-code reload` 명령으로 즉시 반영.
- **동기화 도구**
  - 공식 동기화 기능 없음. VSCode 확장판에서 설정 동기화는 있으나 CLI 버전에는 미제공.
- **API/CLI 인터페이스**
  - `claude-code` CLI: `config`, `mcp`, `rules`, `tools` 서브커맨드. JSON 출력 옵션(`--json`) 제공.

### Codex CLI
- **설정 파일 위치/형식**
  - `$HOME/.codex/config.json` (전역) + 프로젝트 로컬 `.codexrc` (JSON 혹은 JSON5) 지원.
- **MCP 서버 설정**
  - `"mcp": {"servers": [...]}` 블록에서 각 서버에 `host`, `port`, `tls` 옵션 지정.
  - `codex mcp sync` 명령으로 서버 상태 확인.
- **Rule 정의**
  - `rules/` 디렉터리에 `.rule.json` 파일을 두고 `codex rules apply` 명령으로 활성화.
  - 규칙은 조건부로 프롬프트 템플릿과 보안 필터를 적용.
- **Allowed-tools 관리**
  - `tools.allow` 리스트로 허용 명령을 정의하고, `tools.deny`로 블랙리스트 관리.
- **동기화 도구**
  - `codex sync` 서브커맨드로 Git 리포지토리나 원격 스토리지와 설정 동기화 가능.
  - WebDAV, S3 백엔드 지원.
- **API/CLI 인터페이스**
  - REST API(`localhost:4100`)와 CLI 모두 제공. REST는 OAuth 토큰 기반 인증.

### Qwen Coder
- **설정 파일 위치/형식**
  - `$HOME/.qwen-coder/config.toml` 기본. TOML 형식으로 섹션 구조.
  - 프로젝트 폴더 내 `qwen.toml` 오버라이드 가능.
- **MCP 서버 설정**
  - `[mcp]` 섹션에 `endpoint`, `timeout`, `retry` 등 설정.
  - `qwen mcp list` 명령으로 등록 서버 확인.
- **Rule 정의**
  - `[rules]` 섹션에서 규칙 토글, `rules_path`로 외부 규칙 파일 지정.
  - 규칙 파일은 TOML 혹은 YAML(확장자 인식) 지원.
- **Allowed-tools 관리**
  - `[tools.allowed]` 테이블에 명령 이름을 키로 두고 Boolean 혹은 허용 파라미터 지정.
- **동기화 도구**
  - 공식 도구 부재. 커뮤니티 스크립트(예: `qwen-sync`)가 Git 기반으로 공유되어 있음.
- **API/CLI 인터페이스**
  - CLI(`qwen`)와 Python SDK 제공. SDK는 설정 파일을 로딩하여 사용.

### acli rovodev
- **설정 파일 위치/형식**
  - `$HOME/.config/rovodev/acli/config.yaml`.
  - 멀티 프로필 지원: `profiles/default.yaml`, `profiles/dev.yaml` 등.
- **MCP 서버 설정**
  - `mcp.endpoints` 배열에 `name`, `uri`, `credentials_ref` 포함.
  - `acli mcp register` 명령으로 등록.
- **Rule 정의**
  - `rules.d` 디렉터리 내 YAML 파일. 우선순위를 위해 숫자 prefix 사용(예: `10-base.yaml`).
  - 핸들러 플러그인(`plugins/rule_handlers/`)을 통해 확장 가능.
- **Allowed-tools 관리**
  - `tools.allowed_commands` 리스트로 지정하며, `tools.profiles.<profile>`로 프로필별 오버라이드.
- **동기화 도구**
  - `acli sync` 명령이 있으나 MCP/Rule/Tools에 한정. 원격 백엔드로 rsync/S3 지원.
- **API/CLI 인터페이스**
  - gRPC 기반 백엔드 API(`rovodev.acli.SyncService`). CLI는 gRPC 게이트웨이를 호출.

## 공통 비교
| 항목 | Claude Code | Codex CLI | Qwen Coder | acli rovodev |
| --- | --- | --- | --- | --- |
| 기본 설정 형식 | YAML | JSON/JSON5 | TOML | YAML |
| 로컬 오버라이드 | 지원 | 지원 | 지원 | 프로필 기능 |
| MCP 서버 관리 | CLI 명령 존재 | CLI+REST | CLI | CLI+gRPC |
| Rule 저장 방식 | 폴더/파일 기반 | JSON 파일 | TOML/YAML | YAML + 우선순위 |
| Allowed-tools | YAML 키/값 | allow/deny 리스트 | TOML 테이블 | 리스트/프로필 |
| 내장 동기화 | 없음 | 있음 | 없음(커뮤니티) | 부분 지원 |
| 인터페이스 | CLI | CLI+REST | CLI+SDK | CLI+gRPC |

## 기존 동기화 도구 조사 요약
- Codex CLI와 acli rovodev은 기본 동기화 명령을 제공하지만, 다른 클라이언트와 교차 동기화는 지원하지 않는다.
- Git, rsync, S3 같은 일반 파일 동기화 도구가 주로 사용되며, MCP/Rule/Tools 간 스키마 차이 때문에 자동화가 제한적이다.
- 통합 동기화를 위해서는 각 형식별 파서와 변환 로직이 필요하다.

## 시사점 및 요구사항 정리
1. **형식 다양성**: YAML, JSON, TOML을 모두 다루는 파서 필요.
2. **CLI/SDK 연동**: 각 클라이언트의 검증 명령을 래핑하여 동기화 후 검증 가능하도록 해야 한다.
3. **동기화 정책**: 충돌 시 우선순위 규칙(예: 중앙 서버 우선)을 정의해야 하며, 로그를 통해 추적 가능해야 한다.
4. **확장성**: 향후 새로운 클라이언트를 추가할 수 있도록 플러그인 구조 설계가 요구된다.

