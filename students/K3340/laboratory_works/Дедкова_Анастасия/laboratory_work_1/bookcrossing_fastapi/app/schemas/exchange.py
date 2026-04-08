from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class ExchangeCreate(SQLModel):
    request_id: int
    place: str
    exchange_date: datetime
    status: str = "planned"
    comment: Optional[str] = None


class ExchangeRead(SQLModel):
    id: int
    request_id: int
    place: str
    exchange_date: datetime
    status: str
    comment: Optional[str] = None


class ExchangeUpdate(SQLModel):
    place: Optional[str] = None
    exchange_date: Optional[datetime] = None
    status: Optional[str] = None
    comment: Optional[str] = None