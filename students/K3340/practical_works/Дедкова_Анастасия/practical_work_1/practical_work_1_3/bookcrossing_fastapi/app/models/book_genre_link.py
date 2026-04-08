from typing import Optional
from sqlmodel import SQLModel, Field


class BookGenreLink(SQLModel, table=True):
    book_id: Optional[int] = Field(default=None, foreign_key="book.id", primary_key=True)
    genre_id: Optional[int] = Field(default=None, foreign_key="genre.id", primary_key=True)
    is_primary: bool = False