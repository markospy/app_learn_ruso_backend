from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_active_user
from app.crud.noun import (add_noun_to_group, create_noun_group,
                           delete_noun_group, get_noun_by_id,
                           get_noun_group_by_id, get_noun_groups_by_user,
                           remove_noun_from_group, update_noun_group)
from app.database import get_session
from app.models.user import User
from app.schemas.noun import (NounGroupCreate, NounGroupResponse,
                              NounGroupUpdate)

router = APIRouter(prefix="/api/noun-groups", tags=["noun-groups"])

def check_is_student(user):
    if not user.role or user.role.name != "student":
        return False
    return True

@router.get("", response_model=List[NounGroupResponse])
def list_noun_groups(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> List[NounGroupResponse]:
    """List noun groups for the current user and their teachers."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing"
        )

    groups = get_noun_groups_by_user(session, current_user.id)
    if check_is_student(current_user):
        if len(current_user.teachers) > 0:
            for teacher in current_user.teachers:
                groups.extend(get_noun_groups_by_user(session, teacher.id))
    return [NounGroupResponse.model_validate(group) for group in groups]


@router.get("/{group_id}", response_model=NounGroupResponse)
def get_noun_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> NounGroupResponse:
    """Get noun group by ID with its nouns."""
    group = get_noun_group_by_id(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noun group not found"
        )

    # Check ownership (students can only see their own groups)
    if current_user.role and current_user.role.name == "student":
        if group.id_user != current_user.id and group.id_user not in [teacher.id for teacher in current_user.teachers]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this group"
            )

    return NounGroupResponse.model_validate(group)


@router.post("", response_model=NounGroupResponse, status_code=status.HTTP_201_CREATED)
def create_noun_group_endpoint(
    group_create: NounGroupCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> NounGroupResponse:
    """Create a new noun group."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing"
        )
    group = create_noun_group(session, group_create, current_user.id)
    return NounGroupResponse.model_validate(group)


@router.put("/{group_id}", response_model=NounGroupResponse)
def update_noun_group_endpoint(
    group_id: int,
    group_update: NounGroupUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> NounGroupResponse:
    """Update a noun group."""
    group = get_noun_group_by_id(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noun group not found"
        )

    # Check ownership
    if group.id_user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this group"
        )

    updated_group = update_noun_group(session, group, group_update)
    return NounGroupResponse.model_validate(updated_group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_noun_group_endpoint(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> None:
    """Delete a noun group."""
    group = get_noun_group_by_id(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noun group not found"
        )

    # Check ownership
    if group.id_user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this group"
        )

    delete_noun_group(session, group)


@router.post("/{group_id}/nouns/{noun_id}", status_code=status.HTTP_201_CREATED)
def add_noun_to_group_endpoint(
    group_id: int,
    noun_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> dict:
    """Add a noun to a group."""
    group = get_noun_group_by_id(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noun group not found"
        )

    # Check ownership
    if group.id_user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this group"
        )

    noun = get_noun_by_id(session, noun_id)
    if not noun:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noun not found"
        )

    add_noun_to_group(session, group_id, noun_id)
    return {"message": "Noun added to group successfully"}


@router.delete("/{group_id}/nouns/{noun_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_noun_from_group_endpoint(
    group_id: int,
    noun_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> None:
    """Remove a noun from a group."""
    group = get_noun_group_by_id(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noun group not found"
        )

    # Check ownership
    if group.id_user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this group"
        )

    remove_noun_from_group(session, group_id, noun_id)

