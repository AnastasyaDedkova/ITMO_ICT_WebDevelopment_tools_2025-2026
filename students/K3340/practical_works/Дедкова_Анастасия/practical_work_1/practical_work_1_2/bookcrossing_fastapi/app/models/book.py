from typing import Optional
from sqlmodel import SQLModel, Field


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    title: str
    author: str
    description: Optional[str] = None
    condition: str
    status: str = "available"