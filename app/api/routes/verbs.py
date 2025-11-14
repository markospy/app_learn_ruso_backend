from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import require_admin_or_teacher
from app.crud.verb import create_verb, delete_verb, get_verb_by_id, get_verbs, update_verb
from app.database import get_session
from app.models.user import User
from app.schemas.verb import VerbCreate, VerbResponse, VerbUpdate, VerbWithConjugations

router = APIRouter(prefix="/api/verbs", tags=["verbs"])


@router.get("", response_model=List[VerbResponse])
def list_verbs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    infinitive: Optional[str] = Query(None),
    conjugation_type: Optional[int] = Query(None, alias="conjugationType"),
    session: Session = Depends(get_session),
) -> List[VerbResponse]:
    """List verbs with optional filters."""
    verbs = get_verbs(
        session,
        skip=skip,
        limit=limit,
        infinitive=infinitive,
        conjugation_type=conjugation_type,
    )
    return [VerbResponse.model_validate(verb) for verb in verbs]


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


@router.get("/{verb_id}/conjugations", response_model=VerbWithConjugations)
def get_verb_conjugations(
    verb_id: int,
    session: Session = Depends(get_session),
) -> VerbWithConjugations:
    """Get verb with conjugations grouped by tense."""
    verb = get_verb_by_id(session, verb_id)
    if not verb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verb not found"
        )
    return VerbWithConjugations.from_orm(verb)


@router.post("", response_model=VerbResponse, status_code=status.HTTP_201_CREATED)
def create_verb_endpoint(
    verb_create: VerbCreate,
    current_user: User = Depends(require_admin_or_teacher),
    session: Session = Depends(get_session),
) -> VerbResponse:
    """Create a new verb (admin or teacher only)."""
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

