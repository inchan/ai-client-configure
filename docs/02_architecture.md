# AI Client 동기화 서비스 아키텍처 및 기술 스택 제안

## 요구사항 요약
- 로컬 설치 가능한 웹 서비스 형태
- 실시간 동기화 상태 모니터링 및 알림
- 로그 관리 및 내보내기(export)
- 확장 가능한 구조 및 새로운 클라이언트 추가 용이성

## 제안 아키텍처

```
+-------------------+          +---------------------+
|   Web Frontend    | <------> |  Backend API Layer  |
| (React + Vite)    |  WebSocket/REST  (FastAPI)    |
+---------+---------+          +----------+----------+
          |                               |
          | GraphQL/REST API              |
          v                               v
+---------+---------+          +----------+-----------+
|  Sync Orchestrator | <-----> | Persistence Layer    |
|  (Python service)  |  Event  | (PostgreSQL + Redis) |
+---------+---------+  Bus     +----------+-----------+
          |                               |
          |                               |
          v                               v
+---------+---------+          +----------+-----------+
| File Watch Agents |          | Log Aggregation      |
| (watchdog +       |          | (OpenSearch / Loki)  |
|  client adapters) |          +----------+-----------+
+---------+---------+                     |
          |                               |
          v                               v
+-------------------+          +---------------------+
| Local AI Clients  |          | Export Connectors   |
| (Claude, Codex,   |          | (CSV, JSON, S3)      |
|  Qwen, acli ...)  |          +---------------------+
```

### 동작 개요
1. 파일 감시 에이전트가 각 클라이언트의 설정 디렉터리 변화를 감지.
2. Sync Orchestrator가 감지 이벤트를 받아 파서/변환 모듈을 통해 공통 중간 스키마로 변환.
3. Backend API는 상태와 로그를 DB/로그 스토리지에 기록하고 WebSocket을 통해 프론트엔드에 실시간 전파.
4. 프론트엔드는 대시보드, 로그 뷰어, 동기화 정책 설정 UI를 제공.
5. Export Connectors는 사용자 요청 시 로그와 동기화 설정을 다양한 포맷으로 내보낸다.

## 기술 스택 선정

| 영역 | 기술 | 선택 이유 |
| --- | --- | --- |
| 백엔드 프레임워크 | FastAPI | ASGI 기반 비동기 처리, Pydantic으로 스키마 검증, OpenAPI 자동 문서화 |
| 프론트엔드 | React + Vite + TypeScript | 컴포넌트 생태계 풍부, Vite로 빠른 로컬 개발, 타입 안정성 |
| 실시간 통신 | WebSocket (FastAPI), SSE 대체 옵션 | 실시간 상태 업데이트 |
| 데이터베이스 | PostgreSQL | ACID 보장, JSONB로 유연한 스키마 저장 가능 |
| 캐시/큐 | Redis Streams | 실시간 이벤트 큐 및 Pub/Sub, 작업 재시도 |
| 로그 관리 | Loki + Grafana (경량) | 라벨 기반 로그 검색, 로컬 설치 용이 |
| 파일 감시 | Python watchdog 라이브러리 | 크로스 플랫폼 파일 변경 감지 |
| 설정 파서 | PyYAML, json5, tomli | 다양한 포맷 지원 |
| 테스트 프레임워크 | pytest, Playwright(프론트), k6(부하) | TDD 및 통합 테스트 용이 |
| 컨테이너화 | Docker Compose | 로컬 설치 시 의존성 관리 |
| 인증/권한 | OAuth2 Password Flow (FastAPI) | 로컬 사용자 관리 |

## 확장 전략
- **모듈형 어댑터**: 각 클라이언트별 파서를 `Adapter` 인터페이스 구현체로 분리하여 신규 클라이언트를 쉽게 추가.
- **이벤트 기반 확장**: Redis Streams를 통한 이벤트 브로커 도입으로 여러 Sync Worker를 수평 확장 가능.
- **관찰성**: Loki/Grafana와 Prometheus를 연계해 메트릭/로그를 통합 모니터링.

## 로그 관리 및 Export
- 애플리케이션 로그는 Loki에 저장하고 Grafana 대시보드에서 검색.
- Export 요청 시 FastAPI 백엔드에서 PostgreSQL/Redis/Loki 데이터를 집계하여 CSV, JSON, Parquet 형식으로 제공.
- 감사 로그는 S3 호환 스토리지(minio)로 주기적 백업.

