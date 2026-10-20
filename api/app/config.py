from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str
    test_database_url: str | None = None
    jwt_secret: str
    jwt_expire_minutes: int = 1440
    business_tz: str = "Asia/Yangon"


settings = Settings()
