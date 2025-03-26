
# app/api/v1/auth/service.py
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.models import User
from app.api.v1.auth.schemas import UserCreate, UserInDB, UserUpdate
from app.core.config import settings
from app.core.security import create_access_token, create_password_hash, verify_password
from app.db.base import CRUDBase


class UserService(CRUDBase[User, UserCreate, UserUpdate]):
    """
    Service for User operations.
    """
    
    async def get_by_email_or_username(
        self,
        db: AsyncSession,
        *,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> Optional[User]:
        """
        Get a User by email or username.
        """
        if not email and not username:
            return None
        
        query = select(User)
        
        if email and username:
            query = query.where(or_(User.email == email, User.username == username))
        elif email:
            query = query.where(User.email == email)
        else:
            query = query.where(User.username == username)
        
        result = await db.execute(query)
        return result.scalars().first()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: UserCreate,
    ) -> User:
        """
        Create a new User.
        """
        # Check if user already exists
        existing_user = await self.get_by_email_or_username(
            db,
            email=obj_in.email,
            username=obj_in.username,
        )
        
        if existing_user:
            return None
        
        # Create new user
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=create_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> User:
        """
        Update a User.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        if update_data.get("password"):
            hashed_password = create_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def authenticate(
        self,
        db: AsyncSession,
        *,
        username: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate a User.
        """
        user = await self.get_by_email_or_username(db, username=username)
        
        if not user:
            # Try with email
            user = await self.get_by_email_or_username(db, email=username)
            
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def create_token(
        self,
        user_id: Union[str, uuid.UUID],
    ) -> Dict[str, str]:
        """
        Create a JWT token for a User.
        """
        # Generate a unique token ID
        jti = str(uuid.uuid4())
        
        # Generate the token
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            subject=str(user_id),
            expires_delta=expires_delta,
            extra_data={"jti": jti},
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
        }


user_service = UserService(User)
