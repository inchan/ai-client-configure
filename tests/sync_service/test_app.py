"""동기화 서비스 FastAPI 앱 테스트."""

from fastapi.testclient import TestClient

from sync_service.app import create_app
from sync_service.config import Settings


def test_health_endpoint_returns_ok() -> None:
    settings = Settings(api_prefix="")
    app = create_app(settings=settings)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_settings_apply_custom_prefix() -> None:
    settings = Settings(api_prefix="/custom")
    app = create_app(settings=settings)
    client = TestClient(app)

    response = client.get("/custom/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
