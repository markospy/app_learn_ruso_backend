from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import require_admin_or_teacher
from app.crud.noun import (create_noun, delete_noun, get_noun_by_id, get_nouns,
                           update_noun)
from app.database import get_session
from app.models.user import User
from app.schemas.noun import NounCreate, NounResponse, NounUpdate
from app.schemas.traslation import Translation

router = APIRouter(prefix="/api/nouns", tags=["nouns"])


@router.get("", response_model=List[NounResponse])
def list_nouns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    noun: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    translation: Optional[Translation] = Query(None),
    session: Session = Depends(get_session),
) -> List[NounResponse]:
    """List nouns with optional filters."""
    nouns = get_nouns(
        session,
        skip=skip,
        limit=limit,
        noun=noun,
        gender=gender,
        translation=translation,
    )
    return [NounResponse.model_validate(noun) for noun in nouns]


@router.get("/{noun_id}", response_model=NounResponse)
def get_noun(
    noun_id: int,
    session: Session = Depends(get_session),
) -> NounResponse:
    """Get noun by ID."""
    noun = get_noun_by_id(session, noun_id)
    if not noun:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noun not found"
        )
    return NounResponse.model_validate(noun)


@router.post("", response_model=NounResponse, status_code=status.HTTP_201_CREATED)
def create_noun_endpoint(
    noun_create: NounCreate,
    current_user: User = Depends(require_admin_or_teacher),
    session: Session = Depends(get_session),
) -> NounResponse:
    """Create a new noun (admin or teacher only)."""
    noun = create_noun(session, noun_create)
    return NounResponse.model_validate(noun)


@router.put("/{noun_id}", response_model=NounResponse)
def update_noun_endpoint(
    noun_id: int,
    noun_update: NounUpdate,
    current_user: User = Depends(require_admin_or_teacher),
    session: Session = Depends(get_session),
) -> NounResponse:
    """Update a noun (admin or teacher only)."""
    noun = get_noun_by_id(session, noun_id)
    if not noun:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noun not found"
        )

    updated_noun = update_noun(session, noun, noun_update)
    return NounResponse.model_validate(updated_noun)


@router.delete("/{noun_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_noun_endpoint(
    noun_id: int,
    current_user: User = Depends(require_admin_or_teacher),
    session: Session = Depends(get_session),
) -> None:
    """Delete a noun (admin or teacher only)."""
    noun = get_noun_by_id(session, noun_id)
    if not noun:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noun not found"
        )

    delete_noun(session, noun)

