from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class ExchangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    requester_id: int = Field(foreign_key="user.id")
    owner_id: int = Field(foreign_key="user.id")
    message: Optional[str] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)