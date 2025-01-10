from pydantic import BaseModel, Field


class UserVerification(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)
