from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from app.models.noun import Noun, NounGroup, NounGroupNoun
from app.schemas.noun import (NounCreate, NounGroupCreate, NounGroupUpdate,
                              NounUpdate)


def get_noun_by_id(session: Session, noun_id: int) -> Optional[Noun]:
    """Get noun by ID."""
    return session.get(Noun, noun_id)


def get_nouns(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    noun: Optional[str] = None,
    gender: Optional[str] = None,
) -> List[Noun]:
    """Get nouns with optional filters."""
    statement = select(Noun)

    if noun:
        statement = statement.where(Noun.noun.like(f"%{noun}%"))
    if gender:
        statement = statement.where(Noun.gender == gender)

    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def create_noun(session: Session, noun_create: NounCreate) -> Noun:
    """Create a new noun."""
    noun = Noun(**noun_create.model_dump())
    session.add(noun)
    session.commit()
    session.refresh(noun)
    return noun


def update_noun(session: Session, noun: Noun, noun_update: NounUpdate) -> Noun:
    """Update a noun."""
    update_data = noun_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(noun, field, value)
    noun.updated_at = datetime.now()
    session.add(noun)
    session.commit()
    session.refresh(noun)
    return noun


def delete_noun(session: Session, noun: Noun) -> None:
    """Delete a noun."""
    session.delete(noun)
    session.commit()


def get_noun_group_by_id(session: Session, group_id: int) -> Optional[NounGroup]:
    """Get noun group by ID."""
    return session.get(NounGroup, group_id)


def get_noun_groups_by_user(session: Session, user_id: int) -> List[NounGroup]:
    """Get all noun groups for a user."""
    statement = select(NounGroup).where(NounGroup.id_user == user_id)
    return list(session.exec(statement).all())


def create_noun_group(session: Session, group_create: NounGroupCreate, user_id: int) -> NounGroup:
    """Create a new noun group."""
    group = NounGroup(
        name_group=group_create.name_group,
        id_user=user_id,
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def update_noun_group(session: Session, group: NounGroup, group_update: NounGroupUpdate) -> NounGroup:
    """Update a noun group."""
    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)
    group.updated_at = datetime.now()
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def delete_noun_group(session: Session, group: NounGroup) -> None:
    """Delete a noun group."""
    session.delete(group)
    session.commit()


def add_noun_to_group(session: Session, group_id: int, noun_id: int) -> NounGroupNoun:
    """Add a noun to a group."""
    link = NounGroupNoun(id_group=group_id, id_noun=noun_id)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def remove_noun_from_group(session: Session, group_id: int, noun_id: int) -> None:
    """Remove a noun from a group."""
    statement = select(NounGroupNoun).where(
        NounGroupNoun.id_group == group_id,
        NounGroupNoun.id_noun == noun_id
    )
    link = session.exec(statement).first()
    if link:
        session.delete(link)
        session.commit()

