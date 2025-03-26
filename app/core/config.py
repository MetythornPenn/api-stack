import os
import secrets
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseType(str, Enum):
    POSTGRES = "postgres"
    ORACLE = "oracle"


class AppEnvironment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('APP_ENV', 'local')}",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Core settings
    APP_ENV: AppEnvironment = AppEnvironment.LOCAL
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database settings
    DATABASE_TYPE: DatabaseType = DatabaseType.POSTGRES
    
    # PostgreSQL settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    POSTGRES_PORT: str = "5432"
    
    # Oracle settings
    ORACLE_SERVER: str = "localhost"
    ORACLE_USER: str = "system"
    ORACLE_PASSWORD: str = "oracle"
    ORACLE_SERVICE: str = "xe"
    ORACLE_PORT: str = "1521"
    
    # Construct SQLAlchemy database URI based on selected database type
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_TYPE == DatabaseType.POSTGRES:
            return str(
                PostgresDsn.build(
                    scheme="postgresql+asyncpg",
                    username=self.POSTGRES_USER,
                    password=self.POSTGRES_PASSWORD,
                    host=self.POSTGRES_SERVER,
                    port=int(self.POSTGRES_PORT),
                    path=f"/{self.POSTGRES_DB or ''}",
                )
            )
        elif self.DATABASE_TYPE == DatabaseType.ORACLE:
            # Oracle connection string for async operations using oracledb
            return f"oracle+oracledb://{self.ORACLE_USER}:{self.ORACLE_PASSWORD}@{self.ORACLE_SERVER}:{self.ORACLE_PORT}/?service_name={self.ORACLE_SERVICE}"
        raise ValueError(f"Unsupported database type: {self.DATABASE_TYPE}")

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Cache settings
    CACHE_EXPIRATION_SECONDS: int = 60 * 5  # 5 minutes
    
    # MinIO settings
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "media"
    MINIO_SECURE: bool = False
    
    # API settings
    DISABLE_DOCS: bool = False
    
    @property
    def DOCS_URL(self) -> Optional[str]:
        return None if (self.DISABLE_DOCS or self.APP_ENV == AppEnvironment.PROD) else "/docs"
    
    @property
    def REDOC_URL(self) -> Optional[str]:
        return None if (self.DISABLE_DOCS or self.APP_ENV == AppEnvironment.PROD) else "/redoc"
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_SECOND: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Project base directory
    PROJECT_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Create global settings object
settings = Settings()
