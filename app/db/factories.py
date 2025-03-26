
# app/db/factories.py
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings, DatabaseType


def get_engine() -> AsyncEngine:
    """
    Create database engine based on the configured database type.
    """
    if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
        # For PostgreSQL with pgvector
        connect_args = {
            "server_settings": {
                "search_path": "public",
                # Load pgvector extension on connection
                "options": "-c search_path=public -c shared_preload_libraries=pgvector"
            }
        }
        
        return create_async_engine(
            settings.DATABASE_URI,
            future=True,
            echo=settings.ENV == "local",
            connect_args=connect_args,
            pool_pre_ping=True,
        )
    elif settings.DATABASE_TYPE == DatabaseType.ORACLE:
        # For Oracle
        return create_async_engine(
            settings.DATABASE_URI,
            future=True,
            echo=settings.ENV == "local",
            pool_pre_ping=True,
        )
    else:
        raise ValueError(f"Unsupported database type: {settings.DATABASE_TYPE}")


def get_session_factory(engine: AsyncEngine) -> sessionmaker:
    """
    Create session factory for the given engine.
    """
    return sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
