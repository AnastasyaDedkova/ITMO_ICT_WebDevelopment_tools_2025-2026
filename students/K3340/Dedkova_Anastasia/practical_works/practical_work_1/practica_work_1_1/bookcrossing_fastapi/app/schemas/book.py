from typing import List

from pydantic import BaseModel

from .profile import Profile
from .genre import Genre


class BookBase(BaseModel):
    title: str
    author: str
    condition: str


class BookCreate(BookBase):
    owner: Profile
    genres: List[Genre]


class Book(BookBase):
    id: int
    owner: Profile
    genres: List[Genre]