"""동기화 서비스 FastAPI 앱 진입점."""

from .app import create_app

app = create_app()
