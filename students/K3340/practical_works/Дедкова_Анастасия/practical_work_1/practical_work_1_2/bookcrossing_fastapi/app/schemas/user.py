from typing import Optional
from sqlmodel import SQLModel


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