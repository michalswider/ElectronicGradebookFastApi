from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from ..routers.auth import get_db
from fastapi import HTTPException
from starlette import status
from datetime import date
from ..models import User, Class, Subject, Grade, Attendance
from ..routers.auth import bcrypt_context
from ..exception import ExistException, InvalidException, NotFoundException, ForeignKeyConstraintException
from ..schemas.students import UserVerification

db_dependency = Annotated[Session, Depends(get_db)]


def verify_admin_user(user: dict):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')


def verify_teacher_user(user: dict):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')

def verify_student_user(user: dict):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'student'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')

def validate_username_exist(user: dict, username: str, db: db_dependency):
    username_model = db.query(User).filter(User.username == username).first()
    if username_model is not None:
        raise ExistException(detail=f'Username: {username} already exist.', user=user.get('username'))


def validate_class_exist(user: dict, class_id: int, db: db_dependency):
    classes = db.query(Class).filter(Class.id == class_id).first()
    if not classes:
        raise ExistException(detail=f'Class with id: {class_id} does not exist', user=user.get('username'))


def validate_subject_exist(user: dict, subject_id: int, db: db_dependency):
    subjects = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subjects:
        raise ExistException(detail=f'Subject with id: {subject_id} does not exist', user=user.get('username'))


def validate_roles(role: str, user: dict):
    valid_roles = ['admin', 'teacher', 'student']
    if role not in valid_roles:
        raise InvalidException(detail=f"Invalid role: {role}. Allowed roles are 'admin', 'teacher','student'.", user=user.get('username'))


def validate_username_found(user_model: User, user: dict, username: str):
    if user_model is None:
        raise NotFoundException(detail=f'User with username: {username} not found', user=user.get('username'))


def validate_database_relation(related_records: dict, user_id: int, user: dict):
    for table_name, record in related_records.items():
        if record:
            raise ForeignKeyConstraintException(detail=f'User with id: {user_id} cannot be deleted because it is associated with table: {table_name}.', user=user.get('username'))


def validate_database_subjects_relation(related_records: dict, subject_id: int, user: dict):
    for table_name, record in related_records.items():
        if record:
            raise ForeignKeyConstraintException(f'Subject with id: {subject_id} cannot be deleted because it is associated with table: {table_name}.', user=user.get('username'))


def validate_user_id(user_id, db: db_dependency, user: dict, role: str, ):
    if role == "student":
        user_model = db.query(User).filter(User.id == user_id, User.role == 'student').first()
    elif role == "teacher":
        user_model = db.query(User).filter(User.id == user_id, User.role == 'teacher').first()
    elif role == "all":
        user_model = db.query(User).filter(User.id == user_id).first()
    else:
        raise ValueError(f"Invalid user type: {role}. Allowed types are 'student','teacher','all'.")
    if user_model is None:
        raise NotFoundException(detail=f'User with id: {user_id} not found', user=user.get('username'))


def validate_related_class(class_id: int, user: dict, db: db_dependency, table_name:str):
    related_users = db.query(User).filter(User.class_id == class_id).all()
    if related_users:
        raise ForeignKeyConstraintException( f'Class with id: {class_id} cannot be deleted because it is associated with table: {table_name}.', user=user.get('username'))


def validate_user_grades(student_id: int, user: dict, db: db_dependency,role: str):
    grades = (
        db.query(Grade)
        .join(User, Grade.student_id == User.id)
        .join(Subject, Grade.subject_id == Subject.id)
        .filter(Grade.student_id == student_id)
        .all()
    )

    if not grades:
        if role in ['admin', 'teacher']:
            raise NotFoundException(detail=f'Grades for user with id: {student_id} not found', user=user.get('username'))
        elif role == 'student':
            raise NotFoundException(detail='Not found', user=user.get('username'))
    return grades


def validate_grades_for_subject(subject_id: int, class_id: int, user: dict, db: db_dependency):
    grade_model = db.query(Grade).join(User, Grade.student_id == User.id).join(Subject,
                                                                               Grade.subject_id == Subject.id).join(
        Class, User.class_id == Class.id).filter(
        Class.id == class_id, Grade.subject_id == subject_id).all()
    if not grade_model:
        raise NotFoundException(detail=f'No grades found for class id: {class_id} and subject id: {subject_id}', user=user.get('username'))
    return grade_model


