from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


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


def _normalize_word_form(value: Any) -> Dict[str, str]:
    """Normalize word form - accepts string or dict."""
    if isinstance(value, str):
        return {"word": value, "accent": value, "phonetics": ""}
    if isinstance(value, dict):
        return value
    return {"word": "", "accent": "", "phonetics": ""}


def _normalize_noun_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize noun structure to handle both simple and complex formats."""
    if not isinstance(data, dict):
        return data

    # Normalize declension
    if "declension" in data and isinstance(data["declension"], dict):
        declension = data["declension"]

        # Normalize singular
        if "singular" in declension and isinstance(declension["singular"], dict):
            for case in ["nominative", "genitive", "dative", "accusative", "instrumental", "prepositional"]:
                if case in declension["singular"]:
                    declension["singular"][case] = _normalize_word_form(declension["singular"][case])

        # Normalize plural
        if "plural" in declension and isinstance(declension["plural"], dict):
            for case in ["nominative", "genitive", "dative", "accusative", "instrumental", "prepositional"]:
                if case in declension["plural"]:
                    declension["plural"][case] = _normalize_word_form(declension["plural"][case])

    return data


def normalize_noun_for_response(noun: Any) -> Dict[str, Any]:
    """Normalize noun object/dict for NounResponse validation."""
    # Convert SQLModel object to dict if needed
    if hasattr(noun, "model_dump"):
        # Use model_dump with mode='json' to get JSON-serializable dict
        data = noun.model_dump(mode='json')
    elif hasattr(noun, "__dict__"):
        data = {}
        for k, v in noun.__dict__.items():
            if not k.startswith("_"):
                # Handle JSON fields that might be already parsed
                if k in ("declension", "translations"):
                    data[k] = v
                else:
                    data[k] = v
    elif isinstance(noun, dict):
        data = noun.copy()
    else:
        data = {}

    # Normalize translations
    if "translations" in data:
        translations = data["translations"]
        if isinstance(translations, dict):
            data["translations"] = [translations]
        elif not isinstance(translations, list):
            data["translations"] = []

    # Normalize declension structure
    data = _normalize_noun_structure(data)

    return data


class NounResponse(NounBase):
    """Schema for noun response."""
    id: int
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def normalize_data(cls, data: Any) -> Any:
        """Normalize noun data structure before validation."""
        # Handle SQLModel objects
        if not isinstance(data, dict):
            data = normalize_noun_for_response(data)
        else:
            # Normalize translations
            if "translations" in data:
                translations = data["translations"]
                if isinstance(translations, dict):
                    data["translations"] = [translations]
                elif not isinstance(translations, list):
                    data["translations"] = []

            # Normalize declension structure
            data = _normalize_noun_structure(data)

        return data

    @field_validator("translations", mode="before")
    @classmethod
    def normalize_translations(cls, v: Any) -> List[Dict[str, Any]]:
        """Convert translations from dict format to list format if needed."""
        if v is None:
            return []
        # If it's a dict (from DB), convert to list
        if isinstance(v, dict):
            return [v]
        # If it's already a list, return as is
        if isinstance(v, list):
            return v
        return []

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
