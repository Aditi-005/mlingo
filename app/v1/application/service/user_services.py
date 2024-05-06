import random
import smtplib
import string

from fastapi import Depends

from app.infrastructure.database import get_db
from app.v1.application.dto.dto_classes import ResponseDTO
from app.v1.application.password_handler.pwd_encrypt_decrypt import verify, hash_pwd
from app.v1.domain import models, schema


def get_projects(ucb, db):
    try:
        projects = []
        for user_project in ucb:
            proj = db.query(models.Projects).filter(models.Projects.project_id == user_project.project_id).all()
            if proj:
                for project in proj:
                    env = db.query(models.Environments).filter(
                        models.Environments.project_id == project.project_id).all()
                    projects.append({"project_id": project.project_id,
                                     "project_name": project.project_name,
                                     "project_logo": project.project_logo,
                                     "env": get_environments(project.project_id, db)})

            return projects

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def get_environments(project_id, db):
    environments = []
    env = db.query(models.Environments).filter(
        models.Environments.project_id == project_id).all()
    if env:
        for environment in env:
            environments.append({"environment_id": environment.environment_id,
                                 "environment_name": environment.environment_name})
    return environments


def auth_function(credentials: schema.Credentials, db=Depends(get_db)):
    try:
        email = credentials.email
        pwd = credentials.password

        is_user_present = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == email).first()

        if is_user_present is None:
            return ResponseDTO(404, "User is not registered, please register.", {})

        if is_user_present.password is None:
            return ResponseDTO(404, "Password is not set yet. Please set your password", {})

        if not verify(pwd, is_user_present.password):
            return ResponseDTO(401, "Password Incorrect!", {})

        user_details = db.query(models.UserDetails).filter(
            models.UserDetails.user_id == is_user_present.user_id).first()

        user_projects = db.query(models.UserProjectEnv).filter(
            models.UserProjectEnv.user_id == is_user_present.user_id).all()
        if user_projects:
            projects = get_projects(user_projects, db)
        else:
            projects = []

        return ResponseDTO(200, "Login successful",
                           schema.LoginResponse(user_id=is_user_present.user_id,
                                                name=user_details.user_name, projects=projects))

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_owner_to_ucb(new_user, db):
    """Adds the data mapped to a user into db"""
    try:
        ucb = models.UserProjectEnv(user_id=new_user.user_id)
        db.add(ucb)
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_user_details(user: schema.AddUser, user_id, db):
    """Adds user details in the db"""
    try:
        user_details = models.UserDetails(user_id=user_id, user_name=user.user_name, user_contact=user.user_contact)
        db.add(user_details)
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_user(user: schema.AddUser, db):
    """Adds a user into the database"""
    # try:
    user_email_exists = db.query(models.UsersAuth).filter(
        models.UsersAuth.user_email == user.user_email).first()

    if user_email_exists:
        return ResponseDTO(403, "User with this email already exists", {})
    hashed_pwd = hash_pwd(user.password)
    user.password = hashed_pwd
    new_user = models.UsersAuth(user_email=user.user_email, password=user.password)
    db.add(new_user)
    db.flush()

    add_user_details(user, new_user.user_id, db)
    add_owner_to_ucb(new_user, db)

    db.commit()
    db.refresh(new_user)

    return ResponseDTO(200, "User created successfully",
                       {"user_id": new_user.user_id, "name": user.user_name, "company": []})


# except Exception as exc:
#     return ResponseDTO(204, str(exc), {})


"""-------------------------------Update password code starts below this line-----------------------------"""


def check_token(obj, db):
    """Verifies the reset token stored in DB, against the token entered by an individual"""
    try:
        user = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == obj.email).first()
        if user is None:
            return ResponseDTO(404, "User not found!", {})
        else:
            if user.change_password_token != obj.token:
                return ResponseDTO(204, "Reset token doesn't match", {})
            else:
                return change_password(obj, db)
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def change_password(obj, db):
    """Updates the password and makes the change_password_token null in db"""
    user_query = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == obj.model_dump()["email"])
    user = user_query.first()

    if user is None:
        return ResponseDTO(404, "User with this email does not exist!", {})

    if user.change_password_token != obj.model_dump()["token"]:
        return ResponseDTO(204, "Reset token doesn't match", {})

    hashed_pwd = hash_pwd(obj.model_dump()["password"])
    user_query.update({"change_password_token": None, "password": hashed_pwd})
    db.commit()

    return ResponseDTO(200, "Password updated successfully!", {})


"""-------------------------------Code below this line sends the change_password_token to an individual-----------------------------"""


def create_smtp_session(fetched_email, msg):
    """Creates a smtp session and sends an email. The exception handling is done by the library itself"""
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()

        # Authentication
        s.login("aditi.diwan005@gmail.com", "odxfrxoyfcgzwsks")

        s.sendmail("aditi.diwan005@gmail.com", fetched_email, msg)

        s.quit()

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def temporarily_add_token(reset_code, fetched_email, db):
    """Temporarily stores the reset code in DB"""
    try:
        user_query = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == fetched_email)

        user_query.update({"change_password_token": reset_code})
        db.commit()
        create_smtp_session(fetched_email, reset_code)

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def create_password_reset_code(fetched_email, db):
    """Creates a 6 digit reset code"""
    try:
        code_length = 6
        reset_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length))

        temporarily_add_token(reset_code, fetched_email, db)
        return reset_code

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def initiate_pwd_reset(email, db):
    """Fetches the user who has requested for password reset and calls a method to create a smtp session"""
    try:
        fetched_user = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == email).first()
        if fetched_user:
            fetched_email = fetched_user.user_email
            create_password_reset_code(fetched_email, db)
        else:
            return ResponseDTO(404, "User not found", {})

        return ResponseDTO(200, "Email sent successfully", {})

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
