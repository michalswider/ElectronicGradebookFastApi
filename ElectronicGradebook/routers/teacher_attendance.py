from datetime import date
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Request
from ..response_models.attendance import map_student_attendance_to_response, \
    map_attendance_for_class_on_date_to_response, map_attendance_for_student_in_subject
from ..schemas.attendance import AddAttendanceRequest,EditAttendanceStatusRequest
from sqlalchemy.orm import Session
from starlette import status
from ..routers.auth import get_db
from ..services.attendance_service import create_attendance, edit_attendance, delete_attendances
from ..services.validation_service import verify_teacher_user, validate_user_id, validate_subject_exist, \
    validate_attendance_status, validate_student_attendance, validate_class_exist, \
    validate_attendance_for_class_on_date, validate_attendance_for_student_in_subject, validate_attendance_data

router = APIRouter(
    prefix='/teacher',
    tags=['teacher-attendance']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/add-attendance", status_code=status.HTTP_201_CREATED)
async def add_attendance(request: Request, db: db_dependency, add_attendance_request: AddAttendanceRequest):
    user = request.state.user
    verify_teacher_user(user)
    validate_user_id(add_attendance_request.student_id,db,user,role="student")
    validate_subject_exist(user, add_attendance_request.subject_id, db)
    validate_attendance_status(add_attendance_request.status, user)
    create_attendance(add_attendance_request, db,user)


@router.get("/show-student-attendance/{student_id}", status_code=status.HTTP_200_OK)
async def show_student_attendance(request: Request, db: db_dependency, student_id: int = Path(gt=0)):
    user = request.state.user
    verify_teacher_user(user)
    validate_user_id(student_id,db,user,role="student")
    attendance_model = validate_student_attendance(student_id,db,user,role="teacher")
    return map_student_attendance_to_response(attendance_model)


@router.get("/attendance/class/{class_id}/date", status_code=status.HTTP_200_OK)
async def get_attendance_for_class_on_date(request: Request, db: db_dependency, class_id: int = Path(gt=0),
                                           date: date = Query()):
    user = request.state.user
    verify_teacher_user(user)
    validate_class_exist(user,class_id,db)
    attendance_model = validate_attendance_for_class_on_date(class_id,date,user,db)
    return map_attendance_for_class_on_date_to_response(attendance_model)


@router.get("/attendance/subject/{subject_id}/student/{student_id}", status_code=status.HTTP_200_OK)
async def get_attendance_for_student_in_subject(request: Request, db: db_dependency, subject_id: int = Path(gt=0),
                                                student_id: int = Path(gt=0)):
    user = request.state.user
    verify_teacher_user(user)
    validate_subject_exist(user,subject_id,db)
    validate_user_id(student_id,db,user,role="student")
    attendance_model = validate_attendance_for_student_in_subject(student_id,subject_id,user,db)
    return map_attendance_for_student_in_subject(attendance_model)


@router.put("/edit-attendance/{student_id}/{subject_id}/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_attendance_status(request: Request, db: db_dependency,
                                 edit_attendance_status_request: EditAttendanceStatusRequest,
                                 attendance_id: int = Path(gt=0), subject_id: int = Path(gt=0),
                                 student_id: int = Path(gt=0)):
    user = request.state.user
    verify_teacher_user(user)
    validate_subject_exist(user,subject_id,db)
    validate_user_id(student_id,db,user,role="student")
    attendance_model = validate_attendance_data(attendance_id,student_id,subject_id,user,db)
    validate_attendance_status(edit_attendance_status_request.status,user)
    edit_attendance(attendance_model,edit_attendance_status_request,db)


@router.delete("/delete-attendance/{student_id}/{subject_id}/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(request: Request, db: db_dependency, student_id: int = Path(gt=0),
                            subject_id: int = Path(gt=0),
                            attendance_id: int = Path(gt=0)):
    user = request.state.user
    verify_teacher_user(user)
    validate_user_id(student_id,db,user,role="student")
    validate_subject_exist(user,subject_id,db)
    attendance_model = validate_attendance_data(attendance_id,student_id,subject_id,user,db)
    delete_attendances(attendance_model,db)
