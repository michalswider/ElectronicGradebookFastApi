from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from ..routers.auth import get_db
from fastapi import HTTPException
from starlette import status
from ..models import User, Class, Subject, Grade
from ..exception import UsernameAlreadyExistException, ClassNotExistException, SubjectNotExistException, \
    InvalidRoleException, UsernameNotFoundException, UserDeleteException, UserIdNotFoundException, ClassDeleteException, \
    SubjectDeleteException, GradesNotFoundException, GradeForSubjectNotExistException, \
    AverageBySubjectForStudentNotFoundException, AverageByClassNotFoundException, GradeEditNotExistException, \
    InvalidStatusException

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


def validate_username_exist(user: dict, username: str, db: db_dependency):
    username_model = db.query(User).filter(User.username == username).first()
    if username_model is not None:
        raise UsernameAlreadyExistException(username=username, user=user.get('username'))


def validate_class_exist(user: dict, class_id: int, db: db_dependency):
    classes = db.query(Class).filter(Class.id == class_id).first()
    if not classes:
        raise ClassNotExistException(class_id=class_id, username=user.get('username'))


def validate_subject_exist(user: dict, subject_id: int, db: db_dependency):
    subjects = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subjects:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))


def validate_roles(role: str, user: dict):
    valid_roles = ['admin', 'teacher', 'student']
    if role not in valid_roles:
        raise InvalidRoleException(role=role, username=user.get('username'))


def validate_username_found(user_model: User, user: dict, username: str):
    if user_model is None:
        raise UsernameNotFoundException(username=username, user=user.get('username'))


def validate_database_relation(related_records: dict, user_id: int, user: dict):
    for table_name, record in related_records.items():
        if record:
            raise UserDeleteException(user_id=user_id, table_name=table_name, username=user.get('username'))


def validate_database_subjects_relation(related_records: dict, subject_id: int, user: dict):
    for table_name, record in related_records.items():
        if record:
            raise SubjectDeleteException(subject_id=subject_id, table_name=table_name, username=user.get('username'))


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
        raise UserIdNotFoundException(user_id=user_id, username=user.get('username'))


def validate_related_class(class_id: int, user: dict, db: db_dependency):
    related_users = db.query(User).filter(User.class_id == class_id).all()
    if related_users:
        raise ClassDeleteException(class_id=class_id, table_name="users", username=user.get('username'))


def validate_user_grades(student_id: int, user: dict, db: db_dependency):
    grades = (
        db.query(Grade)
        .join(User, Grade.student_id == User.id)
        .join(Subject, Grade.subject_id == Subject.id)
        .filter(Grade.student_id == student_id)
        .all()
    )
    if not grades:
        raise GradesNotFoundException(student_id=student_id, username=user.get('username'))
    return grades


def validate_grades_for_subject(subject_id: int, class_id: int, user: dict, db: db_dependency):
    grade_model = db.query(Grade).join(User, Grade.student_id == User.id).join(Subject,
                                                                               Grade.subject_id == Subject.id).join(
        Class, User.class_id == Class.id).filter(
        Class.id == class_id, Grade.subject_id == subject_id).all()
    if not grade_model:
        raise GradeForSubjectNotExistException(class_id=class_id, subject_id=subject_id, username=user.get('username'))
    return grade_model


def validate_average_student_for_subject(subject_id: int, student_id: int, user: dict, db: db_dependency):
    grade_model = db.query(Grade).filter(Grade.student_id == student_id, Grade.subject_id == subject_id).all()
    if not grade_model:
        raise AverageBySubjectForStudentNotFoundException(subject_id=subject_id, student_id=student_id,
                                                          username=user.get('username'))
    return grade_model


def validate_average_by_class(class_id: int, user: dict, db: db_dependency):
    grades = db.query(Grade).join(User, Grade.student_id == User.id).join(Class, Class.id == User.class_id).filter(
        Class.id == class_id).all()
    if not grades:
        raise AverageByClassNotFoundException(class_id=class_id, username=user.get('username'))
    return grades


def validate_grade_edit(subject_id: int, grade_id: int, student_id: int, user: dict, db: db_dependency):
    grade_model = db.query(Grade).filter(Grade.student_id == student_id, Grade.subject_id == subject_id,
                                         Grade.id == grade_id).first()
    if grade_model is None:
        raise GradeEditNotExistException(student_id=student_id, grade_id=grade_id, subject_id=subject_id,
                                         username=user.get('username'))
    return grade_model


def validate_grade_delete(subject_id: int, grade_id: int, student_id: int, db: db_dependency):
    grade_model = db.query(Grade).filter(Grade.student_id == student_id, Grade.id == grade_id,
                                         Grade.subject_id == subject_id).first()
    if grade_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Grade with the specified student_id, subject_id, and grade_id not found')
    return grade_model


def validate_attendance_status(attendance_status: str, user: dict):
    if attendance_status not in ('present', 'absent', 'excused'):
        raise InvalidStatusException(status=attendance_status, username=user.get('username'))
