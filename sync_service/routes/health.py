"""헬스체크 엔드포인트."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="동기화 서비스 상태 확인")
def read_health() -> dict[str, str]:
    """서비스 상태를 반환한다."""

    return {"status": "ok"}
