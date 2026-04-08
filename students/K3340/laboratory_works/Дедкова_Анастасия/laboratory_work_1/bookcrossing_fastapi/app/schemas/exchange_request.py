from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class ExchangeRequestCreate(SQLModel):
    book_id: int
    requester_id: int
    owner_id: int
    message: Optional[str] = None
    status: str = "pending"


class ExchangeRequestRead(SQLModel):
    id: int
    book_id: int
    requester_id: int
    owner_id: int
    message: Optional[str] = None
    status: str
    created_at: datetime


class ExchangeRequestUpdate(SQLModel):
    message: Optional[str] = None
    status: Optional[str] = None