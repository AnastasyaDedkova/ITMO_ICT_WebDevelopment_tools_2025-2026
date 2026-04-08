from typing import Optional
from sqlmodel import SQLModel
from pydantic import BaseModel

class UserCreate(SQLModel):
    email: str
    username: str
    hashed_password: str


class UserRead(SQLModel):
    id: int
    email: str
    username: str
    hashed_password: str


class UserUpdate(SQLModel):
    email: Optional[str] = None
    username: Optional[str] = None
    hashed_password: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
