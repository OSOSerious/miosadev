# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "MIOSA"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(..., validation_alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - PostgreSQL with asyncpg
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(..., validation_alias="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="miosa")
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    
    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    # Groq API (Latest SDK v0.30.0)
    GROQ_API_KEY: str = Field(..., validation_alias="GROQ_API_KEY")
    GROQ_MODEL: str = Field(default="moonshotai/kimi-k2-instruct")  # Default to Kimi K2
    
    # Frontend
    FRONTEND_URL: str = Field(default="http://localhost:5173")
    
    # CORS
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"])
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()