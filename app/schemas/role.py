from pydantic import BaseModel


class RolePublic(BaseModel):
    """Public role schema."""
    id: int
    name: str

    class Config:
        from_attributes = True

