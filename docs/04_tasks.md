# 동기화 서비스 개발 Task 관리 시트

| Task ID | 분류 | Task 이름 | 설명 | 우선순위 | 예상 소요시간 | 의존성 | Subtasks | 완료 조건 | 테스트 시나리오 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-ENV-01 | 환경 설정 및 초기화 | 개발 환경 부트스트랩 | Python 가상환경, Node 패키지, Docker Compose 스켈레톤 구성 | High | 2일 | - | - 가상환경 스크립트 작성<br>- Docker Compose 초안 작성 | FastAPI/React dev 서버 구동, 기본 Docker 컨테이너 실행 | `make dev-up` 실행 시 백엔드/프론트 모두 기동 확인 |
| T-ENV-02 | 환경 설정 및 초기화 | CI 파이프라인 구축 | GitHub Actions로 lint/test 실행 파이프라인 구성 | Medium | 1일 | T-ENV-01 | - Workflow YAML 작성<br>- 캐시 전략 정의 | PR 생성 시 lint/test 자동 실행 | PR에 GitHub Actions 체크 통과 |
| T-BE-01 | 백엔드 API 개발 | FastAPI 프로젝트 스캐폴딩 | 핵심 폴더 구조, 설정 로딩, DB 커넥션 초기화 | High | 3일 | T-ENV-01 | - settings 모듈 구현<br>- DB 세션 팩토리 구성 | `/health` 엔드포인트 200 응답, DB 마이그레이션 성공 | `pytest tests/api/test_health.py` 통과 |
| T-BE-02 | 백엔드 API 개발 | 인증/권한 모듈 구현 | OAuth2 Password Flow, 사용자 관리 API | High | 2일 | T-BE-01 | - 사용자 모델/스키마 작성<br>- 토큰 발급 로직 구현 | 로그인, 토큰 검증, 권한 체크 동작 | 인증 관련 pytest 통과 |
| T-BE-03 | 백엔드 API 개발 | 동기화 상태 API | `/clients`, `/sync/status`, `/sync/trigger` 구현 | High | 3일 | T-BE-01 | - Service 레이어 작성<br>- Redis 이벤트 연동 | API 스펙 문서와 응답 일치 | 단위/통합 테스트 + OpenAPI 확인 |
| T-BE-04 | 백엔드 API 개발 | 로그/Export API | `/logs`, `/export` 구현 및 Loki/스토리지 연동 | Medium | 3일 | T-BE-03 | - Loki 쿼리 래퍼<br>- Export 파이프라인 | 로그 검색/Export 성공 | pytest + 통합 시나리오 |
| T-FE-01 | 프론트엔드 개발 | UI 프레임워크 셋업 | Vite+React+TS 초기 구조, 라우팅 구성 | High | 2일 | T-ENV-01 | - 페이지 레이아웃 컴포넌트<br>- 공통 스타일 시스템 | 기본 페이지 렌더링, 라우팅 정상 | `pnpm test` 및 스냅샷 통과 |
| T-FE-02 | 프론트엔드 개발 | 대시보드 화면 구현 | 실시간 상태 카드, 타임라인 | High | 3일 | T-FE-01, T-BE-03 | - WebSocket 훅<br>- 상태 카드 컴포넌트 | 실시간 상태 업데이트 표시 | Cypress/Playwright 시나리오 |
| T-FE-03 | 프론트엔드 개발 | 로그 뷰어 구현 | 필터, 로그 테이블, 상세 패널 | Medium | 3일 | T-FE-01, T-BE-04 | - 필터 폼<br>- 로그 테이블 | 로그 검색 및 상세 보기 동작 | E2E 테스트로 필터링 확인 |
| T-FE-04 | 프론트엔드 개발 | 설정/정책 화면 | 동기화 정책 CRUD, Export 예약 | Medium | 3일 | T-FE-01, T-BE-03, T-BE-04 | - 폼 컴포넌트<br>- 일정 예약 UI | 정책 변경 저장, Export 예약 성공 | Playwright 폼 제출 테스트 |
| T-SE-01 | 동기화 엔진 개발 | 어댑터 인터페이스 정의 | 통합 중간 스키마와 추상 BaseAdapter 설계 | High | 2일 | T-BE-01 | - BaseAdapter 클래스<br>- 변환 스키마 정의 | 각 어댑터가 인터페이스 준수 | 단위 테스트로 Mock 어댑터 검증 |
| T-SE-02 | 동기화 엔진 개발 | 파일 감시 서비스 | watchdog 기반 파일 감시 및 이벤트 브로커 전송 | High | 3일 | T-SE-01 | - 감시 매니저<br>- Redis Streams 퍼블리셔 | 파일 변경 시 이벤트 생성 | pytest로 파일 변경 모의 테스트 |
| T-SE-03 | 동기화 엔진 개발 | 동기화 파이프라인 구현 | 이벤트 수신→변환→배포 전체 파이프라인 | High | 5일 | T-SE-01, T-SE-02 | - 파서/변환 모듈<br>- 충돌 해결기 | 동기화 세션 성공/실패 상태 기록 | 통합 테스트로 멀티 클라이언트 시나리오 |
| T-SE-04 | 동기화 엔진 개발 | 충돌 해결/검증 도구 | 정책 기반 충돌 처리, CLI 검증 호출 | Medium | 3일 | T-SE-03 | - 정책 엔진<br>- CLI 커맨드 래퍼 | 충돌 사례별 정책 적용 | 시뮬레이션 테스트 |
| T-LOG-01 | 로그 시스템 구현 | Loki/Grafana 통합 | Loki 스택 docker-compose 서비스 추가 | Medium | 2일 | T-ENV-01 | - Loki 설정<br>- Grafana 대시보드 템플릿 | 로그 수집/조회 가능 | Docker 환경에서 로그 쿼리 테스트 |
| T-LOG-02 | 로그 시스템 구현 | 애플리케이션 로깅 | 구조화 로그, Loki 전송 핸들러 | Medium | 2일 | T-BE-01, T-SE-03 | - Python 로거 설정<br>- 프론트 로깅 API | 로그가 Loki에 정상 적재 | pytest + 수동 확인 |
| T-QA-01 | 테스트 및 배포 | 통합 테스트 파이프라인 | 백엔드/프론트/엔진 통합 테스트 자동화 | High | 3일 | 모든 기능 개발 | - docker-compose 통합 테스트<br>- k6 부하 테스트 | CI에서 통합 테스트 통과 | GitHub Actions 리포트 확인 |
| T-QA-02 | 테스트 및 배포 | 배포 패키징 | Docker 이미지 빌드, 설치 스크립트, 문서화 | High | 2일 | T-QA-01 | - Dockerfile 최적화<br>- install 스크립트 | 릴리스 패키지 생성, 설치 테스트 | 로컬 설치 시나리오 검증 |

