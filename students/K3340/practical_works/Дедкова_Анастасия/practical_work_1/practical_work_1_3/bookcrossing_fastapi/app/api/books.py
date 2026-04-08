from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.book import Book
from app.models.genre import Genre
from app.models.book_genre_link import BookGenreLink
from app.schemas.book import BookCreate, BookRead, BookUpdate

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[BookRead])
def get_books(session: Session = Depends(get_session)):
    books = session.exec(select(Book)).all()
    return books


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookRead)
def create_book(book_data: BookCreate, session: Session = Depends(get_session)):
    book = Book(**book_data.model_dump())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.get("/{book_id}/genres")
def get_book_genres(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    links = session.exec(
        select(BookGenreLink).where(BookGenreLink.book_id == book_id)
    ).all()

    result = []
    for link in links:
        genre = session.get(Genre, link.genre_id)
        if genre:
            result.append({
                "id": genre.id,
                "name": genre.name,
                "description": genre.description,
                "is_primary": link.is_primary
            })

    return {
        "book_id": book.id,
        "title": book.title,
        "genres": result
    }

@router.patch("/{book_id}", response_model=BookRead)
def update_book(book_id: int, book_data: BookUpdate, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(book, key, value)

    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.delete("/{book_id}")
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(book)
    session.commit()
    return {"message": "Book deleted"}