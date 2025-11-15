from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_active_user
from app.crud.verb import (add_verb_to_group, create_verb_group,
                           delete_verb_group, get_verb_by_id,
                           get_verb_group_by_id, get_verb_groups_by_user,
                           remove_verb_from_group, update_verb_group)
from app.database import get_session
from app.models.user import User
from app.schemas.verb import (VerbGroupCreate, VerbGroupResponse,
                              VerbGroupUpdate)

router = APIRouter(prefix="/api/verb-groups", tags=["verb-groups"])

def check_is_student(user):
    if not user.role or user.role.name != "student":
        return False
    return True

@router.get("", response_model=List[VerbGroupResponse])
def list_verb_groups(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> List[VerbGroupResponse]:
    """List verb groups for the current user and their teachers."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing"
        )
    groups = get_verb_groups_by_user(session, current_user.id)
    if check_is_student(current_user):
        if len(current_user.teachers) > 0:
            for teacher in current_user.teachers:
                groups.extend(get_verb_groups_by_user(session, teacher.id))
    return [VerbGroupResponse.model_validate(group) for group in groups]


@router.get("/{group_id}", response_model=VerbGroupResponse)
def get_verb_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> VerbGroupResponse:
    """Get verb group by ID with its verbs."""
    group = get_verb_group_by_id(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb group not found"
        )

    # Check ownership (students can only see their own groups)
    if current_user.role and current_user.role.name == "student":
         if group.id_user != current_user.id and group.id_user not in [teacher.id for teacher in current_user.teachers]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this group"
            )

    return VerbGroupResponse.model_validate(group)


@router.post("", response_model=VerbGroupResponse, status_code=status.HTTP_201_CREATED)
def create_verb_group_endpoint(
    group_create: VerbGroupCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> VerbGroupResponse:
    """Create a new verb group."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing"
        )
    group = create_verb_group(session, group_create, current_user.id)
    return VerbGroupResponse.model_validate(group)


@router.put("/{group_id}", response_model=VerbGroupResponse)
def update_verb_group_endpoint(
    group_id: int,
    group_update: VerbGroupUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> VerbGroupResponse:
    """Update a verb group."""
    group = get_verb_group_by_id(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb group not found"
        )

    # Check ownership
    if group.id_user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this group"
        )

    updated_group = update_verb_group(session, group, group_update)
    return VerbGroupResponse.model_validate(updated_group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_verb_group_endpoint(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> None:
    """Delete a verb group."""
    group = get_verb_group_by_id(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb group not found"
        )

    # Check ownership
    if group.id_user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this group"
        )

    delete_verb_group(session, group)


@router.post("/{group_id}/verbs/{verb_id}", status_code=status.HTTP_201_CREATED)
def add_verb_to_group_endpoint(
    group_id: int,
    verb_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> dict:
    """Add a verb to a group."""
    group = get_verb_group_by_id(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb group not found"
        )

    # Check ownership
    if group.id_user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this group"
        )

    verb = get_verb_by_id(session, verb_id)
    if not verb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb not found"
        )

    add_verb_to_group(session, group_id, verb_id)
    return {"message": "Verb added to group successfully"}


@router.delete("/{group_id}/verbs/{verb_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_verb_from_group_endpoint(
    group_id: int,
    verb_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> None:
    """Remove a verb from a group."""
    group = get_verb_group_by_id(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb group not found"
        )

    # Check ownership
    if group.id_user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this group"
        )

    remove_verb_from_group(session, group_id, verb_id)

