from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    picture: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None
    provider: str = "local"

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
