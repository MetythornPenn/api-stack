
# app/api/v1/auth/schemas.py
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """
    Base schema for User.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    """
    Schema for creating a new User.
    """
    email: EmailStr
    username: str
    password: str = Field(..., min_length=8)


class UserUpdate(UserBase):
    """
    Schema for updating a User.
    """
    password: Optional[str] = Field(None, min_length=8)


class UserOut(UserBase):
    """
    Schema for User response.
    """
    id: str
    email: EmailStr
    username: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """
    Schema for User in the database.
    """
    id: UUID
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """
    Schema for JWT token.
    """
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Schema for JWT token payload.
    """
    sub: str
    exp: float
    jti: str


class LoginRequest(BaseModel):
    """
    Schema for login request.
    """
    username: str
    password: str

