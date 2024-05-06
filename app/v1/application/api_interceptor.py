"""Apis are intercepted in this file"""
from typing import Annotated

from fastapi import APIRouter, Header
from fastapi import Depends

from app.infrastructure.database import engine, get_db
from app.v1.application.dto.dto_classes import ResponseDTO
from app.v1.application.service.language_service import add_translation, fetch_language_keys, \
    fetch_all_translation, update_translation
from app.v1.application.service.project_services import add_project
from app.v1.application.service.user_services import auth_function, add_user, initiate_pwd_reset, check_token, \
    change_password, get_projects
from app.v1.domain import models, schema

router = APIRouter()
models.Base.metadata.create_all(bind=engine)

"""----------------------------------------------Language Related APIs-------------------------------------------------------------------"""


@router.post("/v1/addTranslation")
def new_translation(addTranslation: schema.Translate, db=Depends(get_db)):
    return add_translation(addTranslation, db)


@router.put("/v1/updateTranslation")
def edit_translation(editTranslation: schema.Translate, db=Depends(get_db)):
    return update_translation(editTranslation, db)


@router.get("/v1/getAllTranslations")
def get_all_translations(db=Depends(get_db)):
    try:
        return fetch_all_translation(db)
    except Exception as e:
        return ResponseDTO(204, f"{str(e)}", [])


@router.get("/v1/getLanguageKeys")
def get_language_keys(languageId: int, db=Depends(get_db)):
    try:
        return fetch_language_keys(languageId, db)
    except Exception as e:
        return ResponseDTO(204, f"{str(e)}", [])


@router.get("/v1/getAllLanguage")
def get_all_language(db=Depends(get_db)):
    try:
        languages = db.query(models.Language).all()
        return ResponseDTO(200, "Languages fetched successfully", languages)
    except Exception as e:
        return ResponseDTO(204, f"{str(e)}", [])


"""----------------------------------------------User Related APIs-------------------------------------------------------------------"""


@router.post("/v1/authenticateUser")
def login(credentials: schema.Credentials, db=Depends(get_db)):
    """User Login"""
    return auth_function(credentials, db)


@router.post("/v1/registerUser")
def register_user(user: schema.AddUser, db=Depends(get_db)):
    """User Registration"""
    return add_user(user, db)


@router.post("/v1/forgotPassword")
def forgot_password(email: schema.JsonObject, db=Depends(get_db)):
    """Calls the service layer to send an email for password reset"""
    return initiate_pwd_reset(email.model_dump()["email"], db)


@router.post("/v1/sendVerificationLink")
def verify_token(obj: schema.Credentials, db=Depends(get_db)):
    """Calls the service layer to verify the token received by an individual"""
    return check_token(obj, db)


@router.put("/v1/updatePassword")
def update_password(obj: schema.Credentials, db=Depends(get_db)):
    """Calls the service layer to update the password of an individual"""
    return change_password(obj, db)


"""----------------------------------------------Company related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{user_id}/createProject")
def create_company(project: schema.AddProject, user_id: int, db=Depends(get_db)):
    return add_project(project, user_id, db)


@router.get("/v2.0/getProjects")
def get_company(user_id: Annotated[str | None, Header(convert_underscores=False)] = None,
                db=Depends(get_db)):
    print(user_id)
    user_projects = db.query(models.UserProjectEnv).filter(models.UserProjectEnv.user_id == user_id).all()
    return ResponseDTO(200, "", get_projects(user_projects, db))

# @router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateCompany/{comp_id}")
# def update_company(company: schema.UpdateProject, user_id: int, company_id: int, branch_id: int, comp_id: int,
#                    db=Depends(get_db)):
#     return modify_company(company, user_id, company_id, branch_id, comp_id, db)
