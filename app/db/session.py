from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create async engine according to the configured database URI
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=settings.APP_ENV == "local",
    future=True,
)

# Create sessionmaker for async sessions
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


# Dependency to get db session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async DB session.
    
    Yields:
        AsyncSession: SQLAlchemy async session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise