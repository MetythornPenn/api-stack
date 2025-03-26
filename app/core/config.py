# app/core/config.py
import os
import secrets
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, Field, PostgresDsn, OracleDsn, RedisDsn, validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    LOCAL = "local"
    PRODUCTION = "prod"


class DatabaseType(str, Enum):
    POSTGRES = "postgres"
    ORACLE = "oracle"


class Settings(BaseSettings):
    # Base
    ENV: Environment = Environment.LOCAL
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    PROJECT_NAME: str = "FastAPI Boilerplate"
    
    # Database
    DATABASE_TYPE: DatabaseType = DatabaseType.POSTGRES
    
    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DATABASE_URI: Optional[PostgresDsn] = None
    
    # Oracle
    ORACLE_SERVER: str = "localhost"
    ORACLE_USER: str = "oracle"
    ORACLE_PASSWORD: str = "oracle"
    ORACLE_DB: str = "app"
    ORACLE_PORT: str = "1521"
    ORACLE_DATABASE_URI: Optional[OracleDsn] = None
    
    # Redis
    REDIS_SERVER: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_URI: Optional[RedisDsn] = None
    
    # MinIO
    MINIO_SERVER: str = "localhost"
    MINIO_PORT: str = "9000"
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "app-bucket"
    
    # Security
    ALGORITHM: str = "HS256"
    SWAGGER_UI_ENABLED: bool = True
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # Cache settings
    CACHE_ENABLED: bool = True
    CACHE_EXPIRE_SECONDS: int = 60 * 5  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("POSTGRES_DATABASE_URI", pre=True)
    def assemble_postgres_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    @validator("ORACLE_DATABASE_URI", pre=True)
    def assemble_oracle_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return OracleDsn.build(
            scheme="oracle+oracledb",
            username=values.get("ORACLE_USER"),
            password=values.get("ORACLE_PASSWORD"),
            host=values.get("ORACLE_SERVER"),
            port=values.get("ORACLE_PORT"),
            path=f"/{values.get('ORACLE_DB') or ''}",
        )
    
    @validator("REDIS_URI", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        password_part = f":{values.get('REDIS_PASSWORD')}@" if values.get("REDIS_PASSWORD") else ""
        return f"redis://{password_part}{values.get('REDIS_SERVER')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
    
    @property
    def DATABASE_URI(self) -> str:
        if self.DATABASE_TYPE == DatabaseType.POSTGRES:
            return str(self.POSTGRES_DATABASE_URI)
        elif self.DATABASE_TYPE == DatabaseType.ORACLE:
            return str(self.ORACLE_DATABASE_URI)
        raise ValueError(f"Unsupported database type: {self.DATABASE_TYPE}")

    class Config:
        env_file = f".env.{os.getenv('APP_ENV', 'local')}"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


