from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from ..routers.auth import get_db
from fastapi import HTTPException
from starlette import status
from ..models import User,Class
from ..exception import UsernameAlreadyExistException,ClassNotExistException

db_dependency = Annotated[Session,Depends(get_db)]

def verify_admin_user(user: dict):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')

def validate_username_exist(user: dict, username: str,db: db_dependency):
    username_model = db.query(User).filter(User.username == username).first()
    if username_model is not None:
        raise UsernameAlreadyExistException(username=username, user=user.get('username'))

def validate_class_exist(user: dict,class_id:int,db: db_dependency):
    classes = db.query(Class).filter(Class.id == class_id).first()
    if not classes:
        raise ClassNotExistException(class_id=class_id, username=user.get('username'))