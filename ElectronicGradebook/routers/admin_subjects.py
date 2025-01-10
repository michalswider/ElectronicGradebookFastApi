from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request
from sqlalchemy.orm import Session
from starlette import status

from ..models import Subject
from ..routers.auth import get_db
from ..schemas.subjects import CreateSubjectRequest
from ..services.subject_service import (add_subject, delete_subjects,
                                        edit_subjects)
from ..services.validation_service import (validate_subject_exist,
                                           verify_admin_user)

router = APIRouter(prefix="/admin", tags=["admin-subjects"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/subjects", status_code=status.HTTP_201_CREATED)
async def create_subject(
    request: Request, create_subject_request: CreateSubjectRequest, db: db_dependency
):
    user = request.state.user
    verify_admin_user(user)
    add_subject(create_subject_request, db)


@router.get("/subjects", status_code=status.HTTP_200_OK)
async def show_all_subjects(request: Request, db: db_dependency):
    user = request.state.user
    verify_admin_user(user)
    return db.query(Subject).all()


@router.put("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_subject(
    request: Request,
    db: db_dependency,
    create_subject_request: CreateSubjectRequest,
    subject_id: int = Path(gt=0),
):
    user = request.state.user
    verify_admin_user(user)
    subject_model = validate_subject_exist(user, subject_id, db)
    edit_subjects(create_subject_request, subject_model, db)


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    request: Request, db: db_dependency, subject_id: int = Path(gt=0)
):
    user = request.state.user
    verify_admin_user(user)
    validate_subject_exist(user, subject_id, db)
    delete_subjects(subject_id, db, user)
