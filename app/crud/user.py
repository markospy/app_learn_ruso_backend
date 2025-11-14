from typing import Optional

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """Get user by username."""
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(session: Session, user_create: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user_create.password)
    user = User(
        name=user_create.name,
        country=user_create.country,
        email=user_create.email,
        username=user_create.username,
        password=hashed_password,
        language=user_create.language,
        id_rol=user_create.id_rol,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(session: Session, user: User, user_update: UserUpdate) -> User:
    """Update user information."""
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users with pagination."""
    statement = select(User).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def delete_user(session: Session, user: User) -> None:
    """Delete a user."""
    session.delete(user)
    session.commit()

