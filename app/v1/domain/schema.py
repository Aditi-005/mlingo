"""Schemas for different models are written here"""
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel

from app.v1.domain.models import KeyStatus, ActivityStatus


class Modifier(BaseModel):
    """Contains all the fields that will be inherited by other schemas """
    modified_on: Optional[date] = None
    modified_by: Optional[int] = None


class Credentials(BaseModel):
    """Used to get the credentials of an individual"""
    email: str
    token: Optional[str] = None
    password: str


class LoginResponse(BaseModel):
    user_id: int
    name: str
    projects: List


class UpdateEnvironment(Modifier):
    project_id: int = None
    environment_name: str
    activity_status: Optional[ActivityStatus] = ActivityStatus.ACTIVE
    is_main: bool = None


class AddEnvironment(UpdateEnvironment):
    """Contains all the fields that will be accessible to all objects of type - 'Branch' """
    created_at: date = datetime.now()


class GetEnvironments(BaseModel):
    environment_name: str
    environment_id: int
    activity_status: Optional[ActivityStatus] = ActivityStatus.ACTIVE
    is_main: bool
    project_id: int


class AddUser(Modifier):
    """Contains all the fields that will be accessible to all objects of type - 'User' """
    user_name: str = ""
    password: Optional[str] = None
    user_email: str
    user_contact: int = None
    change_password_token: str = None


class InviteEmployee(Modifier):
    user_email: Optional[str] = None
    activity_status: Optional[ActivityStatus] = ActivityStatus.ACTIVE


class JsonObject(BaseModel):
    """Used to get selected json fields from FE"""
    email: Optional[str] = None


class UpdateProject(Modifier):
    project_id: Optional[int] = None
    project_name: str
    project_logo: str = None
    services: str = None
    owner: int = None
    activity_status: Optional[ActivityStatus] = ActivityStatus.ACTIVE


class AddProject(AddEnvironment, UpdateProject):
    """Contains all the fields that will be accessible to all objects of type - 'Project' """
    status: Optional[ActivityStatus] = ActivityStatus.ACTIVE
    onboarding_date: date = datetime.now()


class GetProject(BaseModel):
    project_id: int
    project_name: Optional[str]
    owner: Optional[int]
    activity_status: Optional[ActivityStatus] = None


class Language(BaseModel):
    language_id: Optional[int] | None = None
    language: str


class Key(BaseModel):
    key_id: Optional[int] | None = None
    key: str
    status: KeyStatus = "PUBLISHED"


class LanguageTranslation(Language):
    translation: str


class Translate(Key):
    translation_id: Optional[int] | None = None
    translations: List[LanguageTranslation]
