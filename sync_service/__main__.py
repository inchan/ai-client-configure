"""`python -m sync_service` 실행 지원."""

import uvicorn

from .config import get_settings


def main() -> None:
    """uvicorn 서버를 실행한다."""

    settings = get_settings()
    uvicorn.run(
        "sync_service.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.reload,
    )


if __name__ == "__main__":
    main()