def validate_average_student_for_subject(subject_id: int, student_id: int, user: dict, db: db_dependency):
    grade_model = db.query(Grade).filter(Grade.student_id == student_id, Grade.subject_id == subject_id).all()
    if not grade_model:
        raise NotFoundException(detail=f'No average found for subject id: {subject_id} and student id: {student_id}.', user=user.get('username'))
    return grade_model


def validate_average_by_class(class_id: int, user: dict, db: db_dependency):
    grades = db.query(Grade).join(User, Grade.student_id == User.id).join(Class, Class.id == User.class_id).filter(
        Class.id == class_id).all()
    if not grades:
        raise NotFoundException(detail=f'No average found for class id: {class_id}.', user=user.get('username'))
    return grades


def validate_grade_edit(subject_id: int, grade_id: int, student_id: int, user: dict, db: db_dependency):
    grade_model = db.query(Grade).filter(Grade.student_id == student_id, Grade.subject_id == subject_id,
                                         Grade.id == grade_id).first()
    if grade_model is None:
        raise NotFoundException(detail=f'Grade with id: {grade_id} not found, for user id: {student_id} on subject id: {subject_id}', user=user.get('username'))
    return grade_model


def validate_grade_delete(subject_id: int, grade_id: int, student_id: int,user: dict, db: db_dependency):
    grade_model = db.query(Grade).filter(Grade.student_id == student_id, Grade.id == grade_id,
                                         Grade.subject_id == subject_id).first()
    if grade_model is None:
        raise NotFoundException(detail='Grade with the specified student_id, subject_id, and grade_id not found', user=user.get('username'))
    return grade_model


def validate_attendance_status(attendance_status: str, user: dict):
    if attendance_status not in ('present', 'absent', 'excused'):
        raise InvalidException(detail=f"Invalid status: {attendance_status}. Allowed status are 'present', 'absent', 'excused'.", user=user.get('username'))


def validate_student_attendance(student_id: int, db: db_dependency, user: dict, role:str):
    attendance_model = db.query(Attendance).join(User, Attendance.student_id == User.id).join(Subject,
                                                                                              Attendance.subject_id == Subject.id).filter(
        Attendance.student_id == student_id).all()
    if not attendance_model:
        if role in ['admin', 'teacher']:
            raise NotFoundException(detail=f'No attendance records found for student with id: {student_id}', user=user.get('username'))
        elif role == 'student':
            raise NotFoundException(detail='Not found', user=user.get('username'))
    return attendance_model


def validate_attendance_for_class_on_date(class_id: int, date: date, user: dict, db: db_dependency):
    attendance_model = db.query(Attendance).join(User, Attendance.student_id == User.id).join(Class,
                                                                                              Class.id == User.class_id).filter(
        Attendance.class_date == date, Class.id == class_id).all()
    if not attendance_model:
        raise NotFoundException(detail=f'No attendance records found for class with id: {class_id} on date: {date}', user=user.get('username'))
    return attendance_model


def validate_attendance_for_student_in_subject(student_id: int, subject_id: int, user: dict, db: db_dependency):
    attendance_model = db.query(Attendance).join(User, User.id == Attendance.student_id).join(Subject,
                                                                                              Subject.id == Attendance.subject_id).filter(
        Attendance.subject_id == subject_id, Attendance.student_id == student_id).all()

    if not attendance_model:
        raise NotFoundException(detail=f'No attendance records found for student with id: {student_id} in subject with id: {subject_id}', user=user.get('username'))
    return attendance_model

def validate_attendance_data(attendance_id: int,student_id: int,subject_id: int,user: dict,db: db_dependency):
    attendance_model = db.query(Attendance).filter(Attendance.id == attendance_id,
                                                   Attendance.student_id == student_id,
                                                   Attendance.subject_id == subject_id).first()
    if attendance_model is None:
        raise NotFoundException(detail=f'No attendance data found for attendance_id: {attendance_id}, subject_id: {subject_id}, student_id: {student_id}', user=user.get('username'))
    return attendance_model

def validate_password_reset(request: UserVerification,student_id: int, db: db_dependency):
    user_model = db.query(User).filter(User.id == student_id).first()
    if not bcrypt_context.verify(request.old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Error on password change')
    return user_model