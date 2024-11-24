from pydantic import BaseModel, Field
from datetime import date

class AddGradeRequest(BaseModel):
    student_id: int = Field(gt=0)
    subject_id: int = Field(gt=0)
    grade: int = Field(gt=0, lt=7)
    date: date


class EditGradeRequest(BaseModel):
    grade: int = Field(gt=0, lt=7)
    date: date