from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Index, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class NounGroupNoun(SQLModel, table=True):
    """Many-to-many relationship between noun groups and nouns."""

    __tablename__ = "noun_group_nouns"

    id_group: int = Field(foreign_key="noun_groups.id", primary_key=True)
    id_noun: int = Field(foreign_key="nouns.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class Noun(SQLModel, table=True):
    """Noun model for Russian nouns with full declension support."""

    __tablename__ = "nouns"

    id: Optional[int] = Field(default=None, primary_key=True)
    noun: str = Field(max_length=100, unique=True, index=True)
    gender: str = Field(max_length=10)  # masculine, feminine, neuter
    translations: List[Dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )

    # Store complete declension data as JSON
    declension: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    noun_groups: List["NounGroup"] = Relationship(
        back_populates="nouns", link_model=NounGroupNoun
    )

    # Indexes
    __table_args__ = (
        Index("idx_noun_noun", "noun", unique=True),
        Index("idx_noun_translations", "translations"),
        Index("idx_noun_gender", "gender"),
    )


class NounGroup(SQLModel, table=True):
    """Noun group model for organizing nouns."""

    __tablename__ = "noun_groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    name_group: str = Field(max_length=100)
    id_user: int = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    user: "User" = Relationship(back_populates="noun_groups")
    nouns: List["Noun"] = Relationship(
        back_populates="noun_groups", link_model=NounGroupNoun
    )
