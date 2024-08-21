from datetime import date
from typing import Annotated
from ..models import Attendance, User, Subject, Class
from fastapi import APIRouter, Depends, Path, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from ..routers.auth import get_db, get_current_user
from ..exception import SubjectNotExistException, InvalidStatusException, \
    StudentAttendanceNotFoundException, ClassNotExistException, ClassAttendanceOnDateNotFoundException, \
    AttendanceForStudentInSubjectNotFoundException, UserIdNotFoundException, AttendanceNotFoundException, \
    AttendanceDataNotFoundException

router = APIRouter(
    prefix='/teacher',
    tags=['teacher-attendance']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class AddAttendanceRequest(BaseModel):
    student_id: int = Field(gt=0)
    subject_id: int = Field(gt=0)
    class_date: date
    status: str


class EditAttendanceStatusRequest(BaseModel):
    status: str


@router.post("/add-attendance", status_code=status.HTTP_201_CREATED)
async def add_attendance(db: db_dependency, user: user_dependency, add_attendance_request: AddAttendanceRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    student_model = db.query(User).filter(User.id == add_attendance_request.student_id, User.role == 'student').first()
    subject_model = db.query(Subject).filter(Subject.id == add_attendance_request.subject_id).first()
    if student_model is None:
        raise UserIdNotFoundException(user_id=add_attendance_request.student_id, username=user.get('username'))
    if subject_model is None:
        raise SubjectNotExistException(subject_id=add_attendance_request.subject_id, username=user.get('username'))
    if add_attendance_request.status not in ('present', 'absent', 'excused'):
        raise InvalidStatusException(status=add_attendance_request.status, username=user.get('username'))
    attendance_model = Attendance(**add_attendance_request.dict(), added_by_id=user.get('id'))
    db.add(attendance_model)
    db.commit()


@router.get("/show-student-attendance/{student_id}", status_code=status.HTTP_200_OK)
async def show_student_attendance(db: db_dependency, user: user_dependency, student_id: int = Path(gt=0)):
    attendance_model = db.query(Attendance).join(User, Attendance.student_id == User.id).join(Subject,
                                                                                              Attendance.subject_id == Subject.id).filter(
        Attendance.student_id == student_id).all()
    student_model = db.query(User).filter(User.id == student_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    if student_model is None:
        raise UserIdNotFoundException(user_id=student_id, username=user.get('username'))
    if not attendance_model:
        raise StudentAttendanceNotFoundException(student_id=student_id, username=user.get('username'))
    result = {}
    for attendance in attendance_model:
        attendance_subject = attendance.subject.name
        if attendance_subject not in result:
            result[attendance_subject] = []
        result[attendance_subject].append({
            'id': attendance.id,
            'class_date': attendance.class_date,
            'status': attendance.status,
            'added_by': attendance.teacher.first_name + " " + attendance.teacher.last_name
        })
    return result


@router.get("/attendance/class/{class_id}/date")
async def get_attendance_for_class_on_date(db: db_dependency, user: user_dependency, class_id: int = Path(gt=0),
                                           date: date = Query()):
    attendance_model = db.query(Attendance).join(User, Attendance.student_id == User.id).join(Class,
                                                                                              Class.id == User.class_id).filter(
        Attendance.class_date == date, Class.id == class_id).all()
    class_model = db.query(Class).filter(Class.id == class_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    if class_model is None:
        raise ClassNotExistException(class_id=class_id, username=user.get('username'))
    if not attendance_model:
        raise ClassAttendanceOnDateNotFoundException(class_id=class_id, date=date, username=user.get('username'))
    result = {}
    for attendance in attendance_model:
        attendance_class = attendance.student.klasa.name
        attendance_subject = attendance.subject.name
        attendance_student = f"{attendance.student.first_name} {attendance.student.last_name}"

        if attendance_class not in result:
            result[attendance_class] = {}
        if attendance_subject not in result[attendance_class]:
            result[attendance_class][attendance_subject] = {}
        if attendance_student not in result[attendance_class][attendance_subject]:
            result[attendance_class][attendance_subject][attendance_student] = []

        result[attendance_class][attendance_subject][attendance_student].append({
            'class_date': attendance.class_date,
            'status': attendance.status,
            'added_by': attendance.teacher.first_name + " " + attendance.teacher.last_name
        })
    return result


@router.get("/attendance/subject/{subject_id}/student/{student_id}")
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
        raise AttendanceForStudentInSubjectNotFoundException(student_id=student_id, subject_id=subject_id, username=user.get('username'))
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
        raise AttendanceDataNotFoundException(attendance_id=attendance_id, subject_id=subject_id, student_id=student_id, username= user.get('username'))
    if edit_attendance_status_request.status not in ('present', 'absent', 'excused'):
        raise InvalidStatusException(status=edit_attendance_status_request.status, username= user.get('username'))
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
        raise AttendanceDataNotFoundException(attendance_id=attendance_id, subject_id=subject_id, student_id=student_id, username=user.get('username'))
    db.delete(attendance_model)
    db.commit()
