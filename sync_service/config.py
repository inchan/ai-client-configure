"""환경 변수 및 기본 설정을 정의한다."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정."""

    app_name: str = Field(default="AI Client Sync Service", description="서비스 이름")
    api_prefix: str = Field(default="/api/v1", description="API 기본 경로")
    reload: bool = Field(default=True, description="uvicorn reload 모드")
    redis_url: str = Field(default="redis://redis:6379/0", description="Redis 접속 URL")
    database_url: str = Field(
        default=f"sqlite:///{Path.cwd() / 'data' / 'sync_service.db'}",
        description="기본 데이터베이스 URL",
    )
    secret_service_name: str = Field(
        default="ai-client-sync-service",
        description="Keyring 서비스 이름",
    )
    api_token_key: str = Field(
        default="sync-service-api-token",
        description="API 토큰을 저장할 keyring 사용자 키",
    )
    admin_password_key: str = Field(
        default="sync-service-admin-password",
        description="관리자 비밀번호를 저장할 keyring 사용자 키",
    )

    model_config = SettingsConfigDict(
        env_prefix="SYNC_SERVICE_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """싱글톤 설정 인스턴스를 반환한다."""

    return Settings()
