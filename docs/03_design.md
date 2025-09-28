# 동기화 서비스 상세 설계 문서

## 1. 시스템 설계

### 1.1 컴포넌트 다이어그램
```
+------------------+        +---------------------+
| React Frontend   |<------>| FastAPI Gateway     |
| - Dashboard      |  REST  | - Auth Service      |
| - Log Viewer     |  WS    | - Sync API          |
| - Policy Editor  |        | - Export API        |
+------------------+        +----------+----------+
                                     |
                                     v
                          +----------+-----------+
                          | Sync Orchestrator    |
                          | - Adapter Manager    |
                          | - Conflict Resolver  |
                          | - Scheduler          |
                          +----------+-----------+
                                     |
             +-----------------------+------------------------+
             |                        |                       |
             v                        v                       v
+-----------------+       +------------------+      +--------------------+
| File Watchers   |       | Persistence      |      | Observability Stack |
| - watchdog      |       | - PostgreSQL     |      | - Loki (logs)       |
| - per client    |       | - Redis Streams  |      | - Prometheus        |
+-----------------+       +------------------+      +--------------------+
             |
             v
    +-------------------+
    | Local AI Clients  |
    +-------------------+
```

### 1.2 데이터 플로우
1. 파일 감시기가 MCP/Rule/Allowed-tools 파일 변경을 감지하고 이벤트를 Redis Streams에 기록.
2. Sync Orchestrator가 이벤트를 구독하여 해당 클라이언트 어댑터를 통해 파일을 파싱 후 공통 모델로 변환.
3. 변환된 데이터는 PostgreSQL에 버전 기록으로 저장되고, 정책에 따라 다른 클라이언트 설정으로 변환되어 파일 시스템에 반영.
4. 동기화 결과 및 로그는 Loki에 저장되며, 상태 요약은 Redis를 통해 FastAPI에 전달.
5. FastAPI는 WebSocket으로 프론트엔드에 실시간 상태를 push하고, REST API를 통해 이력 조회/설정 변경을 제공.

### 1.3 API 설계 (요약)
| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| POST | `/api/v1/auth/login` | 로컬 사용자 로그인 |
| GET | `/api/v1/clients` | 등록된 클라이언트 목록 조회 |
| POST | `/api/v1/clients` | 신규 클라이언트 설정 추가 |
| GET | `/api/v1/sync/status` | 현재 동기화 상태 및 최근 이벤트 |
| POST | `/api/v1/sync/trigger` | 수동 동기화 트리거 |
| GET | `/api/v1/logs` | 로그 검색 (쿼리 파라미터 지원) |
| GET | `/api/v1/export` | 로그 및 설정 내보내기 |
| WS | `/ws/sync` | 실시간 상태 스트림 |

## 2. 데이터베이스 설계

### 2.1 ERD 요약
```
Clients (id, name, type, config_path, created_at, updated_at)
Adapters (id, client_type, version, schema_version, metadata)
SyncSessions (id, client_id, started_at, finished_at, status, summary)
SyncEvents (id, session_id, event_type, payload, created_at)
Artifacts (id, session_id, artifact_type, storage_path, checksum)
Users (id, username, password_hash, role, created_at)
AuditLogs (id, user_id, action, target, details, created_at)
```

### 2.2 테이블 스키마 (핵심)
- **clients**
  - `id SERIAL PK`
  - `name VARCHAR(100)`
  - `type VARCHAR(50)` (enum: claude, codex, qwen, acli ...)
  - `config_path TEXT`
  - `settings JSONB`
  - `created_at TIMESTAMP`, `updated_at TIMESTAMP`
- **sync_sessions**
  - `id UUID PK`
  - `client_id FK -> clients.id`
  - `started_at TIMESTAMP`
  - `finished_at TIMESTAMP`
  - `status VARCHAR(20)` (pending, running, success, failed)
  - `summary JSONB`
- **sync_events**
  - `id UUID PK`
  - `session_id FK -> sync_sessions.id`
  - `event_type VARCHAR(50)`
  - `payload JSONB`
  - `created_at TIMESTAMP`
- **artifacts**
  - `id UUID PK`
  - `session_id FK`
  - `artifact_type VARCHAR(30)` (config_snapshot, diff, log)
  - `storage_path TEXT`
  - `checksum VARCHAR(128)`
- **users**
  - `id SERIAL PK`
  - `username VARCHAR(50) UNIQUE`
  - `password_hash TEXT`
  - `role VARCHAR(20)` (admin, viewer)
- **audit_logs**
  - `id UUID PK`
  - `user_id FK -> users.id`
  - `action VARCHAR(50)`
  - `target TEXT`
  - `details JSONB`
  - `created_at TIMESTAMP`

## 3. UI/UX 설계

### 3.1 와이어프레임 개요
- **대시보드 화면**
  - 상단: 전체 동기화 상태 카드 (성공/실패 카운트, 최근 실행 시간).
  - 중앙: 클라이언트별 동기화 상태 타일.
  - 하단: 최근 이벤트 타임라인.
- **클라이언트 상세 화면**
  - 좌측: MCP/Rule/Tools 파일 목록 트리.
  - 우측: 중간 스키마 Diff 뷰어 및 수동 동기화 버튼.
- **로그 뷰어**
  - 검색 필터(클라이언트, 수준, 기간), 테이블 리스트, 상세 패널.
- **설정 화면**
  - 동기화 정책(우선순위, 충돌 전략) 선택, Export 작업 예약.

### 3.2 화면 플로우
1. 로그인 → 대시보드 진입.
2. 대시보드에서 특정 클라이언트 클릭 → 상세 화면.
3. 상세 화면에서 동기화 수동 실행 또는 로그 열람.
4. 상단 메뉴에서 로그 뷰어 및 설정 화면 이동 가능.

## 4. 동기화 로직 설계

### 4.1 동기화 알고리즘
1. 이벤트 수신: 파일 변경 혹은 사용자가 트리거한 동기화 요청.
2. 로드 단계: 해당 클라이언트 어댑터가 파일을 읽어 파싱.
3. 검증 단계: 스키마 유효성 검사, 필수 필드 체크, CLI 검증 명령 실행.
4. 중간 표현 변환: 공통 모델(`UnifiedConfig`)로 매핑.
5. 비교/머지: 중앙 레퍼런스 스토어(PostgreSQL)와 비교하여 변경 사항 계산.
6. 충돌 해결: 정책에 따라 `last-write-wins`, `central-authoritative`, `manual-review` 중 선택.
7. 배포 단계: 필요한 타겟 클라이언트 설정 파일로 변환 후 기록.
8. 후처리: 로그 기록, 알림 발송(WebSocket), Export 요청 예약 처리.

### 4.2 충돌 해결 방안
- **자동 우선순위**: 클라이언트별 우선순위 점수 설정. 높은 우선순위 설정이 충돌 시 승자.
- **타임스탬프 기반**: 최근 변경 시간 기준으로 승자 결정.
- **수동 검토**: 충돌 발생 시 사용자에게 diff를 제공하고 결정 버튼을 통해 선택.
- 모든 전략은 감사 로그에 기록.

### 4.3 에러 핸들링
- 파일 접근 오류 → 재시도(지수 백오프) 후 실패 시 경고 알림.
- 파싱 실패 → 오류 이벤트 기록, 사용자에게 파일 위치와 상세 오류 제공.
- CLI 검증 실패 → 실패 로그 저장, 영향을 받는 클라이언트 동기화 중단.
- 시스템 오류 → Sentry 대체(오픈소스 `glitchtip`) 연동으로 오류 추적.

