from typing import Optional
from sqlmodel import SQLModel, Field


class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    full_name: str
    city: str
    bio: Optional[str] = None