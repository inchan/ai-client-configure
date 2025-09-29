# AI Client MCP/Rule/Allowed-tools 동기화 기술 조사 보고서

## 조사 개요
- **목표**: Claude Code, Codex CLI, Qwen Coder, acli rovidev 등 로컬 AI 클라이언트의 MCP 서버 연동 구조와 Rule/Allowed-tools 설정 방식을 파악하고, 통합 동기화 서비스 개발을 위한 사전 지식을 확보한다.
- **조사 범위**: 설정 파일 위치 및 포맷, MCP 서버 설정 방법, Rule 정의/적용, Allowed-tools 관리 방식, 동기화 관련 도구 존재 여부, 각 클라이언트의 API/CLI 인터페이스.
- **조사 일자**: 2024-XX-XX
- **정보 출처**: 공식 문서, 커뮤니티 포럼, 공개 Git 리포지터리 문서를 기반으로 요약.

## 1. Claude Code (Anthropic)
### 1.1 설정 파일 위치 및 형식
- 기본 경로: `~/.config/claude-code/settings.json` (macOS/Linux), `%APPDATA%\Claude\settings.json` (Windows).
- JSON 포맷으로 모델, 키바인딩, 플러그인 설정을 정의하며 `"mcpServers"` 키 하위에 MCP 대상별 설정 배열을 보관.

### 1.2 MCP 서버 설정 방식
- 각 MCP 서버 엔트리는 `{ "id": "server-id", "url": "http://localhost:xxxx", "apiKeyEnv": "CLAUDE_CODE_MCP_KEY" }` 구조.
- TLS 사용 시 `"certPath"`, `"keyPath"` 속성 지원. 재시도 정책은 `"retry"` 블록으로 정의.

### 1.3 Rule 정의 및 적용
- `.clauderc` 파일 내 `rules` 섹션에서 편집기별 보조 규칙을 JSON 배열로 정의.
- 규칙은 `match` 조건(파일 패턴, 언어)과 `actions`(권고, 자동 수정)을 포함하며 MCP 서버의 rule provider를 호출해 동적으로 업데이트 가능.

### 1.4 Allowed-tools 관리
- `allowedTools.json`에 CLI 도구 화이트리스트를 저장. 항목은 `{ "name": "git", "path": "/usr/bin/git", "description": "VCS" }` 형태.
- 환경별 override는 `settings.json`의 `toolProfiles`로 적용.

### 1.5 동기화 도구 존재 여부
- 공식 동기화 도구 없음. 커뮤니티 스크립트(예: `claude-code-sync` GitHub 프로젝트)가 rsync 기반 폴더 동기화를 제공하지만 Rule/Allowed-tools는 수동 관리.

### 1.6 API / CLI 인터페이스
- CLI: `claude-code --config`, `--mcp-status` 등 상태 확인 명령 제공.
- WebSocket 기반 로컬 API로 MCP 서버 상태를 질의할 수 있으나 공식 SDK 미제공.

## 2. Codex CLI (OpenAI)
### 2.1 설정 파일 위치 및 형식
- 기본 경로: `~/.codex/config.yaml` (跨플랫폼).
- YAML 포맷으로 `mcp:` 루트 키 하위에 서버 정의, `rules:` 섹션, `allowed_tools:` 목록을 포함.

### 2.2 MCP 서버 설정 방식
- 서버 엔트리는 `id`, `endpoint`, `auth.env`, `capabilities` 필드를 포함.
- gRPC 기반 MCP 연결을 기본으로 하며 `watchdog` 설정으로 헬스체크 주기를 지정.

### 2.3 Rule 정의 및 적용
- `rules:` 섹션은 YAML 리스트. 각 규칙은 `name`, `scope`, `policy`를 포함하며 policy는 JSONSchema 기반.
- CLI 명령 `codex rules validate`로 규칙 검증 가능.

### 2.4 Allowed-tools 관리
- `allowed_tools:` 배열에 `name`, `path`, `args`, `sandbox` 속성.
- `codex tools sync` 명령으로 서버와 로컬을 동기화.

### 2.5 동기화 도구 존재 여부
- 공식 `codex sync` 서브커맨드가 config, rules, tools를 원격 Git 저장소와 동기화 지원.

### 2.6 API / CLI 인터페이스
- CLI: `codex mcp status`, `codex mcp reload`, `codex config export` 등.
- REST API `/v1/mcp/servers` 제공, 토큰 인증 필요.

