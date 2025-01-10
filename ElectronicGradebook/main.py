from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from .database import engine
from .handlers import setup_exception_handlers
from .middleware.authentication_middleware import JWTMiddleware
from .models import Base, User
from .routers import (admin_classes, admin_subjects, admin_users, auth,
                      student_panel, teacher_attendance, teacher_grades)
from .routers.auth import ALGORITHM, SECRET_KEY, bcrypt_context, get_db

Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]


def create_admin_user(db: db_dependency):
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_model = User(
            first_name="admin",
            last_name="admin",
            username="admin",
            hashed_password=bcrypt_context.hash("admin"),
            role="admin",
        )
        db.add(admin_model)
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    try:
        create_admin_user(db)
        yield
    finally:
        db.close()


app = FastAPI(lifespan=lifespan)

setup_exception_handlers(app)
app.add_middleware(JWTMiddleware, secret_key=SECRET_KEY, algorithm=ALGORITHM)
app.include_router(admin_users.router)
app.include_router(admin_subjects.router)
app.include_router(admin_classes.router)
app.include_router(teacher_grades.router)
app.include_router(teacher_attendance.router)
app.include_router(student_panel.router)
app.include_router(auth.router)
