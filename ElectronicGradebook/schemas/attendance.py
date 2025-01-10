from datetime import date

from pydantic import BaseModel, Field


class AddAttendanceRequest(BaseModel):
    student_id: int = Field(gt=0)
    subject_id: int = Field(gt=0)
    class_date: date
    status: str


class EditAttendanceStatusRequest(BaseModel):
    status: str
