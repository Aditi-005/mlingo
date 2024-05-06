"""Service layer for languages"""

from fastapi import Depends

from app.infrastructure.database import get_db
from app.v1.application.dto.dto_classes import ResponseDTO
from app.v1.domain import models, schema
from app.v1.domain.models import KeyStatus


def add_language(languageName: str, db=Depends(get_db)):
    language = db.query(models.Language).filter(models.Language.language == languageName).first()
    if language:
        return language.language_id
    else:
        new_language = models.Language(language=languageName)

        db.add(new_language)
        db.commit()
        db.refresh(new_language)

        return new_language.language_id


def add_key(addkey: str, status: KeyStatus, db=Depends(get_db)):
    key = db.query(models.Key).filter(models.Key.key == addkey).first()
    if key:
        return key.key_id
    else:
        new_key = models.Key(key=addkey, status=status)

        db.add(new_key)
        db.commit()
        db.refresh(new_key)

        return new_key.key_id


def add_translation(addTranslation: schema.Translate, db=Depends(get_db)):
    try:
        addTranslation.key_id = add_key(addTranslation.key, addTranslation.status, db)

        for translation in addTranslation.translations:
            translation.language_id = add_language(translation.language, db)

            translation_id = db.query(models.Translation).filter(
                models.Translation.key_id == addTranslation.key_id,
                models.Translation.language_id == translation.language_id).first()
            if not translation_id:
                new_translation = models.Translation(key_id=addTranslation.key_id,
                                                     language_id=translation.language_id,
                                                     translation=translation.translation)

                db.add(new_translation)

        db.commit()
        return ResponseDTO(200, "Translation Added successfully", {})
    except Exception as e:
        db.rollback()
        return ResponseDTO(204, f"{str(e)}", {})


def update_translation(editTranslation: schema.Translate, db=Depends(get_db)):
    try:
        if not editTranslation.key_id:
            editTranslation.key_id = add_key(editTranslation.key, editTranslation.status, db)

        for translation in editTranslation.translations:
            if not translation.language_id:
                translation.language_id = add_language(translation.language, db)

            translated = db.query(models.Translation).filter(
                models.Translation.key_id == editTranslation.key_id,
                models.Translation.language_id == translation.language_id)
            translation_exist = translated.first()
            if translation_exist:
                translated.update({"translation": translation.translation})

        db.commit()
        return ResponseDTO(200, "Translation Edited successfully", {})
    except Exception as e:
        db.rollback()
        return ResponseDTO(204, f"{str(e)}", {})


def fetch_translation(keyId: int, languageId: int, db=Depends(get_db)):
    fetched = db.query(models.Translation).filter(models.Translation.key_id == keyId).filter(
        models.Translation.language_id == languageId).first()
    if fetched:
        return fetched.translation
    else:
        return ""


def fetch_language_keys(languageId: int, db=Depends(get_db)):
    keys = db.query(models.Key).all()
    language_keys = []
    for key in keys:
        language_keys.append({
            "key": key.key,
            "value": fetch_translation(key.key_id, languageId, db)})

    return ResponseDTO(200, "Keys fetched successfully", language_keys)


def fetch_all_translation(db=Depends(get_db)):
    available_languages = db.query(models.Language).all()
    available_keys = db.query(models.Key).all()

    formatted_translations = {}

    for key in available_keys:
        key_id = key.key_id
        if key_id not in formatted_translations:
            formatted_translations[key_id] = {
                "id": key_id,
                "key": key.key}

        for available_language in available_languages:
            formatted_translations[key_id][available_language.language] = fetch_translation(key_id,
                                                                                            available_language.language_id,
                                                                                            db)

    formatted_translations_list = list(formatted_translations.values())
    return ResponseDTO(200, "Translations fetched successfully", formatted_translations_list)
