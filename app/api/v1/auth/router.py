
# app/api/v1/auth/router.py
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_current_superuser
from app.api.v1.auth.schemas import LoginRequest, Token, UserCreate, UserOut, UserUpdate
from app.api.v1.auth.service import user_service
from app.core.db import get_db
from app.services.ratelimit import rate_limit

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    dependencies=[Depends(rate_limit())],
)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """
    Register a new user.
    
    - **email**: User's email
    - **username**: User's username
    - **password**: User's password (min 8 characters)
    - **full_name**: Optional full name
    """
    # Check if user already exists
    existing_user = await user_service.get_by_email_or_username(
        db,
        email=user_in.email,
        username=user_in.username,
    )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )
    
    # Create new user (without superuser privileges)
    user_data = user_in.model_dump()
    user_data["is_superuser"] = False  # Ensure no one can register as superuser
    
    user = await user_service.create(db, obj_in=UserCreate(**user_data))
    
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    dependencies=[Depends(rate_limit(requests=10, window_seconds=60))],
)
async def login(
    login_in: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Login to get access token.
    
    - **username**: Username or email
    - **password**: User's password
    """
    user = await user_service.authenticate(
        db,
        username=login_in.username,
        password=login_in.password,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Create access token
    token_data = user_service.create_token(user.id)
    
    return Token(**token_data)


@router.post(
    "/login/token",
    response_model=Token,
    summary="OAuth2 compatible token login",
    dependencies=[Depends(rate_limit(requests=10, window_seconds=60))],
)
async def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await user_service.authenticate(
        db,
        username=form_data.username,
        password=form_data.password,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Create access token
    token_data = user_service.create_token(user.id)
    
    return Token(**token_data)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user",
    dependencies=[Depends(rate_limit())],
)
async def get_me(
    current_user: UserOut = Depends(get_current_active_user),
) -> UserOut:
    """
    Get current user.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserOut,
    summary="Update current user",
    dependencies=[Depends(rate_limit())],
)
async def update_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user),
) -> UserOut:
    """
    Update current user.
    
    - **email**: Optional new email
    - **username**: Optional new username
    - **password**: Optional new password (min 8 characters)
    - **full_name**: Optional new full name
    """
    # Get current user from database
    db_user = await user_service.get(db, id=current_user.id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if email or username already exists
    if user_in.email and user_in.email != db_user.email:
        existing_user = await user_service.get_by_email_or_username(
            db,
            email=user_in.email,
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    if user_in.username and user_in.username != db_user.username:
        existing_user = await user_service.get_by_email_or_username(
            db,
            username=user_in.username,
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
    
    # Ensure user can't change their superuser status
    user_data = user_in.model_dump(exclude_unset=True)
    if "is_superuser" in user_data:
        del user_data["is_superuser"]
    
    # Update user
    user = await user_service.update(
        db,
        db_obj=db_user,
        obj_in=user_data,
    )
    
    return user


@router.get(
    "/users",
    response_model=list[UserOut],
    summary="Get all users",
    dependencies=[
        Depends(get_current_superuser),
        Depends(rate_limit()),
    ],
)
async def get_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> list[UserOut]:
    """
    Get all users. Requires superuser privileges.
    
    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return
    """
    users = await user_service.get_multi(db, skip=skip, limit=limit)
    return users
