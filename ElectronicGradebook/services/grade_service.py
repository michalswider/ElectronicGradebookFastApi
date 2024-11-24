from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from ..models import Grade
from ..routers.auth import get_db
from ..schemas.grades import AddGradeRequest
from ..services.validation_service import validate_user_id, validate_subject_exist

db_dependency = Annotated[Session, Depends(get_db)]

def create_grade(request: AddGradeRequest, user: dict, db: db_dependency):
    validate_user_id(request.student_id,db,user)
    validate_subject_exist(user,request.subject_id,db)
    grade_model = Grade(**request.dict(), added_by_id=user.get('id'))
    db.add(grade_model)
    db.commit()