from datetime import datetime

from app.v1.application.dto.dto_classes import ResponseDTO
from app.v1.domain import models, schema


def add_company_to_ucb(new_company, user_id, db):
    """Adds the company to ucb table"""
    try:
        db.query(models.UserProjectEnv).filter(models.UserProjectEnv.user_id == user_id).update(
            {"project_id": new_company.project_id})
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_branch_to_ucb(new_branch, user_id, project_id, db):
    """Adds the branch to Users company branch table"""
    try:
        env = db.query(models.UserProjectEnv).filter(models.UserProjectEnv.user_id == user_id).first()

        if env.environment_id is None:
            db.query(models.UserProjectEnv).filter(models.UserProjectEnv.user_id == user_id).update(
                {"environment_id": new_branch.environment_id})
            db.commit()
        elif env.environment_id != new_branch.environment_id:
            new_branch_in_ucb = models.UserProjectEnv(user_id=user_id, project_id=project_id,
                                                      environment_id=new_branch.environment_id, role=["OWNER"])
            db.add(new_branch_in_ucb)
            db.commit()
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_env(environment: schema.AddEnvironment, user_id, project_id, db, is_init: bool):
    """Creates a branch for a company"""
    try:
        project_exists = db.query(models.Projects).filter(models.Projects.project_id == project_id).first()
        if project_exists is None:
            return ResponseDTO(404, "Project not found!", {})
        new_env = models.Environments(environment_name=environment.environment_name, project_id=project_id,
                                      activity_status="ACTIVE", modified_on=datetime.now(), modified_by=user_id,
                                      is_main=environment.is_main)
        db.add(new_env)
        db.flush()

        # Adds the branch in Users_Company_Branches table
        add_branch_to_ucb(new_env, user_id, project_id, db)
        db.commit()
        if is_init:
            return {"environment_name": new_env.environment_name, "environment_id": new_env.environment_id}
        else:
            return ResponseDTO(200, "Branch created successfully!",
                               {"environment_name": new_env.environment_name, "environment_id": new_env.environment_id})
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_project(project: schema.AddProject, user_id, db):
    """Creates a company and adds a branch to it"""
    user_exists = db.query(models.UsersAuth).filter(models.UsersAuth.user_id == user_id).first()
    if user_exists is None:
        return ResponseDTO(404, "User does not exist!", {})

    new_project = models.Projects(project_name=project.project_name, owner=user_id, modified_by=user_id,
                                  activity_status=project.status, onboarding_date=datetime.now())
    db.add(new_project)
    db.commit()

    add_company_to_ucb(new_project, user_id, db)
    db.commit()
    db.refresh(new_project)

    environment = schema.AddEnvironment(environment_name=project.environment_name, is_main=project.is_main)
    init_branch = add_env(environment, user_id, new_project.project_id, db, True)

    return ResponseDTO(200, "Company created successfully",
                       {"project_name": new_project.project_name, "project_id": new_project.project_id,
                        "environment": init_branch})
