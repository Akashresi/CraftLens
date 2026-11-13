import secrets
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "CraftLens 2.0"
    API_V1_STR: str = "/api/v1"

    # Security - dynamically generated ephemeral key in dev if unset; mandatory via env in prod
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15

    # Upload limits & malware scan hook
    MAX_IMAGE_UPLOAD_BYTES: int = 10 * 1024 * 1024
    MAX_AUDIO_UPLOAD_BYTES: int = 15 * 1024 * 1024
    CLAMAV_HOST: str = ""
    CLAMAV_PORT: int = 3310

    # Server Binding
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    AI_SERVICE_URL: str = "http://127.0.0.1:8001"
    PUBLIC_WEB_BASE_URL: str = "http://localhost:3000"

    # Strict CORS Allowlist (no wildcard '*')
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8081",
        "exp://localhost:8081",
    ]

    # Database & Redis
    DATABASE_URL: str = "sqlite:///./craftlens_dev.db"
    REDIS_URL: str = ""

    # Storage
    STORAGE_PROVIDER: str = "local"
    LOCAL_UPLOAD_DIR: str = "./uploads"

    # Provenance Signing (Ed25519 PEM; generated ephemerally in dev if unset)
    HERITAGE_ED25519_PRIVATE_KEY_PEM: str = ""

    # External AI / LLM
    GEMINI_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Indian Language Speech & Translation
    BHASHINI_USER_ID: str = ""
    BHASHINI_API_KEY: str = ""
    BHASHINI_PIPELINE_ID: str = ""
    ASR_FALLBACK: str = "whisper_local"

    # Payment, Shipping & Notification Providers (from env)
    PAYMENT_GATEWAY: str = "razorpay_sandbox"
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    SHIPPING_PROVIDER: str = "shiprocket_sandbox"
    SHIPROCKET_TOKEN: str = ""
    NOTIFICATION_PROVIDER: str = "sandbox_inapp"

    # DPDP Act 2023 Grievance Contact
    DPDP_GRIEVANCE_OFFICER_NAME: str = "CraftLens Data Protection & Grievance Officer"
    DPDP_GRIEVANCE_OFFICER_EMAIL: str = "grievance@craftlens.org"
    DPDP_GRIEVANCE_OFFICER_PHONE: str = "+91-11-2338-0000"

    # Observability
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    @property
    def resolved_database_url(self) -> str:
        """Resolves relative SQLite database URLs to an absolute path anchored at the backend directory."""
        if self.DATABASE_URL.startswith("sqlite:///") and not self.DATABASE_URL.startswith("sqlite:////"):
            rel_path = self.DATABASE_URL.replace("sqlite:///", "")
            if rel_path.startswith("./"):
                rel_path = rel_path[2:]
            backend_dir = Path(__file__).resolve().parents[2]
            abs_db_path = (backend_dir / rel_path).resolve()
            return f"sqlite:///{abs_db_path.as_posix()}"
        return self.DATABASE_URL

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.APP_ENV.lower() == "production":
            insecure = not self.SECRET_KEY or "replace-this" in self.SECRET_KEY.lower() or len(self.SECRET_KEY) < 32
            if insecure:
                raise ValueError("SECRET_KEY must be set to a strong >=32-char env secret in production")
            if "*" in self.CORS_ORIGINS:
                raise ValueError("Wildcard '*' is forbidden in CORS_ORIGINS in production")
        return self

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")


settings = Settings()
