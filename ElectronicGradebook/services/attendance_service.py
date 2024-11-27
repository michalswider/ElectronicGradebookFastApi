from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from ..routers.auth import get_db
from ..models import Attendance
from ..schemas.attendance import AddAttendanceRequest

db_dependency = Annotated[Session, Depends(get_db)]

def create_attendance(request: AddAttendanceRequest,db: db_dependency, user: dict):
    attendance_model = Attendance(**request.model_dump(), added_by_id=user.get('id'))
    db.add(attendance_model)
    db.commit()