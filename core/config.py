from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    project_name: str = "Exposure Intelligence Platform"
    environment: str = "development"

    database_url: str = Field(
        "postgresql+asyncpg://eip_user:eip_password@localhost:5432/eip",
        env="DATABASE_URL",
    )

    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")

    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")
    ipinfo_token: str | None = Field(None, env="IPINFO_TOKEN")

    class Config:
        env_file = ".env"


_settings_instance: Settings | None = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
