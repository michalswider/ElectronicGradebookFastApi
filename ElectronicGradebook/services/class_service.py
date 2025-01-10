from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ..models import Class
from ..routers.auth import get_db
from ..schemas.classes import CreateClassRequest
from .validation_service import validate_related_class

db_dependency = Annotated[Session, Depends(get_db)]


def add_class(request: CreateClassRequest, db):
    class_model = Class(**request.model_dump())
    db.add(class_model)
    db.commit()


def edit_classes(request: CreateClassRequest, class_model: Class, db: db_dependency):
    class_model.name = request.name
    db.commit()


def delete_classes(class_id: int, user: dict, db: db_dependency):
    validate_related_class(class_id, user, db, table_name="users")
    db.query(Class).filter(Class.id == class_id).delete()
    db.commit()
