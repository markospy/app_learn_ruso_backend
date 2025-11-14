from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""
    name: str = Field(max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    email: EmailStr
    username: str = Field(max_length=50)
    language: str = Field(default="es", max_length=10)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(min_length=6)
    id_rol: int = Field(default=3)  # Default to student


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    name: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    language: Optional[str] = Field(default=None, max_length=10)
    is_active: Optional[bool] = None


class UserPublic(BaseModel):
    """Public user schema without sensitive information."""
    id: int
    name: str
    country: Optional[str]
    email: str
    username: str
    language: str
    role: Optional[str] = None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UserResponse(UserPublic):
    """Full user response schema."""
    id_rol: int
    updated_at: datetime

    class Config:
        from_attributes = True

