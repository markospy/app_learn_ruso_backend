from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_active_user
from app.config import settings
from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.database import get_session
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, Token
from app.schemas.user import UserPublic

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(
    register_data: RegisterRequest,
    session: Session = Depends(get_session),
) -> Token:
    """Register a new user."""
    # Check if username already exists
    if get_user_by_username(session, register_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    if get_user_by_email(session, register_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = create_user(session, register_data)

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic.model_validate(user)
    )


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session),
) -> Token:
    """Login and get access token."""
    user = get_user_by_username(session, login_data.username)

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic.model_validate(user)
    )


@router.get("/me", response_model=UserPublic)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> UserPublic:
    """Get current authenticated user information."""
    return UserPublic.model_validate(current_user)

