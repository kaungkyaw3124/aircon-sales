from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str
    test_database_url: str | None = None
    jwt_secret: str
    jwt_expire_minutes: int = 1440
    business_tz: str = "Asia/Yangon"
    # comma-separated proxy IPs whose X-Forwarded-For we believe; empty = trust none
    trusted_proxies: str = ""

    @field_validator("jwt_secret")
    @classmethod
    def jwt_secret_long_enough(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return v


settings = Settings()
