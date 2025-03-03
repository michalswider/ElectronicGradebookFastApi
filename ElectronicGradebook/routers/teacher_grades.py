from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.orm import Session
from starlette import status

from ..response_models.grade import (map_average_grades_by_class_response,
                                     map_grades_to_response,
                                     map_grades_to_students_response)
from ..routers.auth import get_db
from ..schemas.grades import AddGradeRequest, EditGradeRequest
from ..services.grade_service import create_grade, delete_grades, edit_grade
from ..services.validation_service import (
    validate_average_by_class, validate_average_student_for_subject,
    validate_class_exist, validate_grade_delete, validate_grade_edit,
    validate_grades_for_subject, validate_subject_exist, validate_user_grades,
    validate_user_id, verify_teacher_user)

router = APIRouter(prefix="/teacher", tags=["teacher-grades"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/grades/add-grade", status_code=status.HTTP_201_CREATED)
async def add_grade(
    request: Request, db: db_dependency, add_grade_request: AddGradeRequest
):
    user = request.state.user
    verify_teacher_user(user)
    validate_user_id(add_grade_request.student_id, db, user, role="student")
    validate_subject_exist(user, add_grade_request.subject_id, db)
    create_grade(add_grade_request, user, db)
    return {"message": "Grade added successfully"}


@router.get("/grades/{student_id}", status_code=status.HTTP_200_OK)
async def show_student_grades(
    request: Request, db: db_dependency, student_id: int = Path(gt=0)
):
    user = request.state.user
    verify_teacher_user(user)
    validate_user_id(student_id, db, user, role="student")
    grades = validate_user_grades(student_id, user, db, role="teacher")
    return map_grades_to_response(grades)


@router.get(
    "/grades/class/{class_id}/subject/{subject_id}", status_code=status.HTTP_200_OK
)
async def get_students_grades_for_subject(
    request: Request,
    db: db_dependency,
    class_id: int = Path(gt=0),
    subject_id: int = Path(gt=0),
):
    user = request.state.user
    verify_teacher_user(user)
    validate_class_exist(user, class_id, db)
    validate_subject_exist(user, subject_id, db)
    grade_model = validate_grades_for_subject(subject_id, class_id, user, db)
    return map_grades_to_students_response(grade_model)


@router.get("/grades/average/subject/{subject_id}", status_code=status.HTTP_200_OK)
async def show_average_student_for_subject(
    request: Request,
    db: db_dependency,
    subject_id: int = Path(gt=0),
    student_id: int = Query(gt=0),
):
    user = request.state.user
    verify_teacher_user(user)
    validate_subject_exist(user, subject_id, db)
    validate_user_id(student_id, db, user, role="student")
    grade_model = validate_average_student_for_subject(subject_id, student_id, user, db)
    grade_values = [grade.grade for grade in grade_model]
    average = round(sum(grade_values) / len(grade_values), 2)
    return {"average_grade": average}


@router.get("/grades/average/class/{class_id}", status_code=status.HTTP_200_OK)
async def show_average_by_class(
    request: Request, db: db_dependency, class_id: int = Path(gt=0)
):
    user = request.state.user
    verify_teacher_user(user)
    validate_class_exist(user, class_id, db)
    grade_model = validate_average_by_class(class_id, user, db)
    grade_values = [grade.grade for grade in grade_model]
    class_model = grade_model[0].student.klasa.name
    average = round(sum(grade_values) / len(grade_values), 2)
    return map_average_grades_by_class_response(class_model, average)


@router.put("/grades/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_student_grade(
    request: Request,
    db: db_dependency,
    edit_grade_request: EditGradeRequest,
    student_id: int = Path(gt=0),
    subject_id: int = Query(gt=0),
    grade_id: int = Query(gt=0),
):
    user = request.state.user
    verify_teacher_user(user)
    validate_user_id(student_id, db, user, role="student")
    validate_subject_exist(user, subject_id, db)
    grade_model = validate_grade_edit(subject_id, grade_id, student_id, user, db)
    edit_grade(edit_grade_request, grade_model, user, db)


@router.delete(
    "/grades/{student_id}/{subject_id}/{grade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_grade(
    request: Request,
    db: db_dependency,
    student_id: int = Path(gt=0),
    subject_id: int = Path(gt=0),
    grade_id: int = Path(gt=0),
):
    user = request.state.user
    verify_teacher_user(user)
    validate_user_id(student_id, db, user, role="student")
    validate_subject_exist(user, subject_id, db)
    grade_model = validate_grade_delete(subject_id, grade_id, student_id, user, db)
    delete_grades(grade_model, db)
