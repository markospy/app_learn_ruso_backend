from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WordForm(BaseModel):
    """Schema for a word form with accent and phonetics."""
    word: str
    accent: str
    phonetics: str


class TranslationSchema(BaseModel):
    """Schema for translations by language."""
    es: Optional[List[str]] = None
    en: Optional[List[str]] = None
    pt: Optional[List[str]] = None
    # Add more languages as needed


class VerbInfinitive(BaseModel):
    """Schema for infinitive form."""
    word: WordForm


class VerbTenseForms(BaseModel):
    """Schema for tense forms (present, past, future)."""
    ya: Optional[WordForm] = None
    ty: Optional[WordForm] = None
    on_ona: Optional[WordForm] = None
    my: Optional[WordForm] = None
    vy: Optional[WordForm] = None
    oni: Optional[WordForm] = None


class VerbPastTenseForms(BaseModel):
    """Schema for past tense forms."""
    masculine: Optional[WordForm] = None
    feminine: Optional[WordForm] = None
    neuter: Optional[WordForm] = None
    plural: Optional[WordForm] = None


class ImperfectiveAspect(BaseModel):
    """Schema for imperfective aspect conjugations."""
    infinitive: VerbInfinitive
    present_tense: VerbTenseForms
    past_tense: VerbPastTenseForms


class PerfectiveAspect(BaseModel):
    """Schema for perfective aspect conjugations."""
    infinitive: VerbInfinitive
    future_simple: VerbTenseForms


class VerbBase(BaseModel):
    """Base verb schema with full grammar support."""
    verb_pair_id: str = Field(max_length=200)
    translations: List[TranslationSchema] = Field(default_factory=list)
    conjugation_type: int = Field(ge=1, le=2, alias="conjugationType")
    root: str = Field(max_length=100)
    stress_pattern: Optional[str] = Field(default=None, max_length=50)
    imperfective: ImperfectiveAspect
    perfective: PerfectiveAspect

    class Config:
        populate_by_name = True


class VerbCreate(VerbBase):
    """Schema for creating a verb."""
    pass


class VerbUpdate(BaseModel):
    """Schema for updating a verb."""
    verb_pair_id: Optional[str] = Field(default=None, max_length=200)
    translations: Optional[List[TranslationSchema]] = None
    conjugation_type: Optional[int] = Field(default=None, ge=1, le=2, alias="conjugationType")
    root: Optional[str] = Field(default=None, max_length=100)
    stress_pattern: Optional[str] = Field(default=None, max_length=50)
    imperfective: Optional[Dict[str, Any]] = None
    perfective: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class VerbResponse(VerbBase):
    """Schema for verb response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


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
