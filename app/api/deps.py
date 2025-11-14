from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.security import decode_access_token
from app.crud.user import get_user_by_username
from app.database import get_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username = payload.get("sub")
    if username is None or not isinstance(username, str):
        raise credentials_exception

    user = get_user_by_username(session, username)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    return current_user


def require_role(required_role: str):
    """Dependency factory to require a specific role."""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.role or current_user.role.name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        return current_user
    return role_checker


def require_admin_or_teacher(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require admin or teacher role."""
    if not current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role not found"
        )

    if current_user.role.name not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin or teacher role"
        )

    return current_user


def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require admin role."""
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin role"
        )
    return current_user

