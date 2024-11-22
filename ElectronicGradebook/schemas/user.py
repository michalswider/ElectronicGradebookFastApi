from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class CreateUserRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    username: str = Field(min_length=1)
    password: str = Field(min_length=6)
    date_of_birth: Optional[date] = None
    class_id: Optional[int] = None
    subject_id: Optional[int] = None
    role: str = Field(min_length=4)

class EditUserRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    username: Optional[str] = Field(None,min_length=1)
    password: Optional[str] = Field(None, min_length=6)
    date_of_birth: Optional[date] = None
    class_id: Optional[int] = None
    subject_id: Optional[int] = None
    role: Optional[str] = None