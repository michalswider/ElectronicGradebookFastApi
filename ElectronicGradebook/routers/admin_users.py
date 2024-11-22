from datetime import date
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Path, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from ..exception import UsernameNotFoundException, ClassNotExistException, SubjectNotExistException, InvalidRoleException, \
    UserIdNotFoundException, UsernameAlreadyExistException, UserDeleteException
from ..models import User, Class, Subject, Grade, Attendance
from ..routers.auth import get_db, bcrypt_context, get_current_user
from ..services.user_service import create_user
from ..services.validation_service import verify_admin_user, validate_username_exist, validate_class_exist, \
    validate_subject_exist, validate_roles

router = APIRouter(
    prefix='/admin',
    tags=['admin-users']
)


class UserRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    username: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    date_of_birth: Optional[date] = None
    class_id: Optional[int] = None
    subject_id: Optional[int] = None
    role: Optional[str] = None


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/add-user", status_code=status.HTTP_201_CREATED)
async def add_user(user: user_dependency,create_user_request: UserRequest, db: db_dependency):
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
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    students = db.query(User).filter(User.role == 'student').all()
    result = []
    for student in students:
        result.append({'id': student.id,
                       'first_name': student.first_name,
                       'last_name': student.last_name,
                       'username': student.username,
                       'hashed_password': student.hashed_password,
                       'date_of_birth': student.date_of_birth,
                       'class': student.klasa.name if student.klasa else "No class assigned",
                       'role': student.role
                       })
    return result


@router.get("/teachers", status_code=status.HTTP_200_OK)
async def show_all_teachers(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    teachers = db.query(User).filter(User.role == 'teacher').all()
    result = []
    for teacher in teachers:
        result.append({'id': teacher.id,
                       'first_name': teacher.first_name,
                       'last_name': teacher.last_name,
                       'username': teacher.username,
                       'hashed_password': teacher.hashed_password,
                       'subject': teacher.subject.name if teacher.subject else "No subject assigned",
                       'role': teacher.role
                       })
    return result


@router.get("/students/", status_code=status.HTTP_200_OK)
async def show_student_detail(db: db_dependency, user: user_dependency, username: str = Query()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    student = db.query(User).filter(User.username == username, User.role == 'student').first()
    if student is None:
        raise UsernameNotFoundException(username=username, user=user.get('username'))
    result = [{'id': student.id,
               'first_name': student.first_name,
               'last_name': student.last_name,
               'username': student.username,
               'hashed_password': student.hashed_password,
               'date_of_birth': student.date_of_birth,
               'class': student.klasa.name if student.klasa else "No class assigned",
               'role': student.role
               }]
    return result


@router.get("/teachers/", status_code=status.HTTP_200_OK)
async def show_teacher_detail(db: db_dependency, user: user_dependency, username: str = Query()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    teacher = db.query(User).filter(User.username == username, User.role == 'teacher').first()
    if teacher is None:
        raise UsernameNotFoundException(username=username, user=user.get('username'))
    result = [{'id': teacher.id,
               'first_name': teacher.first_name,
               'last_name': teacher.last_name,
               'username': teacher.username,
               'hashed_password': teacher.hashed_password,
               'subject': teacher.subject.name if teacher.subject else "No subject assigned",
               'role': teacher.role
               }]
    return result


@router.put("/edit-user/", status_code=status.HTTP_204_NO_CONTENT)
async def edit_user(edit_user_request: UserRequest, user: user_dependency, db: db_dependency, username: str = Query()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    user_model = db.query(User).filter(User.username == username).first()
    if user_model is None:
        raise UsernameNotFoundException(username=username, user=user.get('username'))
    if edit_user_request.first_name is not None:
        user_model.first_name = edit_user_request.first_name
    if edit_user_request.last_name is not None:
        user_model.last_name = edit_user_request.last_name
    if edit_user_request.username is not None:
        username_model = db.query(User).filter(User.username == edit_user_request.username).first()
        if username_model is not None:
            raise UsernameAlreadyExistException(username=edit_user_request.username, user=user.get('username'))
        user_model.username = edit_user_request.username
    if edit_user_request.password is not None:
        user_model.hashed_password = bcrypt_context.hash(edit_user_request.password)
    if edit_user_request.date_of_birth is not None:
        user_model.date_of_birth = edit_user_request.date_of_birth
    if edit_user_request.class_id is not None:
        classes = db.query(Class).filter(Class.id == edit_user_request.class_id).first()
        if not classes:
            raise ClassNotExistException(class_id=edit_user_request.class_id, username=user.get('username'))
        user_model.class_id = edit_user_request.class_id
    if edit_user_request.subject_id is not None:
        subjects = db.query(Subject).filter(Subject.id == edit_user_request.subject_id).first()
        if not subjects:
            raise SubjectNotExistException(subject_id=edit_user_request.subject_id, username=user.get('username'))
        user_model.subject_id = edit_user_request.subject_id
    if edit_user_request.role is not None:
        if edit_user_request.role not in ('admin', 'teacher', 'student'):
            raise InvalidRoleException(role=edit_user_request.role, username=user.get('username'))
        user_model.role = edit_user_request.role

    db.commit()


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
