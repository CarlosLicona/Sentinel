from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Database
    database_url: str = "postgresql://sentinel:sentinel_pass@localhost:5432/sentinel_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
