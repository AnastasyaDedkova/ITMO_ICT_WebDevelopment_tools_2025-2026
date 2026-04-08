from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db.session import engine
from app.api.users import router as users_router
from app.api.books import router as books_router
from app.api.genres import router as genres_router
from app.api.profiles import router as profiles_router
from app.api.book_genres import router as book_genres_router

from app.models.user import User
from app.models.profile import Profile
from app.models.book import Book
from app.models.genre import Genre
from app.models.book_genre_link import BookGenreLink

app = FastAPI(title="BookCrossing API")


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


app.include_router(users_router)
app.include_router(books_router)
app.include_router(genres_router)
app.include_router(profiles_router)
app.include_router(book_genres_router)


@app.get("/")
def root():
    return {"message": "BookCrossing API is working"}