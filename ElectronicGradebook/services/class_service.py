from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from ..models import Class
from ..routers.auth import get_db
from ..schemas.classes import CreateClassRequest

db_dependency = Annotated[Session, Depends(get_db)]

def add_class(request: CreateClassRequest, db):
    class_model = Class(**request.dict())
    db.add(class_model)
    db.commit()

def edit_classes(request: CreateClassRequest, class_id: int, db: db_dependency):
    class_model = db.query(Class).filter(Class.id == class_id).first()
    class_model.name = request.name
    db.commit()