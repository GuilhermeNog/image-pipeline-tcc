from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Image Pipeline"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/image_pipeline"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@postgres:5432/image_pipeline"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_ACCESS_SECRET: str = "change-me"
    JWT_REFRESH_SECRET: str = "change-me"
    JWT_ACCESS_EXPIRATION_MINUTES: int = 15
    JWT_REFRESH_EXPIRATION_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"
    STORAGE_PATH: str = "./storage"

    MAX_UPLOAD_SIZE_MB: int = 10
    MAX_PIPELINE_OPERATIONS: int = 20
    JOB_TIMEOUT_SECONDS: int = 300

    BCRYPT_ROUNDS: int = 12

    ACCOUNT_LOCKOUT_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15

    EMAIL_VERIFICATION_EXPIRY_MINUTES: int = 15
    PASSWORD_RESET_EXPIRY_MINUTES: int = 15

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@imagepipeline.local"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
