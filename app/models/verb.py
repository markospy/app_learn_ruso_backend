from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Index, Relationship, SQLModel

from app.schemas.traslation import Translation

if TYPE_CHECKING:
    from app.models.user import User


class VerbGroupVerb(SQLModel, table=True):
    """Many-to-many relationship between verb groups and verbs."""

    __tablename__ = "verb_group_verbs"

    id_group: int = Field(foreign_key="verb_groups.id", primary_key=True)
    id_verb: int = Field(foreign_key="verbs.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class Verb(SQLModel, table=True):
    """Verb model for Russian verb conjugations."""

    __tablename__ = "verbs"

    id: Optional[int] = Field(default=None, primary_key=True)
    infinitive: str = Field(max_length=100, unique=True, index=True)
    translations: list[Translation] = Field(default=[])
    conjugationType: int = Field()  # 1 or 2
    root: str = Field(max_length=100)

    # Present tense
    present_ya: str = Field(max_length=50)
    present_ty: str = Field(max_length=50)
    present_on_ona: str = Field(max_length=50)
    present_my: str = Field(max_length=50)
    present_vy: str = Field(max_length=50)
    present_oni: str = Field(max_length=50)

    # Past tense
    past_masculine: str = Field(max_length=50)
    past_feminine: str = Field(max_length=50)
    past_neuter: str = Field(max_length=50)
    past_plural: str = Field(max_length=50)

    # Future tense
    future_ya: str = Field(max_length=50)
    future_ty: str = Field(max_length=50)
    future_on_ona: str = Field(max_length=50)
    future_my: str = Field(max_length=50)
    future_vy: str = Field(max_length=50)
    future_oni: str = Field(max_length=50)

    # Imperative
    imperative_singular: str = Field(max_length=50)
    imperative_plural: str = Field(max_length=50)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    verb_groups: List["VerbGroup"] = Relationship(
        back_populates="verbs", link_model=VerbGroupVerb
    )
    # Indexes
    __table_args__ = (
        Index("idx_verb_translations", "translations"),
        Index("idx_verb_infinitive", "infinitive", unique=True),
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

