from typing import List

from sqlmodel import Session, select

from app.models.role import Role


def get_roles(session: Session) -> List[Role]:
    """Get all roles."""
    statement = select(Role)
    return list(session.exec(statement).all())


def get_role_by_id(session: Session, role_id: int) -> Role | None:
    """Get role by ID."""
    return session.get(Role, role_id)


def get_role_by_name(session: Session, name: str) -> Role | None:
    """Get role by name."""
    statement = select(Role).where(Role.name == name)
    return session.exec(statement).first()

