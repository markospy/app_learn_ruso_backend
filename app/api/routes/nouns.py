import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import require_admin_or_teacher
from app.crud.noun import (create_noun, delete_noun, get_noun_by_id, get_nouns,
                           update_noun)
from app.database import get_session
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.noun import (NounCreate, NounResponse, NounUpdate,
                              normalize_noun_for_response)

router = APIRouter(prefix="/api/nouns", tags=["nouns"])


@router.get("", response_model=PaginatedResponse[NounResponse])
def list_nouns(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    noun: Optional[str] = Query(None, description="Filter by noun (partial match)"),
    gender: Optional[str] = Query(None, description="Filter by gender (masculine, feminine, neuter)"),
    translation_lang: Optional[str] = Query(None, description="Translation language code (es, en, etc.)"),
    translation_text: Optional[str] = Query(None, description="Search text in translations"),
    session: Session = Depends(get_session),
) -> PaginatedResponse[NounResponse]:
    """List nouns with optional filters and pagination."""
    nouns, total = get_nouns(
        session,
        page=page,
        per_page=per_page,
        noun=noun,
        gender=gender,
        translation_lang=translation_lang,
        translation_text=translation_text,
    )

    total_pages = math.ceil(total / per_page) if total > 0 else 0

    return PaginatedResponse(
        items=[NounResponse.model_validate(normalize_noun_for_response(noun)) for noun in nouns],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


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
    return NounResponse.model_validate(normalize_noun_for_response(noun))


@router.post("", response_model=NounResponse, status_code=status.HTTP_201_CREATED)
def create_noun_endpoint(
    noun_create: NounCreate,
    current_user: User = Depends(require_admin_or_teacher),
    session: Session = Depends(get_session),
) -> NounResponse:
    """Create a new noun (admin or teacher only)."""
    noun = create_noun(session, noun_create)
    return NounResponse.model_validate(normalize_noun_for_response(noun))


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
