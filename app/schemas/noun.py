from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class NounBase(BaseModel):
    """Base noun schema."""
    sustantivo: str = Field(max_length=100)
    singular: str = Field(max_length=100)
    plural: str = Field(max_length=100)
    gender: str = Field(max_length=10)  # masculine, feminine, neuter


class NounCreate(NounBase):
    """Schema for creating a noun."""
    pass


class NounUpdate(BaseModel):
    """Schema for updating a noun."""
    sustantivo: Optional[str] = Field(default=None, max_length=100)
    singular: Optional[str] = Field(default=None, max_length=100)
    plural: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[str] = Field(default=None, max_length=10)


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

