from typing import Annotated
from .validation_service import validate_database_subjects_relation
from ..schemas.subjects import CreateSubjectRequest
from ..models import Subject, Grade, Attendance, User
from sqlalchemy.orm import Session
from fastapi import Depends
from ..routers.auth import get_db

db_dependency = Annotated[Session, Depends(get_db)]

def add_subject(request: CreateSubjectRequest, db: db_dependency):
    subject_model = Subject(**request.model_dump())
    db.add(subject_model)
    db.commit()

def edit_subjects(request: CreateSubjectRequest, subject_id: int, db: db_dependency):
    subject_model = db.query(Subject).filter(Subject.id == subject_id).first()
    subject_model.name = request.name
    db.commit()

def delete_subjects(subject_id: int, db: db_dependency, user : dict):
    related_records = {
        "grades": db.query(Grade).filter(Grade.subject_id == subject_id).all(),
        "attendance": db.query(Attendance).filter(Attendance.subject_id == subject_id).all(),
        "users": db.query(User).filter(User.subject_id == subject_id).all()
    }
    validate_database_subjects_relation(related_records, subject_id, user)
    db.query(Subject).filter(Subject.id == subject_id).delete()
    db.commit()