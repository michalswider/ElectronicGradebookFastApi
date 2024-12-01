from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from ..routers.auth import get_db, bcrypt_context
from ..schemas.students import UserVerification

db_dependency = Annotated[Session, Depends(get_db)]

def edit_password(request: UserVerification,student: dict, db: db_dependency):
    student.hashed_password = bcrypt_context.hash(request.new_password)
    db.add(student)
    db.commit()