import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import require_admin_or_teacher
from app.crud.verb import (create_verb, delete_verb, get_verb_by_id,
                           get_verb_by_pair_id, get_verbs, update_verb)
from app.database import get_session
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.verb import VerbCreate, VerbResponse, VerbUpdate

router = APIRouter(prefix="/api/verbs", tags=["verbs"])


@router.get("", response_model=PaginatedResponse[VerbResponse])
def list_verbs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    verb_pair_id: Optional[str] = Query(None, description="Filter by verb pair ID (partial match)"),
    conjugation_type: Optional[int] = Query(None, alias="conjugationType", description="Filter by conjugation type (1 or 2)"),
    translation_lang: Optional[str] = Query(None, description="Translation language code (es, en, etc.)"),
    translation_text: Optional[str] = Query(None, description="Search text in translations"),
    session: Session = Depends(get_session),
) -> PaginatedResponse[VerbResponse]:
    """List verbs with optional filters and pagination."""
    verbs, total = get_verbs(
        session,
        page=page,
        per_page=per_page,
        verb_pair_id=verb_pair_id,
        conjugation_type=conjugation_type,
        translation_lang=translation_lang,
        translation_text=translation_text,
    )

    total_pages = math.ceil(total / per_page) if total > 0 else 0

    return PaginatedResponse(
        items=[VerbResponse.model_validate(verb) for verb in verbs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/pair/{verb_pair_id}", response_model=VerbResponse)
def get_verb_by_pair(
    verb_pair_id: str,
    session: Session = Depends(get_session),
) -> VerbResponse:
    """Get verb by pair ID."""
    verb = get_verb_by_pair_id(session, verb_pair_id)
    if not verb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb not found"
        )
    return VerbResponse.model_validate(verb)


@router.get("/{verb_id}", response_model=VerbResponse)
def get_verb(
    verb_id: int,
    session: Session = Depends(get_session),
) -> VerbResponse:
    """Get verb by ID."""
    verb = get_verb_by_id(session, verb_id)
    if not verb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb not found"
        )
    return VerbResponse.model_validate(verb)


@router.post("", response_model=VerbResponse, status_code=status.HTTP_201_CREATED)
def create_verb_endpoint(
    verb_create: VerbCreate,
    current_user: User = Depends(require_admin_or_teacher),
    session: Session = Depends(get_session),
) -> VerbResponse:
    """Create a new verb (admin or teacher only)."""
    # Check if verb_pair_id already exists
    existing = get_verb_by_pair_id(session, verb_create.verb_pair_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verb with pair_id '{verb_create.verb_pair_id}' already exists"
        )

    verb = create_verb(session, verb_create)
    return VerbResponse.model_validate(verb)


@router.put("/{verb_id}", response_model=VerbResponse)
def update_verb_endpoint(
    verb_id: int,
    verb_update: VerbUpdate,
    current_user: User = Depends(require_admin_or_teacher),
    session: Session = Depends(get_session),
) -> VerbResponse:
    """Update a verb (admin or teacher only)."""
    verb = get_verb_by_id(session, verb_id)
    if not verb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb not found"
        )

    # Check if new verb_pair_id conflicts with existing
    if verb_update.verb_pair_id and verb_update.verb_pair_id != verb.verb_pair_id:
        existing = get_verb_by_pair_id(session, verb_update.verb_pair_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Verb with pair_id '{verb_update.verb_pair_id}' already exists"
            )

    updated_verb = update_verb(session, verb, verb_update)
    return VerbResponse.model_validate(updated_verb)


@router.delete("/{verb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_verb_endpoint(
    verb_id: int,
    current_user: User = Depends(require_admin_or_teacher),
    session: Session = Depends(get_session),
) -> None:
    """Delete a verb (admin or teacher only)."""
    verb = get_verb_by_id(session, verb_id)
    if not verb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb not found"
        )

    delete_verb(session, verb)
