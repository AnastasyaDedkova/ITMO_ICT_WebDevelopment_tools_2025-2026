from fastapi import APIRouter, HTTPException
from app.schemas.book import Book, BookCreate

router = APIRouter(prefix="/books", tags=["Books"])

temp_books = [
    {
        "id": 1,
        "title": "1984",
        "author": "George Orwell",
        "condition": "good",
        "owner": {
            "id": 1,
            "username": "andrey",
            "city": "Moscow"
        },
        "genres": [
            {"id": 1, "name": "Dystopia"},
            {"id": 2, "name": "Classic"}
        ]
    }
]


@router.get("/", response_model=list[Book])
def get_books():
    return temp_books


@router.get("/{book_id}", response_model=Book)
def get_book(book_id: int):
    for book in temp_books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@router.post("/", response_model=Book)
def create_book(book: BookCreate):
    new_book = book.model_dump()
    new_book["id"] = len(temp_books) + 1
    temp_books.append(new_book)
    return new_book


@router.delete("/{book_id}")
def delete_book(book_id: int):
    for i, book in enumerate(temp_books):
        if book["id"] == book_id:
            deleted = temp_books.pop(i)
            return {"message": "Book deleted", "book": deleted}
    raise HTTPException(status_code=404, detail="Book not found")