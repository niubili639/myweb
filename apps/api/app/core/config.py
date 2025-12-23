from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    project_name: str = "MyWebBack API"
    environment: str = "local"
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "mysql+pymysql://appuser:appuser@114.55.55.110:3306/appdb"
    allowed_origins_raw: str = Field("http://localhost:5173", alias="ALLOWED_ORIGINS")
    log_level: str = "INFO"
    secret_key: str = "please_change_me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    qwen_api_key: str | None = None
    qwen_model: str = "qwen-turbo"
    # Qwen image model must be one of qwen-image-plus / qwen-image
    qwen_image_model: str = "qwen-image-plus"
    qwen_base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    invite_secret: str = "invite-secret"

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins_raw.split(",") if item.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
