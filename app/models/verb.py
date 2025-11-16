from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Index, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class VerbGroupVerb(SQLModel, table=True):
    """Many-to-many relationship between verb groups and verbs."""

    __tablename__ = "verb_group_verbs"

    id_group: int = Field(foreign_key="verb_groups.id", primary_key=True)
    id_verb: int = Field(foreign_key="verbs.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class Verb(SQLModel, table=True):
    """Verb model for Russian verb conjugations with full grammar support."""

    __tablename__ = "verbs"

    id: Optional[int] = Field(default=None, primary_key=True)
    verb_pair_id: str = Field(max_length=200, unique=True, index=True)
    translations: List[Dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    conjugation_type: int = Field()  # 1 or 2
    root: str = Field(max_length=100)
    stress_pattern: Optional[str] = Field(default=None, max_length=50)

    # Store complete verb data as JSON
    imperfective: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    perfective: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    verb_groups: List["VerbGroup"] = Relationship(
        back_populates="verbs", link_model=VerbGroupVerb
    )

    # Indexes
    __table_args__ = (
        Index("idx_verb_pair_id", "verb_pair_id", unique=True),
        Index("idx_verb_translations", "translations"),
        Index("idx_verb_conjugation_type", "conjugation_type"),
    )


class VerbGroup(SQLModel, table=True):
    """Verb group model for organizing verbs."""

    __tablename__ = "verb_groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    name_group: str = Field(max_length=100)
    id_user: int = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    user: "User" = Relationship(back_populates="verb_groups")
    verbs: List["Verb"] = Relationship(
        back_populates="verb_groups", link_model=VerbGroupVerb
    )
