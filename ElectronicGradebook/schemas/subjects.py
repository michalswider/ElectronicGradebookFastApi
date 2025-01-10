from pydantic import BaseModel, Field


class CreateSubjectRequest(BaseModel):
    name: str = Field(min_length=1)
