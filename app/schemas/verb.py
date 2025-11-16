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
    perfective: Optional[PerfectiveAspect] = None

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


def _normalize_word_form(value: Any) -> Dict[str, str]:
    """Normalize word form - accepts string or dict."""
    if isinstance(value, str):
        return {"word": value, "accent": value, "phonetics": ""}
    if isinstance(value, dict):
        return value
    return {"word": "", "accent": "", "phonetics": ""}


def _normalize_verb_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize verb structure to handle both simple and complex formats."""
    if not isinstance(data, dict):
        return data

    # Normalize imperfective (required)
    if "imperfective" in data and data["imperfective"] is not None and isinstance(data["imperfective"], dict):
        imperfective = data["imperfective"]

        # Normalize infinitive
        if "infinitive" in imperfective:
            infinitive = imperfective["infinitive"]
            if isinstance(infinitive, str):
                # Direct string -> convert to {word: {word, accent, phonetics}}
                imperfective["infinitive"] = {"word": _normalize_word_form(infinitive)}
            elif isinstance(infinitive, dict):
                if "word" in infinitive:
                    # word is string -> convert to WordForm
                    if isinstance(infinitive["word"], str):
                        imperfective["infinitive"]["word"] = _normalize_word_form(infinitive["word"])
                    # word is already dict -> keep as is (but ensure it has all fields)
                    elif isinstance(infinitive["word"], dict):
                        # Ensure all required fields exist
                        word_form = infinitive["word"]
                        if "word" not in word_form:
                            word_form["word"] = ""
                        if "accent" not in word_form:
                            word_form["accent"] = word_form.get("word", "")
                        if "phonetics" not in word_form:
                            word_form["phonetics"] = ""
                else:
                    # No word field, might be malformed, create default
                    imperfective["infinitive"] = {"word": {"word": "", "accent": "", "phonetics": ""}}

        # Normalize present_tense
        if "present_tense" in imperfective and isinstance(imperfective["present_tense"], dict):
            for key in ["ya", "ty", "on_ona", "my", "vy", "oni"]:
                if key in imperfective["present_tense"]:
                    imperfective["present_tense"][key] = _normalize_word_form(imperfective["present_tense"][key])

        # Normalize past_tense
        if "past_tense" in imperfective and isinstance(imperfective["past_tense"], dict):
            for key in ["masculine", "feminine", "neuter", "plural"]:
                if key in imperfective["past_tense"]:
                    imperfective["past_tense"][key] = _normalize_word_form(imperfective["past_tense"][key])

    # Normalize perfective (optional - some verbs don't have perfective)
    if "perfective" in data and data["perfective"] is not None and isinstance(data["perfective"], dict):
        perfective = data["perfective"]

        # Normalize infinitive
        if "infinitive" in perfective:
            infinitive = perfective["infinitive"]
            if isinstance(infinitive, str):
                # Direct string -> convert to {word: {word, accent, phonetics}}
                perfective["infinitive"] = {"word": _normalize_word_form(infinitive)}
            elif isinstance(infinitive, dict):
                if "word" in infinitive:
                    # word is string -> convert to WordForm
                    if isinstance(infinitive["word"], str):
                        perfective["infinitive"]["word"] = _normalize_word_form(infinitive["word"])
                    # word is already dict -> keep as is (but ensure it has all fields)
                    elif isinstance(infinitive["word"], dict):
                        # Ensure all required fields exist
                        word_form = infinitive["word"]
                        if "word" not in word_form:
                            word_form["word"] = ""
                        if "accent" not in word_form:
                            word_form["accent"] = word_form.get("word", "")
                        if "phonetics" not in word_form:
                            word_form["phonetics"] = ""
                else:
                    # No word field, might be malformed, create default
                    perfective["infinitive"] = {"word": {"word": "", "accent": "", "phonetics": ""}}

        # Normalize future_simple
        if "future_simple" in perfective and isinstance(perfective["future_simple"], dict):
            for key in ["ya", "ty", "on_ona", "my", "vy", "oni"]:
                if key in perfective["future_simple"]:
                    perfective["future_simple"][key] = _normalize_word_form(perfective["future_simple"][key])
    elif "perfective" in data and data["perfective"] is None:
        # Keep None if it's explicitly None
        pass

    return data


def normalize_verb_for_response(verb: Any) -> Dict[str, Any]:
    """Normalize verb object/dict for VerbResponse validation."""
    # Convert SQLModel object to dict if needed
    if hasattr(verb, "model_dump"):
        # Use model_dump with mode='json' to get JSON-serializable dict
        data = verb.model_dump(mode='json')
    elif hasattr(verb, "__dict__"):
        data = {}
        for k, v in verb.__dict__.items():
            if not k.startswith("_"):
                # Handle JSON fields that might be already parsed
                if k in ("imperfective", "perfective", "translations"):
                    data[k] = v
                else:
                    data[k] = v
    elif isinstance(verb, dict):
        data = verb.copy()
    else:
        data = {}

    # Normalize translations
    if "translations" in data:
        translations = data["translations"]
        if isinstance(translations, dict):
            data["translations"] = [translations]
        elif not isinstance(translations, list):
            data["translations"] = []

    # Normalize verb structure (imperfective/perfective)
    data = _normalize_verb_structure(data)

    return data


class VerbResponse(VerbBase):
    """Schema for verb response."""
    id: int
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def normalize_data(cls, data: Any) -> Any:
        """Normalize verb data structure before validation."""
        # Handle SQLModel objects
        if not isinstance(data, dict):
            data = normalize_verb_for_response(data)
        else:
            # Normalize translations
            if "translations" in data:
                translations = data["translations"]
                if isinstance(translations, dict):
                    data["translations"] = [translations]
                elif not isinstance(translations, list):
                    data["translations"] = []

            # Normalize verb structure (imperfective/perfective)
            data = _normalize_verb_structure(data)

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
