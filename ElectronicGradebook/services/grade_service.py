from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from ..models import Grade
from ..routers.auth import get_db
from ..schemas.grades import AddGradeRequest, EditGradeRequest

db_dependency = Annotated[Session, Depends(get_db)]

def create_grade(request: AddGradeRequest, user: dict, db: db_dependency):
    grade_model = Grade(**request.model_dump(), added_by_id=user.get('id'))
    db.add(grade_model)
    db.commit()

def edit_grade(request: EditGradeRequest,grade_model: dict,user: dict ,db: db_dependency):
    grade_model.grade = request.grade
    grade_model.date = request.date
    grade_model.added_by_id = user.get('id')
    db.commit()

def delete_grades(grade_model:dict, db: db_dependency):
    db.delete(grade_model)
    db.commit()