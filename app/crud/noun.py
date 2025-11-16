from datetime import datetime
from typing import Any, List, Optional, Tuple

from sqlmodel import Session, func, select

from app.models.noun import Noun, NounGroup, NounGroupNoun
from app.schemas.noun import (NounCreate, NounGroupCreate, NounGroupUpdate,
                              NounUpdate)


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


def get_noun_by_id(session: Session, noun_id: int) -> Optional[Noun]:
    """Get noun by ID."""
    return session.get(Noun, noun_id)


def get_nouns(
    session: Session,
    page: int = 1,
    per_page: int = 20,
    noun: Optional[str] = None,
    gender: Optional[str] = None,
    translation_lang: Optional[str] = None,
    translation_text: Optional[str] = None,
) -> Tuple[List[Noun], int]:
    """Get nouns with optional filters and pagination.

    Returns:
        Tuple of (nouns list, total count)
    """
    # Build base query
    statement = select(Noun)
    count_statement = select(func.count()).select_from(Noun)

    # Apply filters that can be done in SQL
    if noun:
        statement = statement.where(Noun.noun.contains(noun))
        count_statement = count_statement.where(Noun.noun.contains(noun))

    if gender:
        statement = statement.where(Noun.gender == gender.lower())
        count_statement = count_statement.where(Noun.gender == gender.lower())

    # Get total count before pagination
    total = session.exec(count_statement).one()

    # Apply pagination
    offset = (page - 1) * per_page
    statement = statement.offset(offset).limit(per_page)

    # Execute query
    nouns = list(session.exec(statement).all())

    # Filter by translation if provided (after fetching due to JSON complexity)
    if translation_lang and translation_text:
        filtered_nouns = []
        for noun_obj in nouns:
            if _matches_translation_filter(
                noun_obj.translations,
                translation_lang,
                translation_text
            ):
                filtered_nouns.append(noun_obj)

        # If we filtered, we need to recalculate total
        # This is a limitation - we'd need to fetch all to count accurately
        # For now, we'll do a simple approximation
        if filtered_nouns:
            # Re-fetch all matching to get accurate count
            all_statement = select(Noun)
            if noun:
                all_statement = all_statement.where(Noun.noun.contains(noun))
            if gender:
                all_statement = all_statement.where(Noun.gender == gender.lower())
            all_nouns = list(session.exec(all_statement).all())
            filtered_all = [
                n for n in all_nouns
                if _matches_translation_filter(n.translations, translation_lang, translation_text)
            ]
            total = len(filtered_all)
            # Re-apply pagination to filtered results
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            filtered_nouns = filtered_all[start_idx:end_idx]
        else:
            total = 0

        nouns = filtered_nouns

    return nouns, total


def create_noun(session: Session, noun_create: NounCreate) -> Noun:
    """Create a new noun."""
    data = noun_create.model_dump(exclude_unset=True)

    # Convert nested Pydantic models to dicts for JSON storage
    if "declension" in data and hasattr(data["declension"], "model_dump"):
        data["declension"] = data["declension"].model_dump()
    if "translations" in data:
        translations_list = []
        for trans in data["translations"]:
            if hasattr(trans, "model_dump"):
                translations_list.append(trans.model_dump(exclude_none=True))
            else:
                translations_list.append(trans)
        data["translations"] = translations_list

    noun = Noun(**data)
    session.add(noun)
    session.commit()
    session.refresh(noun)
    return noun


def update_noun(session: Session, noun: Noun, noun_update: NounUpdate) -> Noun:
    """Update a noun."""
    update_data = noun_update.model_dump(exclude_unset=True)

    # Convert nested Pydantic models to dicts for JSON storage
    if "declension" in update_data and hasattr(update_data["declension"], "model_dump"):
        update_data["declension"] = update_data["declension"].model_dump()
    if "translations" in update_data:
        translations_list = []
        for trans in update_data["translations"]:
            if hasattr(trans, "model_dump"):
                translations_list.append(trans.model_dump(exclude_none=True))
            else:
                translations_list.append(trans)
        update_data["translations"] = translations_list

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