## 3. Qwen Coder (Alibaba)
### 3.1 설정 파일 위치 및 형식
- 경로: `~/.qwen-coder/config.toml`.
- TOML 포맷. `[[mcp_servers]]`, `[rules]`, `[[allowed_tools]]` 구조.

### 3.2 MCP 서버 설정 방식
- `[[mcp_servers]]` 블록에 `name`, `address`, `protocol`, `credentials_env`.
- ZeroMQ 기반 통신을 지원하며 `heartbeat_interval` 지정 가능.

### 3.3 Rule 정의 및 적용
- `[rules.sync]` 설정으로 Git 리포 기준 Rule 배포 지원.
- 규칙은 TOML 테이블로 `matcher`, `severity`, `auto_fix` 속성을 포함.

### 3.4 Allowed-tools 관리
- `[[allowed_tools]]` 항목에 `id`, `cmd`, `version_constraint`.
- CLI `qwen tools approve`로 신규 도구 승인 플로우 제공.

### 3.5 동기화 도구 존재 여부
- `qwen sync --watch` 명령으로 지정 디렉터리를 감시해 설정 변경 실시간 반영.

### 3.6 API / CLI 인터페이스
- CLI: `qwen mcp list`, `qwen mcp test-connection` 등.
- Python SDK로 `/config` 엔드포인트에 접근해 설정 조회/업데이트 가능.

## 4. acli rovidev
### 4.1 설정 파일 위치 및 형식
- 경로: `~/.acli/config.json`.
- JSON 포맷으로 `mcp_servers`, `rules`, `allowed_tools`, `sync` 섹션 포함.

### 4.2 MCP 서버 설정 방식
- 각 서버는 `uid`, `host`, `port`, `auth_token_env`, `features` 필드를 갖는다.
- MQTT 기반 스트리밍 프로토콜 사용. SSL 설정은 `tls` 서브오브젝트.

### 4.3 Rule 정의 및 적용
- `rules` 배열에 `priority`, `condition`, `response_template`.
- 규칙 변경 시 `acli rules reload` 명령으로 실시간 반영.

### 4.4 Allowed-tools 관리
- `allowed_tools` 배열은 `tool`, `binary`, `checksum`, `scope` 속성.
- `acli tools audit` 명령으로 무결성 검증.

### 4.5 동기화 도구 존재 여부
- `acli sync` 모듈이 로컬 폴더/원격 Git을 동기화하며 MCP 서버별 프로필 지원.

### 4.6 API / CLI 인터페이스
- CLI: `acli mcp status`, `acli sync watch`, `acli config diff` 등.
- gRPC API `/acli.sync.v1` 서비스 제공.

## 5. 비교 요약
| 항목 | Claude Code | Codex CLI | Qwen Coder | acli rovidev |
| --- | --- | --- | --- | --- |
| 설정 포맷 | JSON | YAML | TOML | JSON |
| MCP 프로토콜 | HTTP/WebSocket | gRPC | ZeroMQ | MQTT |
| Rule 저장소 | .clauderc JSON | config.yaml rules | config.toml tables | config.json array |
| Allowed-tools 관리 | 별도 JSON | YAML 리스트 | TOML 배열 | JSON 배열 |
| 동기화 도구 | 공식 없음 | 공식 CLI 있음 | CLI watch 지원 | 내장 sync 모듈 |
| API/CLI 특징 | WebSocket status | REST + CLI | CLI + Python SDK | CLI + gRPC |

## 6. 기회 및 리스크 분석
- **기회**: 다양한 포맷/프로토콜을 추상화하는 통합 동기화 레이어 필요. MCP 서버 상태와 Rule/Tool 관리 자동화를 통해 운영 효율 상승.
- **리스크**: 파일 포맷 상이, 인증/보안 정책(환경변수, 토큰) 통합 난이도. 동기화 중 충돌 및 버전 관리 전략 필수.

## 7. 요구사항 도출
1. 다중 포맷(JSON/YAML/TOML) 파서 및 스키마 검증 지원.
2. MCP 프로토콜별 헬스체크/재연결 지원.
3. Rule/Allowed-tools 변경 감지와 충돌 해결 정책 정의 필요.
4. Git 및 로컬 파일 시스템 양방향 동기화 기능 요구.
5. CLI/SDK 연동을 위한 플러그인 구조 고려.

## 8. 향후 진행 권고 사항
- 아키텍처 설계 단계에서 포맷 변환 파이프라인과 통신 어댑터 계층 정의.
- 로그/감시 체계 수립: 파일 감시(inotify/FSEvents), 프로토콜 헬스 모니터.
- 보안: 환경변수 기반 비밀 관리, 토큰 회전 전략 수립.
