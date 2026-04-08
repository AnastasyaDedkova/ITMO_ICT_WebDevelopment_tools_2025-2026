from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.book import Book
from app.models.genre import Genre
from app.models.book_genre_link import BookGenreLink

router = APIRouter(prefix="/book-genres", tags=["BookGenres"])


@router.get("/")
def get_book_genres(session: Session = Depends(get_session)):
    links = session.exec(select(BookGenreLink)).all()
    return links


@router.post("/")
def add_genre_to_book(
    book_id: int,
    genre_id: int,
    is_primary: bool = False,
    session: Session = Depends(get_session)
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    link = BookGenreLink(book_id=book_id, genre_id=genre_id, is_primary=is_primary)
    session.add(link)
    session.commit()

    return {
        "message": "Genre added to book",
        "book_id": book_id,
        "genre_id": genre_id,
        "is_primary": is_primary
    }