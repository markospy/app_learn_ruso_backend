from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from app.models.verb import Verb, VerbGroup, VerbGroupVerb
from app.schemas.traslation import Translation
from app.schemas.verb import (VerbCreate, VerbGroupCreate, VerbGroupUpdate,
                              VerbUpdate)


def get_verb_by_id(session: Session, verb_id: int) -> Optional[Verb]:
    """Get verb by ID."""
    return session.get(Verb, verb_id)


def get_verbs(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    infinitive: Optional[str] = None,
    conjugation_type: Optional[int] = None,
    translation: Optional[Translation] = None,
) -> List[Verb]:
    """Get verbs with optional filters."""
    statement = select(Verb)

    if infinitive:
        statement = statement.where(Verb.infinitive.like(f"%{infinitive}%"))
    if conjugation_type:
        statement = statement.where(Verb.conjugationType == conjugation_type)
    if translation:
        translation_dict = {"language": translation.language, "translation": translation.translation}
        statement = statement.where(Verb.translations.any_(translation_dict))
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def create_verb(session: Session, verb_create: VerbCreate) -> Verb:
    """Create a new verb."""
    verb = Verb(**verb_create.model_dump())
    session.add(verb)
    session.commit()
    session.refresh(verb)
    return verb


def update_verb(session: Session, verb: Verb, verb_update: VerbUpdate) -> Verb:
    """Update a verb."""
    update_data = verb_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(verb, field, value)
    verb.updated_at = datetime.now()
    session.add(verb)
    session.commit()
    session.refresh(verb)
    return verb


def delete_verb(session: Session, verb: Verb) -> None:
    """Delete a verb."""
    session.delete(verb)
    session.commit()


def get_verb_group_by_id(session: Session, group_id: int) -> Optional[VerbGroup]:
    """Get verb group by ID."""
    return session.get(VerbGroup, group_id)


def get_verb_groups_by_user(session: Session, user_id: int) -> List[VerbGroup]:
    """Get all verb groups for a user."""
    statement = select(VerbGroup).where(VerbGroup.id_user == user_id)
    return list(session.exec(statement).all())


def create_verb_group(session: Session, group_create: VerbGroupCreate, user_id: int) -> VerbGroup:
    """Create a new verb group."""
    group = VerbGroup(
        name_group=group_create.name_group,
        id_user=user_id,
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def update_verb_group(session: Session, group: VerbGroup, group_update: VerbGroupUpdate) -> VerbGroup:
    """Update a verb group."""
    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)
    group.updated_at = datetime.now()
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def delete_verb_group(session: Session, group: VerbGroup) -> None:
    """Delete a verb group."""
    session.delete(group)
    session.commit()


def add_verb_to_group(session: Session, group_id: int, verb_id: int) -> VerbGroupVerb:
    """Add a verb to a group."""
    link = VerbGroupVerb(id_group=group_id, id_verb=verb_id)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def remove_verb_from_group(session: Session, group_id: int, verb_id: int) -> None:
    """Remove a verb from a group."""
    statement = select(VerbGroupVerb).where(
        VerbGroupVerb.id_group == group_id,
        VerbGroupVerb.id_verb == verb_id
    )
    link = session.exec(statement).first()
    if link:
        session.delete(link)
        session.commit()

