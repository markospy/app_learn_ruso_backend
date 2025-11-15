from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.crud.role import get_roles
from app.database import get_session
from app.schemas.role import RolePublic

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("", response_model=List[RolePublic])
def get_roles_endpoint(
    session: Session = Depends(get_session),
) -> List[RolePublic]:
    """Get all roles."""
    roles = get_roles(session)
    return [RolePublic.model_validate(role) for role in roles]

