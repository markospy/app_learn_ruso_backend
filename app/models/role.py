from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Role(SQLModel, table=True):
    """Role model for user roles (admin, teacher, student)."""

    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True, index=True)

    # Relationships
    users: List["User"] = Relationship(back_populates="role")

