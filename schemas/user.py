import uuid
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: uuid.UUID   
    email: EmailStr
    is_active: bool = True

    class Config:
        from_attributes = True  # for Pydantic v2
