from datetime import datetime
from typing import Any, List, Optional, Tuple

from sqlmodel import Session, func, select

from app.models.verb import Verb, VerbGroup, VerbGroupVerb
from app.schemas.verb import (VerbCreate, VerbGroupCreate, VerbGroupUpdate,
                              VerbUpdate)


def _normalize_translations(translations: Any) -> List[dict]:
    """Normalize translations to list format."""
    if not translations:
        return []
    if isinstance(translations, dict):
        return [translations]
    if isinstance(translations, list):
        return translations
    return []


def _matches_translation_filter(
    translations: Any,
    translation_lang: str,
    translation_text: str
) -> bool:
    """Check if translations match the filter."""
    normalized = _normalize_translations(translations)
    if not normalized:
        return False

    for trans in normalized:
        if isinstance(trans, dict):
            lang_translations = trans.get(translation_lang, [])
            if isinstance(lang_translations, list):
                if any(translation_text.lower() in t.lower() for t in lang_translations):
                    return True
    return False


def get_verb_by_id(session: Session, verb_id: int) -> Optional[Verb]:
    """Get verb by ID."""
    return session.get(Verb, verb_id)


def get_verb_by_pair_id(session: Session, verb_pair_id: str) -> Optional[Verb]:
    """Get verb by pair ID."""
    statement = select(Verb).where(Verb.verb_pair_id == verb_pair_id)
    return session.exec(statement).first()


def get_verbs(
    session: Session,
    page: int = 1,
    per_page: int = 20,
    verb_pair_id: Optional[str] = None,
    conjugation_type: Optional[int] = None,
    translation_lang: Optional[str] = None,
    translation_text: Optional[str] = None,
) -> Tuple[List[Verb], int]:
    """Get verbs with optional filters and pagination.

    Returns:
        Tuple of (verbs list, total count)
    """
    # Build base query
    statement = select(Verb)
    count_statement = select(func.count()).select_from(Verb)

    # Apply filters that can be done in SQL
    if verb_pair_id:
        statement = statement.where(Verb.verb_pair_id.contains(verb_pair_id))
        count_statement = count_statement.where(Verb.verb_pair_id.contains(verb_pair_id))

    if conjugation_type:
        statement = statement.where(Verb.conjugation_type == conjugation_type)
        count_statement = count_statement.where(Verb.conjugation_type == conjugation_type)

    # Get total count before pagination
    total = session.exec(count_statement).one()

    # Apply pagination
    offset = (page - 1) * per_page
    statement = statement.offset(offset).limit(per_page)

    # Execute query
    verbs = list(session.exec(statement).all())

    # Filter by translation if provided (after fetching due to JSON complexity)
    if translation_lang and translation_text:
        filtered_verbs = []
        for verb in verbs:
            if _matches_translation_filter(
                verb.translations,
                translation_lang,
                translation_text
            ):
                filtered_verbs.append(verb)

        # If we filtered, we need to recalculate total
        if filtered_verbs:
            # Re-fetch all matching to get accurate count
            all_statement = select(Verb)
            if verb_pair_id:
                all_statement = all_statement.where(Verb.verb_pair_id.contains(verb_pair_id))
            if conjugation_type:
                all_statement = all_statement.where(Verb.conjugation_type == conjugation_type)
            all_verbs = list(session.exec(all_statement).all())
            filtered_all = [
                v for v in all_verbs
                if _matches_translation_filter(v.translations, translation_lang, translation_text)
            ]
            total = len(filtered_all)
            # Re-apply pagination to filtered results
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            filtered_verbs = filtered_all[start_idx:end_idx]
        else:
            total = 0

        verbs = filtered_verbs

    return verbs, total


def create_verb(session: Session, verb_create: VerbCreate) -> Verb:
    """Create a new verb."""
    data = verb_create.model_dump(exclude_unset=True, by_alias=True)

    # Convert nested Pydantic models to dicts for JSON storage
    if "imperfective" in data and hasattr(data["imperfective"], "model_dump"):
        data["imperfective"] = data["imperfective"].model_dump()
    if "perfective" in data and hasattr(data["perfective"], "model_dump"):
        data["perfective"] = data["perfective"].model_dump()
    if "translations" in data:
        translations_list = []
        for trans in data["translations"]:
            if hasattr(trans, "model_dump"):
                translations_list.append(trans.model_dump(exclude_none=True))
            else:
                translations_list.append(trans)
        data["translations"] = translations_list

    verb = Verb(**data)
    session.add(verb)
    session.commit()
    session.refresh(verb)
    return verb


def update_verb(session: Session, verb: Verb, verb_update: VerbUpdate) -> Verb:
    """Update a verb."""
    update_data = verb_update.model_dump(exclude_unset=True, by_alias=True)

    # Convert nested Pydantic models to dicts for JSON storage
    if "imperfective" in update_data and hasattr(update_data["imperfective"], "model_dump"):
        update_data["imperfective"] = update_data["imperfective"].model_dump()
    if "perfective" in update_data and hasattr(update_data["perfective"], "model_dump"):
        update_data["perfective"] = update_data["perfective"].model_dump()
    if "translations" in update_data:
        translations_list = []
        for trans in update_data["translations"]:
            if hasattr(trans, "model_dump"):
                translations_list.append(trans.model_dump(exclude_none=True))
            else:
                translations_list.append(trans)
        update_data["translations"] = translations_list

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
