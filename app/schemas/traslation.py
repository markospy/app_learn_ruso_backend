from typing import Any

from pydantic import BaseModel, model_validator


class Translation(BaseModel):
    """Translation schema that accepts both formats:
    - Standard: {"language": "es", "translation": "amar"}
    - Short: {"es": "amar"}
    """
    language: str
    translation: str

    @model_validator(mode="before")
    @classmethod
    def parse_dict_format(cls, value: Any) -> Any:
        """Accept both {'language': 'es', 'translation': 'amar'} and {'es': 'amar'} formats."""
        if isinstance(value, dict):
            # Check if it's the short format {"es": "amar"}
            # If it has exactly one key and that key is not "language" or "translation"
            if len(value) == 1:
                key = list(value.keys())[0]
                if key not in ("language", "translation"):
                    # It's the short format, convert it
                    return {"language": key, "translation": value[key]}
            # Otherwise, it's already in the standard format or has multiple keys
            return value
        return value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Translation):
            return NotImplemented
        return self.language == other.language

    def __hash__(self) -> int:
        return hash((self.language, self.translation))

    def __str__(self) -> str:
        return f"{self.language}: {self.translation}"

    def __repr__(self) -> str:
        return f"Translation(language={self.language}, translation={self.translation})"

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary format for database storage."""
        return {"language": self.language, "translation": self.translation}