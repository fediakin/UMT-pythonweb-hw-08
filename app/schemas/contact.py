from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class ContactBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    birthday: date
    additional_data: Optional[str] = None

    @field_validator("birthday")
    @classmethod
    def validate_age(cls, v):
        if v >= date.today():
            raise ValueError("Birthday must be in the past")
        return v

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: int

    model_config = {"from_attributes": True}