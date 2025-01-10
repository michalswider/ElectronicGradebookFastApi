from pydantic import BaseModel, Field


class CreateClassRequest(BaseModel):
    name: str = Field(min_length=1)
