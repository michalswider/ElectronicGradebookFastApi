from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from ..routers.auth import get_db
from fastapi import HTTPException
from starlette import status

db_dependency = Annotated[Session,Depends(get_db)]

def verify_admin_user(user: dict):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')