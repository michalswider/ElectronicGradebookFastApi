from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from ..routers.auth import get_db
from fastapi import HTTPException
from starlette import status
from ..models import User,Class,Subject
from ..exception import UsernameAlreadyExistException,ClassNotExistException,SubjectNotExistException, InvalidRoleException, UsernameNotFoundException

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

def validate_subject_exist(user: dict, subject_id: int, db: db_dependency):
    subjects = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subjects:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))

def validate_roles(role: str, user: dict):
    valid_roles = ['admin','teacher','student']
    if role not in valid_roles:
        raise InvalidRoleException(role=role, username=user.get('username'))

def validate_username_found(user:dict,username:str,db: db_dependency):
    user_model = db.query(User).filter(User.username == username, User.role.in_(['student', 'teacher'])).first()
    if user_model is None:
        raise UsernameNotFoundException(username=username, user=user.get('username'))
    return user_model
