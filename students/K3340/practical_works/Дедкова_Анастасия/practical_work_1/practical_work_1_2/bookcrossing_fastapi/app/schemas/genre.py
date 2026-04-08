from typing import Optional
from sqlmodel import SQLModel


class GenreCreate(SQLModel):
    name: str
    description: Optional[str] = None


class GenreRead(SQLModel):
    id: int
    name: str
    description: Optional[str] = None


class GenreUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None