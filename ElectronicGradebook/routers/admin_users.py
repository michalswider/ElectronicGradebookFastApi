from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.orm import Session
from starlette import status

from ..models import User
from ..response_models.user import (map_student_to_response,
                                    map_teacher_to_response)
from ..routers.auth import get_db
from ..schemas.user import CreateUserRequest, EditUserRequest
from ..services.user_service import create_user, delete_users, edit_users
from ..services.validation_service import (validate_class_exist,
                                           validate_roles,
                                           validate_subject_exist,
                                           validate_user_id,
                                           validate_username_exist,
                                           validate_username_found,
                                           verify_admin_user)

router = APIRouter(prefix="/admin", tags=["admin-users"])


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/add-user", status_code=status.HTTP_201_CREATED)
async def add_user(
    request: Request, create_user_request: CreateUserRequest, db: db_dependency
):
    user = request.state.user
    verify_admin_user(user)
    validate_username_exist(user, create_user_request.username, db)
    if create_user_request.class_id:
        validate_class_exist(user, create_user_request.class_id, db)
    if create_user_request.subject_id:
        validate_subject_exist(user, create_user_request.subject_id, db)
    validate_roles(create_user_request.role, user)
    create_user(create_user_request, db)


@router.get("/students", status_code=status.HTTP_200_OK)
async def show_all_students(request: Request, db: db_dependency):
    user = request.state.user
    verify_admin_user(user)
    students = db.query(User).filter(User.role == "student").all()
    result = [map_student_to_response(student) for student in students]
    return result


@router.get("/teachers", status_code=status.HTTP_200_OK)
async def show_all_teachers(request: Request, db: db_dependency):
    user = request.state.user
    verify_admin_user(user)
    teachers = db.query(User).filter(User.role == "teacher").all()
    result = [map_teacher_to_response(teacher) for teacher in teachers]
    return result


@router.get("/students/", status_code=status.HTTP_200_OK)
async def show_student_detail(
    request: Request, db: db_dependency, username: str = Query()
):
    user = request.state.user
    verify_admin_user(user)
    student = validate_username_found(user, username, db, role="student")
    result = map_student_to_response(student)
    return result


@router.get("/teachers/", status_code=status.HTTP_200_OK)
async def show_teacher_detail(
    request: Request, db: db_dependency, username: str = Query()
):
    user = request.state.user
    verify_admin_user(user)
    teacher = validate_username_found(user, username, db, role="teacher")
    result = map_teacher_to_response(teacher)
    return result


@router.put("/edit-user/", status_code=status.HTTP_204_NO_CONTENT)
async def edit_user(
    edit_user_request: EditUserRequest,
    request: Request,
    db: db_dependency,
    username: str = Query(),
):
    user = request.state.user
    verify_admin_user(user)
    user_model = validate_username_found(user, username, db, role="all")
    edit_users(edit_user_request, db, user_model, user)


@router.delete("/delete-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: Request, db: db_dependency, user_id: int = Path(gt=0)):
    user = request.state.user
    verify_admin_user(user)
    validate_user_id(user_id, db, user, role="all")
    delete_users(user_id, db, user)
