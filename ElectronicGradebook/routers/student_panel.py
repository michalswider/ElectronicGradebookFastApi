from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from ..response_models.student import map_student_profile_to_response, map_student_grade_to_response,map_student_attendance_to_response
from ..schemas.students import UserVerification
from sqlalchemy.orm import Session
from starlette import status
from ..models import User
from ..routers.auth import get_db, get_current_user
from ..services.student_service import edit_password
from ..services.validation_service import verify_student_user, validate_password_reset, validate_user_grades, \
    validate_student_attendance

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
    verify_student_user(user)
    student = validate_password_reset(user_verification,user.get("id"),db)
    edit_password(user_verification,student,db)


@router.get("/grades", status_code=status.HTTP_200_OK)
async def show_grades(user: user_dependency, db: db_dependency):
    verify_student_user(user)
    grades = validate_user_grades(user.get('id'), user, db,role="student")
    return map_student_grade_to_response(grades)


@router.get("/attendance", status_code=status.HTTP_200_OK)
async def show_attendance(user: user_dependency, db: db_dependency):
    verify_student_user(user)
    attendance_model = validate_student_attendance(user.get("id"), db, user, role="student")
    return map_student_attendance_to_response(attendance_model)
