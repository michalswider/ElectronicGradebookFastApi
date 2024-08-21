from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from ..models import Subject, Grade, Attendance, User
from ..exception import SubjectNotExistException, SubjectDeleteException
from ..routers.auth import get_db, get_current_user

router = APIRouter(
    prefix="/admin",
    tags=['admin-subjects']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class CreateSubjectRequest(BaseModel):
    name: str = Field(min_length=1)


@router.post("/subjects", status_code=status.HTTP_201_CREATED)
async def create_subject(create_subject_request: CreateSubjectRequest, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    subject_model = Subject(**create_subject_request.dict())
    db.add(subject_model)
    db.commit()


@router.get("/subjects", status_code=status.HTTP_200_OK)
async def show_all_subjects(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    return db.query(Subject).all()


@router.put("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_subject(db: db_dependency, create_subject_request: CreateSubjectRequest, user: user_dependency,
                       subject_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    subject_model = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject_model is None:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))
    subject_model.name = create_subject_request.name
    db.commit()


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(db: db_dependency, user: user_dependency, subject_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed')
    if user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Permission Denied')
    subject_model = db.query(Subject).filter(Subject.id == subject_id).first()
    related_grades = db.query(Grade).filter(Grade.subject_id == subject_id).all()
    related_attendance = db.query(Attendance).filter(Attendance.subject_id == subject_id).all()
    related_users = db.query(User).filter(User.subject_id == subject_id).all()
    if subject_model is None:
        raise SubjectNotExistException(subject_id=subject_id, username=user.get('username'))
    if related_grades:
        raise SubjectDeleteException(subject_id=subject_id, table_name="grades", username=user.get('username'))
    if related_attendance:
        raise SubjectDeleteException(subject_id=subject_id, table_name="attendance", username=user.get('username'))
    if related_users:
        raise SubjectDeleteException(subject_id=subject_id, table_name="users", username=user.get('username'))
    db.query(Subject).filter(Subject.id == subject_id).delete()
    db.commit()
