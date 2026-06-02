import os


class Settings:
    project_name: str
    environment: str

    database_url: str
    redis_url: str

    openai_api_key: str | None
    ipinfo_token: str | None

    def __init__(self) -> None:
        self.project_name = os.getenv("PROJECT_NAME", "Exposure Intelligence Platform")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://eip_user:eip_password@localhost:5432/eip",
        )
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ipinfo_token = os.getenv("IPINFO_TOKEN")


_settings_instance: Settings | None = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
