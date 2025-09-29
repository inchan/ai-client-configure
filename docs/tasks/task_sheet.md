# AI Client 동기화 서비스 Task 관리 시트

아래 표는 프로젝트를 환경 설정, 백엔드, 프런트엔드, 동기화 엔진, 로그 시스템, 테스트/배포 워크플로로 구분하여 작성한 상세 Task 목록이다. 각 Task는 독립적으로 개발·검증 가능하도록 테스트 시나리오와 완료 조건을 명시했다.

| Task ID | Workflow 분류 | Task 이름 | 설명 | 우선순위 | 예상 소요시간 | 의존성 | Subtasks | 완료 조건 | 테스트 시나리오 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENV-01 | 환경 설정 및 초기화 | 개발 환경 부트스트랩 | Poetry/uv 프로젝트 초기화, 기본 패키지 설치 스크립트, Docker Compose 템플릿 작성 | 높음 | 1d | 없음 | - Poetry/uv 설정<br>- pre-commit 정의<br>- Docker Compose 베이스 작성 | `poetry install` 성공, Docker Compose로 FastAPI+Redis 기동 | `poetry install` 실행, `docker compose up`으로 서비스 기동 확인 |
| ENV-02 | 환경 설정 및 초기화 | 시크릿 관리 구성 | Keyring/.env 템플릿, 암호화 유틸 제공 | 중간 | 0.5d | ENV-01 | - .env 템플릿 작성<br>- Keyring helper 구현 | .env.example 제공, keyring 스크립트 테스트 통과 | 단위 테스트로 keyring helper 검증 |
| BE-01 | 백엔드 API 개발 | 인증 모듈 구현 | OAuth2 password flow, 사용자 DB seeding | 높음 | 1.5d | ENV-01 | - 사용자 모델/스키마<br>- 토큰 발급 엔드포인트<br>- 비밀번호 해시 | `/api/v1/auth/token` 200 응답, 만료 정책 적용 | pytest로 토큰 발급/만료/실패 시나리오 검증 |
| BE-02 | 백엔드 API 개발 | 클라이언트 메타데이터 API | 클라이언트 CRUD, 우선순위/상태 관리 | 높음 | 1d | BE-01 | - CLIENT 모델/CRUD<br>- 우선순위 업데이트 로직 | CRUD 동작, 우선순위 규칙 검증 | pytest + Schemathesis로 API contract 테스트 |
| BE-03 | 백엔드 API 개발 | 스냅샷/동기화 API | 스냅샷 조회, 적용, 트리거 엔드포인트 | 높음 | 2d | BE-02, ENG-02 | - 스냅샷 조회/필터링<br>- 동기화 트리거 핸들러 | 최신 스냅샷 조회 및 트리거 성공, 권한 체크 | pytest-asyncio로 비동기 핸들러 테스트 |
| BE-04 | 백엔드 API 개발 | 로그 서비스 API | 로그 조회, Export, 실시간 스트림 엔드포인트 | 중간 | 1d | BE-03, LOG-01 | - 로그 조회 쿼리<br>- Export API<br>- SSE/WebSocket 브로드캐스트 | 로그 조회/Export 200 응답, 스트림 연결 성공 | pytest + schemathesis + WebSocket 통합 테스트 |
| FE-01 | 프런트엔드 개발 | UI 스캐폴딩 & 라우팅 | Vite + React + TypeScript 셋업, 라우터 구성 | 높음 | 1d | ENV-01 | - Vite 템플릿<br>- 글로벌 스타일<br>- Router 구성 | `npm run build` 성공, 기본 라우터 작동 | Vitest + Playwright smoke test |
| FE-02 | 프런트엔드 개발 | 대시보드 화면 | 상태 카드, 이벤트 타임라인, 실시간 업데이트 구독 | 높음 | 2d | FE-01, OPS-01 | - 상태 카드 컴포넌트<br>- 이벤트 스트림 훅<br>- 오류 배너 | 실시간 스트림 수신 후 UI 갱신 | Storybook 스냅샷, Playwright 실시간 업데이트 검증 |
| FE-03 | 프런트엔드 개발 | 로그 뷰어 & Export | 로그 필터링, 페이지네이션, Export 버튼 | 중간 | 1.5d | FE-01, BE-04 | - 로그 테이블<br>- Export 모달<br>- 다운로드 처리 | 필터, 페이지네이션, Export 성공 | Vitest 컴포넌트 테스트, Playwright E2E |
| ENG-01 | 동기화 엔진 개발 | 파일 감시자 구현 | watchfiles 기반 디렉터리 감시, 이벤트 큐잉 | 높음 | 1.5d | ENV-01 | - 감시 경로 구성<br>- 이벤트 디바운스<br>- 오류 재시도 | 파일 변경 시 이벤트 생성, 재시도 동작 | pytest로 감시자 유닛 테스트, 통합 테스트 |
| ENG-02 | 동기화 엔진 개발 | 스키마 노멀라이저 | MCP/Rule/Allowed-tools 공통 스키마 정의 | 높음 | 2d | ENG-01 | - UnifiedConfig 모델<br>- 파서/검증기<br>- 역직렬화 | 다양한 샘플 입력 처리, 검증 오류 처리 | pytest parameterized 테스트 |
| ENG-03 | 동기화 엔진 개발 | 충돌 해결 모듈 | 우선순위/타임스탬프/수동 개입 정책 구현 | 높음 | 2d | ENG-02 | - 정책 정의<br>- 자동 병합 로직<br>- 수동 개입 큐 | 테스트 정책별 기대 동작 | pytest로 정책별 시나리오 검증 |
| ENG-04 | 동기화 엔진 개발 | 동기화 파이프라인 | 이벤트 → 스냅샷 → 전파 전체 파이프라인 | 높음 | 3d | ENG-03, BE-03 | - 파이프라인 오케스트레이션<br>- Redis Streams publish<br>- 전파 드라이버 | 파이프라인 테스트, 실패 복구 동작 | pytest-asyncio 통합 테스트 |
| LOG-01 | 로그 시스템 구현 | 구조화 로깅 & 저장 | structlog 설정, DB 연동, 수준별 필터 | 높음 | 1d | ENG-04 | - structlog 설정<br>- DB 핸들러<br>- 회전 정책 | 로그 DB 적재 및 파일 회전 동작 | pytest로 로깅 헬퍼 테스트 |
| LOG-02 | 로그 시스템 구현 | Export & 알림 | CSV/JSON Export, OpenTelemetry 옵션 | 중간 | 1d | LOG-01, BE-03 | - Export API<br>- 파일 저장소<br>- 알림 훅 | Export API 200 응답, 파일 다운로드 | pytest + Playwright로 다운로드 검증 |
| OPS-01 | 테스트 및 배포 | CI 파이프라인 구성 | GitHub Actions에서 lint/test/build 실행 | 높음 | 1d | ENV-01 | - lint 워크플로<br>- 백엔드 테스트 잡<br>- 프런트엔드 빌드 | CI 파이프라인 성공, 캐시 전략 문서화 | 워크플로 실행 로그 확인 |
| OPS-02 | 테스트 및 배포 | 커버리지 & 품질 게이트 | pytest 커버리지 80%, SonarLint/Ruff 통합 | 중간 | 1d | OPS-01, BE-03 | - 커버리지 보고서<br>- 품질 게이트 규칙 정의 | CI에서 커버리지 80% 이상, 린터 통과 | pytest --cov, Ruff, SonarLint 리포트 |
| OPS-03 | 테스트 및 배포 | 릴리스 패키징 | Docker 이미지 빌드, 버전 태깅, changelog 자동화 | 중간 | 1d | OPS-01 | - Dockerfile 최적화<br>- 버전 태깅 스크립트<br>- changelog 자동화 | 릴리스 태그 생성, 이미지 빌드 성공 | docker build, 릴리스 드라이런 |

