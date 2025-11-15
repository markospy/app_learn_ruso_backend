from dataclasses import dataclass


@dataclass
class Translation:
    """Translation schema."""
    language: str
    translation: str

    def __eq__(cls, other: object) -> bool:
        if not isinstance(other, Translation):
            return NotImplemented
        return cls.language == other.language

    def __hash__(self) -> int:
        return hash((self.language, self.translation))

    def __str__(self) -> str:
        return f"{self.language}: {self.translation}"

    def __repr__(self) -> str:
        return f"Translation(language={self.language}, translation={self.translation})"