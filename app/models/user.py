from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .noun import NounGroup
    from .role import Role
    from .verb import VerbGroup

from sqlmodel import Field, Relationship, SQLModel


class LinkStudentTeacher(SQLModel, table=True):
    """Link table for student-teacher relationships."""

    __tablename__ = "link_student_teacher"

    id_student: int = Field(foreign_key="users.id", primary_key=True)
    id_teacher: int = Field(foreign_key="users.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class User(SQLModel, table=True):
    """User model for authentication and user management."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    email: str = Field(max_length=255, unique=True, index=True)
    username: str = Field(max_length=50, unique=True, index=True)
    password: str = Field(max_length=255)
    language: str = Field(default="es", max_length=10)
    id_rol: int = Field(foreign_key="roles.id", ondelete="RESTRICT")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)

    # Relationships
    role: "Role" = Relationship(back_populates="users")
    verb_groups: List["VerbGroup"] = Relationship(back_populates="user")
    noun_groups: List["NounGroup"] = Relationship(back_populates="user")
    students: List["User"] = Relationship(
        back_populates="teachers",
        link_model=LinkStudentTeacher,
        sa_relationship_kwargs={
            "foreign_keys": "LinkStudentTeacher.id_teacher",
        },
    )
    teachers: List["User"] = Relationship(
        back_populates="students",
        link_model=LinkStudentTeacher,
        sa_relationship_kwargs={
            "foreign_keys": "LinkStudentTeacher.id_student",
        },
    )


