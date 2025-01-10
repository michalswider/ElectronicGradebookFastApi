from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ..models import User
from ..routers.auth import bcrypt_context, get_db
from ..schemas.students import UserVerification

db_dependency = Annotated[Session, Depends(get_db)]


def edit_password(request: UserVerification, student: User, db: db_dependency):
    student.hashed_password = bcrypt_context.hash(request.new_password)
    db.add(student)
    db.commit()
