from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class Noun(SQLModel, table=True):
    """Noun model for Russian nouns."""

    __tablename__ = "nouns"

    id: Optional[int] = Field(default=None, primary_key=True)
    sustantivo: str = Field(max_length=100)
    singular: str = Field(max_length=100)
    plural: str = Field(max_length=100)
    gender: str = Field(max_length=10)  # masculine, feminine, neuter
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    noun_groups: List["NounGroupNoun"] = Relationship(back_populates="noun")


class NounGroup(SQLModel, table=True):
    """Noun group model for organizing nouns."""

    __tablename__ = "noun_groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    name_group: str = Field(max_length=100)
    id_user: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="noun_groups")
    nouns: List["NounGroupNoun"] = Relationship(back_populates="group")


class NounGroupNoun(SQLModel, table=True):
    """Many-to-many relationship between noun groups and nouns."""

    __tablename__ = "noun_group_nouns"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_group: int = Field(foreign_key="noun_groups.id", ondelete="CASCADE")
    id_noun: int = Field(foreign_key="nouns.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    group: NounGroup = Relationship(back_populates="nouns")
    noun: Noun = Relationship(back_populates="noun_groups")

