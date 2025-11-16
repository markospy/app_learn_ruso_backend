from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserPublic


class RegisterRequest(BaseModel):
    """Schema for registration request."""
    name: str = Field(max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    email: EmailStr
    username: str = Field(max_length=50)
    password: str = Field(min_length=6)
    language: str = Field(default="es", max_length=10)
    id_rol: int = Field(default=3)  # Default to student


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class TokenData(BaseModel):
    """Schema for decoded token data."""
    username: Optional[str] = None
    user_id: Optional[int] = None

