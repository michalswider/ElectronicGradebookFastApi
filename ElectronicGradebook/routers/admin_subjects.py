from typing import Annotated
from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from starlette import status
from ..models import Subject
from ..routers.auth import get_db, get_current_user
from ..schemas.subjects import CreateSubjectRequest
from ..services.subject_service import add_subject, edit_subjects, delete_subjects
from ..services.validation_service import verify_admin_user, validate_subject_exist

router = APIRouter(
    prefix="/admin",
    tags=['admin-subjects']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/subjects", status_code=status.HTTP_201_CREATED)
async def create_subject(create_subject_request: CreateSubjectRequest, user: user_dependency, db: db_dependency):
    verify_admin_user(user)
    add_subject(create_subject_request, db)


@router.get("/subjects", status_code=status.HTTP_200_OK)
async def show_all_subjects(db: db_dependency, user: user_dependency):
    verify_admin_user(user)
    return db.query(Subject).all()


@router.put("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_subject(db: db_dependency, create_subject_request: CreateSubjectRequest, user: user_dependency,
                       subject_id: int = Path(gt=0)):
    verify_admin_user(user)
    validate_subject_exist(user, subject_id, db)
    edit_subjects(create_subject_request, subject_id, db)


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(db: db_dependency, user: user_dependency, subject_id: int = Path(gt=0)):
    verify_admin_user(user)
    validate_subject_exist(user, subject_id, db)
    delete_subjects(subject_id, db, user)
