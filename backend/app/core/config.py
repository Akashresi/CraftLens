import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "CraftLens 2.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "craftlens-dev-secret-key-super-secure-at-least-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days for development
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Server Binding
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    AI_SERVICE_URL: str = "http://127.0.0.1:8001"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8081",
        "exp://localhost:8081",
        "*",
    ]

    # Database
    DATABASE_URL: str = "sqlite:///./craftlens_dev.db"
    
    # Storage
    STORAGE_PROVIDER: str = "local"
    LOCAL_UPLOAD_DIR: str = "./uploads"
    
    # External AI / LLM
    GEMINI_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Indian Language Speech & Translation
    BHASHINI_USER_ID: str = ""
    BHASHINI_API_KEY: str = ""
    BHASHINI_PIPELINE_ID: str = ""

    # Payment Gateway
    PAYMENT_GATEWAY: str = "sandbox"
    RAZORPAY_KEY_ID: str = "rzp_test_sampleKey12345"
    RAZORPAY_KEY_SECRET: str = "sampleSecretForTesting12345"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
