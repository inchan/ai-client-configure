# AI Client 동기화 서비스 기획 자료

이 저장소는 Claude Code, Codex CLI, Qwen Coder, acli rovodev 등 로컬 AI 클라이언트의 MCP/Rule/Allowed-tools 설정을 통합 관리하기 위한 동기화 서비스의 기획 및 설계 문서를 담고 있습니다.

## 제공 문서
- `docs/01_research.md`: 클라이언트별 설정 구조 및 동기화 방식에 대한 기술 조사 보고서.
- `docs/02_architecture.md`: 제안 아키텍처 다이어그램과 기술 스택 선정 근거.
- `docs/03_design.md`: 시스템/데이터베이스/UI/동기화 로직 상세 설계.
- `docs/04_tasks.md`: 단계별 개발 Task 관리 시트.
- `docs/05_task_template.md`: 개별 Task 구현 시 사용할 프롬프트 템플릿.
- `docs/06_testing_review.md`: 테스트 및 리뷰 가이드.
- `docs/07_documentation.md`: 문서 업데이트 가이드.
- `docs/08_project_management.md`: 프로젝트 관리 및 주간 리포트 가이드라인.

## 활용 방법
1. `docs/01_research.md`를 통해 현행 클라이언트 설정 구조를 이해합니다.
2. `docs/02_architecture.md`와 `docs/03_design.md`를 참고하여 구현 범위와 구조를 확정합니다.
3. `docs/04_tasks.md`와 `docs/05_task_template.md`를 기반으로 작업을 분할하고 실행합니다.
4. 구현 후 `docs/06_testing_review.md`, `docs/07_documentation.md`를 활용하여 품질 검증 및 문서화를 수행합니다.
5. 프로젝트 전반 관리는 `docs/08_project_management.md`의 절차를 따릅니다.

