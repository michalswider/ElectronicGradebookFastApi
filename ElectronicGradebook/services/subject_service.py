from typing import Annotated
from ..schemas.subjects import CreateSubjectRequest
from ..models import Subject
from sqlalchemy.orm import Session
from fastapi import Depends
from ..routers.auth import get_db

db_dependency = Annotated[Session, Depends(get_db)]

def add_subject(request: CreateSubjectRequest, db: db_dependency):
    subject_model = Subject(**request.dict())
    db.add(subject_model)
    db.commit()