from typing import Annotated
from ..exception import UserIdNotFoundException, SubjectNotExistException, GradesNotFoundException, \
    GradeEditNotExistException, GradeForSubjectNotExistException, AverageByClassNotFoundException, AverageBySubjectForStudentNotFoundException, ClassNotExistException
from fastapi import Path, HTTPException
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from ..models import Grade, Subject, User, Class
from ..routers.auth import get_db
from datetime import date
from ..routers.auth import get_current_user

router = APIRouter(
    prefix="/teacher",
    tags=['teacher-grades']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class AddGradeRequest(BaseModel):
    student_id: int = Field(gt=0)
    subject_id: int = Field(gt=0)
    grade: int = Field(gt=0, lt=7)
    date: date


class EditGradeRequest(BaseModel):
    grade: int = Field(gt=0, lt=7)
    date: date


@router.post("/grades/add-grade", status_code=status.HTTP_201_CREATED)
async def add_grade(db: db_dependency, user: user_dependency, add_grade_request: AddGradeRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    student = db.query(User).filter(User.id == add_grade_request.student_id, User.role == 'student').first()
    subject = db.query(Subject).filter(Subject.id == add_grade_request.subject_id).first()
    if not student:
        raise UserIdNotFoundException(user_id=add_grade_request.student_id, username=user.get('username'))
    if not subject:
        raise SubjectNotExistException(subject_id=add_grade_request.subject_id, username=user.get('username'))
    grade_model = Grade(**add_grade_request.dict(), added_by_id=user.get('id'))
    db.add(grade_model)
    db.commit()
    return {"message": "Grade added successfully"}


@router.get("/grades/{student_id}", status_code=status.HTTP_200_OK)
async def show_student_grades(db: db_dependency, user: user_dependency, student_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    grades = (
        db.query(Grade)
        .join(User, Grade.student_id == User.id)
        .join(Subject, Grade.subject_id == Subject.id)
        .filter(Grade.student_id == student_id)
        .all()
    )
    student_model = db.query(User).filter(User.id == student_id, User.role == 'student').first()
    if student_model is None:
        raise UserIdNotFoundException(user_id=student_id, username=user.get('username'))
    if not grades:
        raise GradesNotFoundException(student_id=student_id, username=user.get('username'))
    result = {}
    for grade in grades:
        subject_name = grade.subject.name
        if subject_name not in result:
            result[subject_name] = []
        result[subject_name].append({
            'id': grade.id,
            'grade': grade.grade,
            'date': grade.date,
            'added_by': grade.teacher.first_name + " " + grade.teacher.last_name
        })
    return result


@router.get("/grades/class/{class_id}/subject/{subject_id}", status_code=status.HTTP_200_OK)
async def get_students_grades_for_subject(db: db_dependency, user: user_dependency, class_id: int = Path(gt=0),
                                          subject_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    grade_model = db.query(Grade).join(User, Grade.student_id == User.id).join(Subject,
                                                                               Grade.subject_id == Subject.id).join(
        Class, User.class_id == Class.id).filter(
        Class.id == class_id, Grade.subject_id == subject_id).all()
    class_model = db.query(Class).filter(Class.id == class_id).first()
    subject_model = db.query(Subject).filter(Subject.id == subject_id).first()
    if class_model is None:
        raise ClassNotExistException(class_id=class_id, username=user.get('username'))
    if subject_model is None:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))
    if not grade_model:
        raise GradeForSubjectNotExistException(class_id=class_id,subject_id=subject_id, username=user.get('username'))
    result = {}

    for grade in grade_model:
        student = grade.student.first_name + " " + grade.student.last_name
        if student not in result:
            result[student] = []

        result[student].append({
            'id': grade.id,
            'grade': grade.grade,
            'date': grade.date,
            'added_by': grade.teacher.first_name + " " + grade.teacher.last_name
        })
    return result


@router.get("/grades/average/subject/{subject_id}", status_code=status.HTTP_200_OK)
async def show_average_student_for_subject(db: db_dependency, user: user_dependency, subject_id: int = Path(gt=0),
                                           student_id: int = Query(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    grade_model = db.query(Grade).filter(Grade.student_id == student_id, Grade.subject_id == subject_id).all()
    subject_model = db.query(Subject).filter(Subject.id == subject_id).first()
    student_model = db.query(User).filter(User.id == student_id, User.role == 'student').first()
    if subject_model is None:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))
    if student_model is None:
        raise UserIdNotFoundException(user_id=student_id, username=user.get('username'))
    if not grade_model:
        raise AverageBySubjectForStudentNotFoundException(subject_id=subject_id,student_id=student_id, username=user.get('username'))
    values = []
    for grade in grade_model:
        values.append(grade.grade)
    average_grade = sum(values) / len(values)
    average_grade_rounded = round(average_grade, 2)
    return {'average_grade': average_grade_rounded}


@router.get("/grades/average/class/{class_id}", status_code=status.HTTP_200_OK)
async def show_average_by_class(db: db_dependency, user: user_dependency, class_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    grades = db.query(Grade).join(User, Grade.student_id == User.id).join(Class, Class.id == User.class_id).filter(
        Class.id == class_id).all()
    class_model = db.query(Class).filter(Class.id == class_id).first()
    if class_model is None:
        raise ClassNotExistException(class_id=class_id, username=user.get('username'))
    if not grades:
        raise AverageByClassNotFoundException(class_id=class_id, username=user.get('username'))
    values_of_grades = []
    for grade in grades:
        values_of_grades.append(grade.grade)

    average_of_grades = sum(values_of_grades) / len(values_of_grades)
    rounded_average_of_grades = round(average_of_grades, 2)
    return {
        'class': grade.student.klasa.name,
        'average_grade': rounded_average_of_grades
    }


@router.put("/grades/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_student_grade(db: db_dependency, user: user_dependency, edit_grade_request: EditGradeRequest,
                             student_id: int = Path(gt=0),
                             subject_id: int = Query(gt=0), grade_id: int = Query(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    grade_model = db.query(Grade).filter(Grade.student_id == student_id, Grade.subject_id == subject_id,
                                         Grade.id == grade_id).first()
    student_model = db.query(User).filter(User.id == student_id, User.role == 'student').first()
    subject_model = db.query(Subject).filter(Subject.id == subject_id).first()
    if student_model is None:
        raise UserIdNotFoundException(user_id=student_id, username=user.get('username'))
    if subject_model is None:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))
    if grade_model is None:
        raise GradeEditNotExistException(student_id=student_id,grade_id=grade_id,subject_id=subject_id, username=user.get('username'))
    grade_model.grade = edit_grade_request.grade
    grade_model.date = edit_grade_request.date
    grade_model.added_by_id = user.get('id')
    db.commit()
    return {"message": "Grade edited successfully"}


@router.delete("/grades/{student_id}/{subject_id}/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grade(db: db_dependency, user: user_dependency, student_id: int = Path(gt=0),
                       subject_id: int = Path(gt=0),
                       grade_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') not in ('admin', 'teacher'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    grade_model = db.query(Grade).filter(Grade.student_id == student_id, Grade.id == grade_id,
                                         Grade.subject_id == subject_id).first()
    subject_model = db.query(Subject).filter(Subject.id == subject_id).first()
    student_model = db.query(User).filter(User.id == student_id).first()
    if student_model is None:
        raise UserIdNotFoundException(user_id=student_id, username=user.get('username'))
    if subject_model is None:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))
    if grade_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Grade with the specified student_id, subject_id, and grade_id not found')
    db.delete(grade_model)
    db.commit()