> **시간 단위**: 1d = 1 개발일(8h 기준). 실제 일정은 인력/우선순위에 따라 조정될 수 있다.

## 진행 관리 권장 지표
- 워크플로 분류별 완료율
- 테스트 커버리지 및 린트 통과율
- 동기화 실패/성공 비율
- 릴리스 리드타임

## 위험 및 대응
- **파일 시스템 권한 문제**: 설치 가이드에 권한 설정 절차 추가, 감시자에서 권한 오류 핸들링 강화.
- **클라이언트별 포맷 변화**: 플러그인 기반 파서 구조로 핫스왑 가능하도록 설계.
- **실시간 스트림 부하**: Redis Consumer 그룹과 백프레셔 정책 적용.
- **보안**: 로컬 인증 및 비밀 관리 가이드 제공, 감사 로그 유지.

## Task 진행 현황 (업데이트)
- **ENV-01 완료**: FastAPI 기반 백엔드 스캐폴딩, Docker Compose 템플릿, `scripts/dev_setup.sh` 설치 스크립트를 추가하여 환경 부트스트랩을 자동화했습니다.
- **ENV-02 완료**: `.env.example` 템플릿과 keyring 기반 `sync_service.secrets` 헬퍼를 도입하여 비밀 값 저장/검증 흐름을 정립했습니다.
