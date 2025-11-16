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


class CaseForms(BaseModel):
    """Schema for case forms (all 6 cases)."""
    nominative: WordForm
    genitive: WordForm
    dative: WordForm
    accusative: WordForm
    instrumental: WordForm
    prepositional: WordForm


class Declension(BaseModel):
    """Schema for noun declension."""
    singular: CaseForms
    plural: CaseForms


class NounBase(BaseModel):
    """Base noun schema with full declension support."""
    noun: str = Field(max_length=100)
    gender: str = Field(max_length=10)  # masculine, feminine, neuter
    translations: List[TranslationSchema] = Field(default_factory=list)
    declension: Declension


class NounCreate(NounBase):
    """Schema for creating a noun."""
    pass


class NounUpdate(BaseModel):
    """Schema for updating a noun."""
    noun: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[str] = Field(default=None, max_length=10)
    translations: Optional[List[TranslationSchema]] = None
    declension: Optional[Dict[str, Any]] = None


class NounResponse(NounBase):
    """Schema for noun response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NounGroupBase(BaseModel):
    """Base noun group schema."""
    name_group: str = Field(max_length=100)


class NounGroupCreate(NounGroupBase):
    """Schema for creating a noun group."""
    pass


class NounGroupUpdate(BaseModel):
    """Schema for updating a noun group."""
    name_group: Optional[str] = Field(default=None, max_length=100)


class NounGroupResponse(NounGroupBase):
    """Schema for noun group response."""
    id: int
    id_user: int
    created_at: datetime
    updated_at: datetime
    nouns: Optional[List[NounResponse]] = None

    class Config:
        from_attributes = True
