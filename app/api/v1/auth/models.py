# app/api/v1/auth/models.py
from typing import List

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """
    User model.
    """
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    items = relationship("Item", back_populates="owner")




# app/api/v1/auth/utils.py
from datetime import datetime
from typing import Optional
from uuid import UUID

from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.models import User
from app.core.config import settings
from app.core.security import verify_password


async def check_user_exists(
    db: AsyncSession,
    user_id: UUID,
) -> bool:
    """
    Check if a user exists.
    
    Args:
        db: Database session
        user_id: ID of the user to check
        
    Returns:
        True if the user exists, False otherwise
    """
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalars().first() is not None


async def validate_token(
    token: str,
) -> Optional[dict]:
    """
    Validate a JWT token.
    
    Args:
        token: The token to validate
        
    Returns:
        The token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            return None
        
        return payload
    except jwt.JWTError:
        return None


async def check_password(
    db: AsyncSession,
    user_id: UUID,
    password: str,
) -> bool:
    """
    Check if a password is correct for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        password: Password to check
        
    Returns:
        True if the password is correct, False otherwise
    """
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        return False
    
    return verify_password(password, user.hashed_password)