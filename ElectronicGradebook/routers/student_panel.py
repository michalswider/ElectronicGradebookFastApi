from typing import Annotated
from ..models import Grade, Subject, Attendance
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from ..models import User, Class
from ..routers.auth import get_db, get_current_user, bcrypt_context

router = APIRouter(
    prefix='/student',
    tags=['student-panel']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserVerification(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


@router.get("/profile", status_code=status.HTTP_200_OK)
async def show_profile_detail(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'student'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    student_model = db.query(User).filter(User.id == user.get('id')).all()
    result = []
    for detail in student_model:
        result.append({
            "first_name": detail.first_name,
            "last_name": detail.last_name,
            'username': detail.username,
            "date_of_birth": detail.date_of_birth,
            "class": detail.klasa.name if detail.klasa else "No class assigned",
            "role": detail.role
        })
    return result


@router.put("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if not bcrypt_context.verify(user_verification.old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.get("/grades", status_code=status.HTTP_200_OK)
async def show_grades(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('student', 'admin'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    grades_model = (
        db.query(Grade)
        .join(User, Grade.student_id == User.id)
        .join(Subject, Grade.subject_id == Subject.id)
        .filter(Grade.student_id == user.get('id'))
        .all()
    )
    if not grades_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    result = {}
    for grade in grades_model:
        subject_name = grade.subject.name
        if subject_name not in result:
            result[subject_name] = []
        result[subject_name].append({
            'grade': grade.grade,
            'date': grade.date,
            'added_by': grade.teacher.first_name + " " + grade.teacher.last_name
        })
    return result


@router.get("/attendance", status_code=status.HTTP_200_OK)
async def show_attendance(user: user_dependency, db: db_dependency):
    attendance_model = db.query(Attendance).join(User, Attendance.student_id == User.id).join(Subject,
                                                                                              Attendance.subject_id == Subject.id).filter(
        Attendance.student_id == user.get('id')).all()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('student', 'admin'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    if not attendance_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    result = {}
    for attendance in attendance_model:
        attendance_subject = attendance.subject.name
        if attendance_subject not in result:
            result[attendance_subject] = []
        result[attendance_subject].append({
            'class_date': attendance.class_date,
            'status': attendance.status,
            'added_by': attendance.teacher.first_name + " " + attendance.teacher.last_name
        })
    return result
