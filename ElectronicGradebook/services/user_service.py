from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ElectronicGradebook.models import Attendance, Grade, User
from ElectronicGradebook.routers.auth import bcrypt_context, get_db

from ..schemas.user import CreateUserRequest, EditUserRequest
from ..services.validation_service import (validate_class_exist,
                                           validate_database_relation,
                                           validate_roles,
                                           validate_subject_exist,
                                           validate_username_exist)

db_dependency = Annotated[Session, Depends(get_db)]


def create_user(request: CreateUserRequest, db: db_dependency):
    user_model = User(
        first_name=request.first_name,
        last_name=request.last_name,
        username=request.username,
        hashed_password=bcrypt_context.hash(request.password),
        date_of_birth=request.date_of_birth,
        class_id=request.class_id,
        subject_id=request.subject_id,
        role=request.role,
    )

    db.add(user_model)
    db.commit()


def edit_users(request: EditUserRequest, db: db_dependency, user_model, user: dict):
    if request.first_name is not None:
        user_model.first_name = request.first_name
    if request.last_name is not None:
        user_model.last_name = request.last_name
    if request.username is not None:
        validate_username_exist(user, request.username, db)
        user_model.username = request.username
    if request.password is not None:
        user_model.hashed_password = bcrypt_context.hash(request.password)
    if request.date_of_birth is not None:
        user_model.date_of_birth = request.date_of_birth
    if request.class_id is not None:
        validate_class_exist(user, request.class_id, db)
        user_model.class_id = request.class_id
    if request.subject_id is not None:
        validate_subject_exist(user, request.subject_id, db)
        user_model.subject_id = request.subject_id
    if request.role is not None:
        validate_roles(request.role, user)
        user_model.role = request.role

    db.commit()


def delete_users(user_id: int, db: db_dependency, user: dict):
    related_records = {
        "grades": db.query(Grade)
        .filter((Grade.student_id == user_id) | (Grade.added_by_id == user_id))
        .first(),
        "attendance": db.query(Attendance)
        .filter(
            (Attendance.student_id == user_id) | (Attendance.added_by_id == user_id)
        )
        .first(),
    }
    validate_database_relation(related_records, user_id, user)
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
