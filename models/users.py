from typing import Optional
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    username: str
    email: str


class UserCreate(BaseModel):
    id: Optional[int]
    username: str
    email: EmailStr
    password_hash: str


class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str
    password2: str