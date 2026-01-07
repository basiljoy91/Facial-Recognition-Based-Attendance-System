from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    app_env: str = Field(default="local")
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    log_level: str = Field(default="INFO")

    postgres_host: str
    postgres_port: int = Field(default=5432)
    postgres_db: str
    postgres_user: str
    postgres_password: str

    jwt_secret: str
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=120)

    embedding_dim: int = Field(default=512)
    similarity_threshold: float = Field(default=0.65)

    attendance_window_start: str = Field(default="07:00")
    attendance_window_end: str = Field(default="19:00")
    attendance_grace_minutes: int = Field(default=10)
    duplicate_cooldown_minutes: int = Field(default=5)

    audit_log_enabled: bool = Field(default=True)
    fernet_key: str
    model_cache_dir: str = Field(default="/models")

    @property
    def database_url(self) -> str:
        # Construct URL manually to avoid path issues
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


