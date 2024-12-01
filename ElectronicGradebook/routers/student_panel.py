from typing import Annotated
from ..models import Grade, Subject, Attendance
from fastapi import APIRouter, Depends, HTTPException
from ..response_models.student import map_student_profile_to_response
from ..schemas.students import UserVerification
from sqlalchemy.orm import Session
from starlette import status
from ..models import User
from ..routers.auth import get_db, get_current_user, bcrypt_context
from ..services.validation_service import verify_student_user

router = APIRouter(
    prefix='/student',
    tags=['student-panel']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/profile", status_code=status.HTTP_200_OK)
async def show_profile_detail(user: user_dependency, db: db_dependency):
    verify_student_user(user)
    student = db.query(User).filter(User.id == user.get('id')).first()
    result = map_student_profile_to_response(student)
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
