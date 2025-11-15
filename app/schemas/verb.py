from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.traslation import Translation


class VerbConjugations(BaseModel):
    """Schema for verb conjugations grouped by tense."""
    present: dict[str, str]
    past: dict[str, str]
    future: dict[str, str]
    imperative: dict[str, str]


class VerbBase(BaseModel):
    """Base verb schema."""
    infinitive: str = Field(max_length=100)
    conjugationType: int = Field(ge=1, le=2)
    root: str = Field(max_length=100)
    translations: list[Translation] = Field(default=[])
    present_ya: str = Field(max_length=50)
    present_ty: str = Field(max_length=50)
    present_on_ona: str = Field(max_length=50)
    present_my: str = Field(max_length=50)
    present_vy: str = Field(max_length=50)
    present_oni: str = Field(max_length=50)
    past_masculine: str = Field(max_length=50)
    past_feminine: str = Field(max_length=50)
    past_neuter: str = Field(max_length=50)
    past_plural: str = Field(max_length=50)
    future_ya: str = Field(max_length=50)
    future_ty: str = Field(max_length=50)
    future_on_ona: str = Field(max_length=50)
    future_my: str = Field(max_length=50)
    future_vy: str = Field(max_length=50)
    future_oni: str = Field(max_length=50)
    imperative_singular: str = Field(max_length=50)
    imperative_plural: str = Field(max_length=50)


class VerbCreate(VerbBase):
    """Schema for creating a verb."""
    pass


class VerbUpdate(BaseModel):
    """Schema for updating a verb."""
    infinitive: Optional[str] = Field(default=None, max_length=100)
    conjugationType: Optional[int] = Field(default=None, ge=1, le=2)
    root: Optional[str] = Field(default=None, max_length=100)
    translations: Optional[list[Translation]] = Field(default=None)
    present_ya: Optional[str] = Field(default=None, max_length=50)
    present_ty: Optional[str] = Field(default=None, max_length=50)
    present_on_ona: Optional[str] = Field(default=None, max_length=50)
    present_my: Optional[str] = Field(default=None, max_length=50)
    present_vy: Optional[str] = Field(default=None, max_length=50)
    present_oni: Optional[str] = Field(default=None, max_length=50)
    past_masculine: Optional[str] = Field(default=None, max_length=50)
    past_feminine: Optional[str] = Field(default=None, max_length=50)
    past_neuter: Optional[str] = Field(default=None, max_length=50)
    past_plural: Optional[str] = Field(default=None, max_length=50)
    future_ya: Optional[str] = Field(default=None, max_length=50)
    future_ty: Optional[str] = Field(default=None, max_length=50)
    future_on_ona: Optional[str] = Field(default=None, max_length=50)
    future_my: Optional[str] = Field(default=None, max_length=50)
    future_vy: Optional[str] = Field(default=None, max_length=50)
    future_oni: Optional[str] = Field(default=None, max_length=50)
    imperative_singular: Optional[str] = Field(default=None, max_length=50)
    imperative_plural: Optional[str] = Field(default=None, max_length=50)


class VerbResponse(VerbBase):
    """Schema for verb response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VerbWithConjugations(VerbResponse):
    """Verb response with conjugations grouped by tense."""
    present: dict[str, str]
    past: dict[str, str]
    future: dict[str, str]
    imperative: dict[str, str]

    @classmethod
    def from_orm(cls, verb):
        """Create from ORM object with grouped conjugations."""
        data = {
            "id": verb.id,
            "infinitive": verb.infinitive,
            "conjugationType": verb.conjugationType,
            "root": verb.root,
            "present": {
                "ya": verb.present_ya,
                "ty": verb.present_ty,
                "on_ona": verb.present_on_ona,
                "my": verb.present_my,
                "vy": verb.present_vy,
                "oni": verb.present_oni,
            },
            "past": {
                "masculine": verb.past_masculine,
                "feminine": verb.past_feminine,
                "neuter": verb.past_neuter,
                "plural": verb.past_plural,
            },
            "future": {
                "ya": verb.future_ya,
                "ty": verb.future_ty,
                "on_ona": verb.future_on_ona,
                "my": verb.future_my,
                "vy": verb.future_vy,
                "oni": verb.future_oni,
            },
            "imperative": {
                "singular": verb.imperative_singular,
                "plural": verb.imperative_plural,
            },
            "created_at": verb.created_at,
            "updated_at": verb.updated_at,
        }
        return cls(**data)


class VerbGroupBase(BaseModel):
    """Base verb group schema."""
    name_group: str = Field(max_length=100)


class VerbGroupCreate(VerbGroupBase):
    """Schema for creating a verb group."""
    pass


class VerbGroupUpdate(BaseModel):
    """Schema for updating a verb group."""
    name_group: Optional[str] = Field(default=None, max_length=100)


class VerbGroupResponse(VerbGroupBase):
    """Schema for verb group response."""
    id: int
    id_user: int
    created_at: datetime
    updated_at: datetime
    verbs: Optional[List[VerbResponse]] = None

    class Config:
        from_attributes = True

