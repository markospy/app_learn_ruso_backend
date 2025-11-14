from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_active_user, require_admin
from app.crud.user import delete_user, get_user_by_id, get_users, update_user
from app.database import get_session
from app.models.user import User
from app.schemas.user import UserPublic, UserResponse, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Get current user's profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> UserResponse:
    """Update current user's profile."""
    updated_user = update_user(session, current_user, user_update)
    return UserResponse.model_validate(updated_user)


@router.get("/{user_id}", response_model=UserPublic)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> UserPublic:
    """Get user by ID (admin or teacher only)."""
    if current_user.role and current_user.role.name not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin or teacher role"
        )

    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserPublic.model_validate(user)


@router.get("", response_model=List[UserPublic])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> List[UserPublic]:
    """List all users (admin only)."""
    users = get_users(session, skip=skip, limit=limit)
    return [UserPublic.model_validate(user) for user in users]


@router.put("/{user_id}", response_model=UserResponse)
def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> UserResponse:
    """Update user by ID (admin only)."""
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    updated_user = update_user(session, user, user_update)
    return UserResponse.model_validate(updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(
    user_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> None:
    """Delete user by ID (admin only)."""
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    delete_user(session, user)

