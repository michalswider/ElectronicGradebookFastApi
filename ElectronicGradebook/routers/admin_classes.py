from typing import Annotated
from ..models import Class, User
from fastapi import APIRouter, Depends, Path, HTTPException
from ..schemas.classes import CreateClassRequest
from sqlalchemy.orm import Session
from starlette import status
from ..routers.auth import get_current_user, get_db
from ..exception import ClassNotExistException, ClassDeleteException
from ..services.class_service import add_class, edit_classes, delete_classes
from ..services.validation_service import verify_admin_user, validate_class_exist, validate_related_class

router = APIRouter(
    prefix="/admin",
    tags=['admin-classes']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/classes", status_code=status.HTTP_201_CREATED)
async def create_class(db: db_dependency, user: user_dependency, create_class_request: CreateClassRequest):
    verify_admin_user(user)
    add_class(create_class_request, db)

@router.get("/classes", status_code=status.HTTP_200_OK)
async def show_all_classes(db: db_dependency, user: user_dependency):
    verify_admin_user(user)
    return db.query(Class).all()


@router.put("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_class(db: db_dependency, user: user_dependency, create_class_request: CreateClassRequest,
                     class_id: int = Path(gt=0)):
    verify_admin_user(user)
    validate_class_exist(user, class_id, db)
    edit_classes(create_class_request, class_id, db)


@router.delete("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(db: db_dependency, user: user_dependency, class_id: int = Path(gt=0)):
    verify_admin_user(user)
    validate_class_exist(user, class_id, db)
    delete_classes(class_id,user, db)
