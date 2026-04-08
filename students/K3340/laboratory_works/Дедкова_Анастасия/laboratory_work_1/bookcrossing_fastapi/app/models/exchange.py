from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Exchange(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="exchangerequest.id")
    place: str
    exchange_date: datetime
    status: str = "planned"
    comment: Optional[str] = None