from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///:memory:"
    JWT_SECRET_KEY: str = "test"
    REDIS_URL: str = "redis://redis:6379"
    SENTRY_DSN: str = "https://0440ba3c5ae190d6c8d413f40af5d778@sentry.hamravesh.com/9385"

    MAIL_PASSWORD: str = ""
    MAIL_USERNAME: str = ""
    MAIL_FROM: str = "no-reply@example.com"
    MAIL_PORT: int = 25
    MAIL_SERVER: str = "smtp4dev"
    MAIL_FROM_NAME: str = "Admin"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool =False

    CELERY_BROKER_URL: str = "redis://redis:6379/3"
    CELERY_BACKEND_URL: str = "redis://redis:6379/3"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
