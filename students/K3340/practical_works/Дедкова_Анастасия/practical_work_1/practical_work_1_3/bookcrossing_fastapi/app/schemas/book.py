from typing import Optional
from sqlmodel import SQLModel


class BookCreate(SQLModel):
    owner_id: int
    title: str
    author: str
    description: Optional[str] = None
    condition: str
    status: str = "available"


class BookRead(SQLModel):
    id: int
    owner_id: int
    title: str
    author: str
    description: Optional[str] = None
    condition: str
    status: str


class BookUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[str] = None
    status: Optional[str] = None