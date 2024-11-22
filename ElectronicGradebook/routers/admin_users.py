from typing import Annotated
from fastapi import APIRouter, Depends, Path, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status
from ..exception import UserIdNotFoundException, UserDeleteException
from ..models import User,Grade, Attendance
from ..routers.auth import get_db,get_current_user
from ..services.user_service import create_user,edit_users
from ..services.validation_service import verify_admin_user, validate_username_exist, validate_class_exist, \
    validate_subject_exist, validate_roles, validate_username_found
from ..response_models.user import map_student_to_response, map_teacher_to_response
from ..schemas.user import CreateUserRequest,EditUserRequest

router = APIRouter(
    prefix='/admin',
    tags=['admin-users']
)



db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/add-user", status_code=status.HTTP_201_CREATED)
async def add_user(user: user_dependency,create_user_request: CreateUserRequest, db: db_dependency):
    verify_admin_user(user)
    validate_username_exist(user, create_user_request.username, db)
    if create_user_request.class_id:
        validate_class_exist(user, create_user_request.class_id, db)
    if create_user_request.subject_id:
        validate_subject_exist(user, create_user_request.subject_id, db)
    validate_roles(create_user_request.role, user)
    create_user(create_user_request, db)


@router.get("/students", status_code=status.HTTP_200_OK)
async def show_all_students(db: db_dependency, user: user_dependency):
    verify_admin_user(user)
    students = db.query(User).filter(User.role == 'student').all()
    result = [map_student_to_response(student) for student in students]
    return result


@router.get("/teachers", status_code=status.HTTP_200_OK)
async def show_all_teachers(db: db_dependency, user: user_dependency):
    verify_admin_user(user)
    teachers = db.query(User).filter(User.role == 'teacher').all()
    result = [map_teacher_to_response(teacher) for teacher in teachers]
    return result


@router.get("/students/", status_code=status.HTTP_200_OK)
async def show_student_detail(db: db_dependency, user: user_dependency, username: str = Query()):
    verify_admin_user(user)
    student = db.query(User).filter(User.username == username, User.role == 'student').first()
    validate_username_found(student,user, username)
    result = map_student_to_response(student)
    return result


@router.get("/teachers/", status_code=status.HTTP_200_OK)
async def show_teacher_detail(db: db_dependency, user: user_dependency, username: str = Query()):
    verify_admin_user(user)
    teacher = db.query(User).filter(User.username == username, User.role == 'teacher').first()
    validate_username_found(teacher,user, username)
    result = map_teacher_to_response(teacher)
    return result


@router.put("/edit-user/", status_code=status.HTTP_204_NO_CONTENT)
async def edit_user(edit_user_request: EditUserRequest, user: user_dependency, db: db_dependency, username: str = Query()):
    verify_admin_user(user)
    user_model = db.query(User).filter(User.username == username).first()
    validate_username_found(user_model, user,username)
    edit_users(edit_user_request,db,user_model,user)



@router.delete("/delete-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user: user_dependency, user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    user_model = db.query(User).filter(User.id == user_id).first()
    related_grades = db.query(Grade).filter(Grade.student_id == user_id).all()
    related_grades_added_by = db.query(Grade).filter(Grade.added_by_id == user_id).all()
    related_attendance = db.query(Attendance).filter(Attendance.student_id == user_id).all()
    related_attendance_added_by = db.query(Attendance).filter(Attendance.added_by_id == user_id).all()
    if user_model is None:
        raise UserIdNotFoundException(user_id=user_id, username=user.get('username'))
    if related_grades:
        raise UserDeleteException(user_id=user_id, table_name='grades', username=user.get('username'))
    if related_grades_added_by:
        raise UserDeleteException(user_id=user_id, table_name='grades', username=user.get('username'))
    if related_attendance:
        raise UserDeleteException(user_id=user_id, table_name='attendance', username=user.get('username'))
    if related_attendance_added_by:
        raise UserDeleteException(user_id=user_id, table_name='attendance', username=user.get('username'))
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
