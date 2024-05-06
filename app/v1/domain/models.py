"""Models for table creation"""

from enum import Enum as PyEnum

from sqlalchemy import Column, String, BIGINT, Integer, Enum, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP, ARRAY, Boolean

from app.infrastructure.database import Base


class ActivityStatus(PyEnum):
    """States the activity of a user"""
    INACTIVE = 0
    ACTIVE = 1


class RolesEnum(PyEnum):
    """Enum for roles of an employee in a project"""
    ADMIN = 0
    DEVELOPER = 1
    TRANSLATOR = 2


class Projects(Base):
    """Contains all the fields required in the 'projects' table"""
    __tablename__ = "projects"
    __table_args__ = {'extend_existing': True}

    project_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    project_name = Column(String, nullable=False)
    project_logo = Column(String, nullable=True)
    owner = Column(Integer, ForeignKey('users_auth.user_id'), nullable=False)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    onboarding_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)


class Environments(Base):
    """Contains all the fields required in the 'environment' table"""
    __tablename__ = 'environments'

    environment_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    environment_name = Column(String, nullable=False)
    is_main = Column(Boolean, nullable=True)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)


class UsersAuth(Base):
    """Contains all the fields required in the 'users' table"""
    __tablename__ = "users_auth"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    password = Column(String, nullable=True)
    user_email = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    invited_by = Column(String, nullable=True)
    modified_by = Column(Integer, nullable=True)
    change_password_token = Column(String, nullable=True)


class UserProjectEnv(Base):
    """Contains all the fields required for creating the table"""
    __tablename__ = 'user_project_env'

    upe_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=True)
    environment_id = Column(Integer, ForeignKey("environments.environment_id"), nullable=True)
    roles = Column(ARRAY(Enum(RolesEnum)), nullable=True)


class UserDetails(Base):
    __tablename__ = 'user_details'

    details_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    user_name = Column(String, nullable=True)
    user_contact = Column(BIGINT, nullable=True, unique=True)
    user_image = Column(String, nullable=True)
    activity_status = Column(Enum(ActivityStatus), nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class KeyStatus(PyEnum):
    """States the activity of a user"""
    DRAFT = 0
    PUBLISHED = 1


class Language(Base):
    __tablename__ = 'languages'

    language_id = Column(BIGINT, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=True)
    environment_id = Column(Integer, ForeignKey("environments.environment_id"), nullable=True)
    language = Column(String, unique=True, index=True)


class Key(Base):
    __tablename__ = "keys"

    key_id = Column(BIGINT, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=True)
    environment_id = Column(Integer, ForeignKey("environments.environment_id"), nullable=True)
    key = Column(String, nullable=False, unique=True)
    status = Column(Enum(KeyStatus), nullable=False)


class Translation(Base):
    __tablename__ = 'translations'

    translation_id = Column(BIGINT, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=True)
    environment_id = Column(Integer, ForeignKey("environments.environment_id"), nullable=True)
    key_id = Column(BIGINT, ForeignKey('keys.key_id'), index=True)
    language_id = Column(BIGINT, ForeignKey('languages.language_id'), index=True)
    translation = Column(String)
