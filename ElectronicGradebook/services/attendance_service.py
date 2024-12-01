from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from ..routers.auth import get_db
from ..models import Attendance
from ..schemas.attendance import AddAttendanceRequest, EditAttendanceStatusRequest

db_dependency = Annotated[Session, Depends(get_db)]

def create_attendance(request: AddAttendanceRequest,db: db_dependency, user: dict):
    attendance_model = Attendance(**request.model_dump(), added_by_id=user.get('id'))
    db.add(attendance_model)
    db.commit()

def edit_attendance(attendance_model: dict,request: EditAttendanceStatusRequest, db: db_dependency):
    attendance_model.status = request.status
    db.add(attendance_model)
    db.commit()

def delete_attendances(attendance_model:dict,db: db_dependency):
    db.delete(attendance_model)
    db.commit()