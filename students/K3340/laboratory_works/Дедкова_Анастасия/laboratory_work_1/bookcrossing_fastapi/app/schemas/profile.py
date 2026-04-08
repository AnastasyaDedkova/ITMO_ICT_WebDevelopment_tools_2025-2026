from typing import Optional
from sqlmodel import SQLModel


class ProfileCreate(SQLModel):
    user_id: int
    full_name: str
    city: str
    bio: Optional[str] = None


class ProfileRead(SQLModel):
    id: int
    user_id: int
    full_name: str
    city: str
    bio: Optional[str] = None


class ProfileUpdate(SQLModel):
    full_name: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None