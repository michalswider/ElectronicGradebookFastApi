from fastapi import FastAPI, Request
import logging
from starlette import status
from starlette.responses import JSONResponse
from .models import Base
from .database import engine
from .exception import InvalidException, ApplicationException
from .logging_config import setup_logging
from .routers import admin_users, admin_subjects, admin_classes, teacher_grades, teacher_attendance, auth, student_panel

setup_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(admin_users.router)
app.include_router(admin_subjects.router)
app.include_router(admin_classes.router)
app.include_router(teacher_grades.router)
app.include_router(teacher_attendance.router)
app.include_router(student_panel.router)
app.include_router(auth.router)


@app.get("/healthy", status_code=status.HTTP_200_OK)
async def check_status():
    return {'details': 'Healthy'}


@app.exception_handler(ApplicationException)
async def application_exception_handler(request: Request, exc: ApplicationException):
    logger = logging.getLogger(__name__)
    logger.error(f'Error: {exc.detail} ~ User: {exc.user} ~ Path: {request.url.path}')
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'detail': exc.detail})


@app.exception_handler(InvalidException)
async def invalid_exception_handler(request: Request, exc: InvalidException):
    logger = logging.getLogger(__name__)
    logger.error(f'Error: {exc.detail} ~ User: {exc.user} ~ Path: {request.url.path}')
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                        content={'detail': exc.detail})
