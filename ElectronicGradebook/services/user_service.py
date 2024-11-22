from typing import Annotated
from ElectronicGradebook.models import User
from ElectronicGradebook.routers.auth import bcrypt_context, get_db
from sqlalchemy.orm import Session
from fastapi import Depends

db_dependency = Annotated[Session, Depends(get_db)]


def create_user(request: dict, db: db_dependency):
    user_model = User(
        first_name=request.first_name,
        last_name=request.last_name,
        username=request.username,
        hashed_password=bcrypt_context.hash(request.password),
        date_of_birth=request.date_of_birth,
        class_id=request.class_id,
        subject_id=request.subject_id,
        role=request.role
    )

    db.add(user_model)
    db.commit()
