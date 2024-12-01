from datetime import date
from typing import Annotated
from ..models import Attendance, User, Subject, Class
from fastapi import APIRouter, Depends, Path, HTTPException, Query
from ..response_models.attendance import map_student_attendance_to_response, \
    map_attendance_for_class_on_date_to_response
from ..schemas.attendance import AddAttendanceRequest,EditAttendanceStatusRequest
from sqlalchemy.orm import Session
from starlette import status
from ..routers.auth import get_db, get_current_user
from ..exception import SubjectNotExistException, InvalidStatusException, \
    AttendanceForStudentInSubjectNotFoundException, UserIdNotFoundException, AttendanceNotFoundException, \
    AttendanceDataNotFoundException
from ..services.attendance_service import create_attendance
from ..services.validation_service import verify_teacher_user, validate_user_id, validate_subject_exist, \
    validate_attendance_status, validate_student_attendance, validate_class_exist, validate_attendance_for_class_on_date

router = APIRouter(
    prefix='/teacher',
    tags=['teacher-attendance']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/add-attendance", status_code=status.HTTP_201_CREATED)
async def add_attendance(db: db_dependency, user: user_dependency, add_attendance_request: AddAttendanceRequest):
    verify_teacher_user(user)
    validate_user_id(add_attendance_request.student_id,db,user,role="student")
    validate_subject_exist(user, add_attendance_request.subject_id, db)
    validate_attendance_status(add_attendance_request.status, user)
    create_attendance(add_attendance_request, db,user)


@router.get("/show-student-attendance/{student_id}", status_code=status.HTTP_200_OK)
async def show_student_attendance(db: db_dependency, user: user_dependency, student_id: int = Path(gt=0)):
    verify_teacher_user(user)
    validate_user_id(student_id,db,user,role="student")
    attendance_model = validate_student_attendance(student_id,db,user)
    return map_student_attendance_to_response(attendance_model)


@router.get("/attendance/class/{class_id}/date", status_code=status.HTTP_200_OK)
async def get_attendance_for_class_on_date(db: db_dependency, user: user_dependency, class_id: int = Path(gt=0),
                                           date: date = Query()):
    verify_teacher_user(user)
    validate_class_exist(user,class_id,db)
    attendance_model = validate_attendance_for_class_on_date(class_id,date,user,db)
    return map_attendance_for_class_on_date_to_response(attendance_model)


@router.get("/attendance/subject/{subject_id}/student/{student_id}", status_code=status.HTTP_200_OK)
async def get_attendance_for_student_in_subject(db: db_dependency, user: user_dependency, subject_id: int = Path(gt=0),
                                                student_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    attendance_model = db.query(Attendance).join(User, User.id == Attendance.student_id).join(Subject,
                                                                                              Subject.id == Attendance.subject_id).filter(
        Attendance.subject_id == subject_id, Attendance.student_id == student_id).all()
    subject_model = db.query(Subject).filter(Subject.id == subject_id).first()
    student_model = db.query(User).filter(User.id == student_id, User.role == 'student').first()
    if subject_model is None:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))
    if student_model is None:
        raise UserIdNotFoundException(user_id=student_id, username=user.get('username'))
    if not attendance_model:
        raise AttendanceForStudentInSubjectNotFoundException(student_id=student_id, subject_id=subject_id,
                                                             username=user.get('username'))
    result = []
    for attendance in attendance_model:
        result.append({
            'id': attendance.id,
            'class_date': attendance.class_date,
            'status': attendance.status,
            'added_by': attendance.teacher.first_name + " " + attendance.teacher.last_name
        })
    return result


@router.put("/edit-attendance/{student_id}/{subject_id}/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_attendance_status(db: db_dependency, user: user_dependency,
                                 edit_attendance_status_request: EditAttendanceStatusRequest,
                                 attendance_id: int = Path(gt=0), subject_id: int = Path(gt=0),
                                 student_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    attendance_model = db.query(Attendance).filter(Attendance.id == attendance_id,
                                                   Attendance.student_id == student_id,
                                                   Attendance.subject_id == subject_id).first()
    attendance_id_model = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    subject_model = db.query(Subject).filter(Subject.id == subject_id).first()
    student_model = db.query(User).filter(User.id == student_id, User.role == 'student').first()
    if attendance_id_model is None:
        raise AttendanceNotFoundException(attendance_id=attendance_id, username=user.get('username'))
    if subject_model is None:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))
    if student_model is None:
        raise UserIdNotFoundException(user_id=student_id, username=user.get('username'))
    if attendance_model is None:
        raise AttendanceDataNotFoundException(attendance_id=attendance_id, subject_id=subject_id, student_id=student_id,
                                              username=user.get('username'))
    if edit_attendance_status_request.status not in ('present', 'absent', 'excused'):
        raise InvalidStatusException(status=edit_attendance_status_request.status, username=user.get('username'))
    attendance_model.status = edit_attendance_status_request.status
    db.add(attendance_model)
    db.commit()


@router.delete("/delete-attendance/{student_id}/{subject_id}/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(db: db_dependency, user: user_dependency, student_id: int = Path(gt=0),
                            subject_id: int = Path(gt=0),
                            attendance_id: int = Path(gt=0)) -> None:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    attendance_model = db.query(Attendance).filter(Attendance.student_id == student_id,
                                                   Attendance.subject_id == subject_id,
                                                   Attendance.id == attendance_id).first()
    subject_model = db.query(Subject).filter(Subject.id == subject_id).first()
    student_model = db.query(User).filter(User.id == student_id, User.role == 'student').first()
    if student_model is None:
        raise UserIdNotFoundException(user_id=student_id, username=user.get('username'))
    if subject_model is None:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))
    if attendance_model is None:
        raise AttendanceDataNotFoundException(attendance_id=attendance_id, subject_id=subject_id, student_id=student_id,
                                              username=user.get('username'))
    db.delete(attendance_model)
    db.commit()
