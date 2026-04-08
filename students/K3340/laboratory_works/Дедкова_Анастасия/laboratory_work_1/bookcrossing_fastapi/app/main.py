from fastapi import FastAPI

from app.api.users import router as users_router
from app.api.books import router as books_router
from app.api.genres import router as genres_router
from app.api.profiles import router as profiles_router
from app.api.book_genres import router as book_genres_router
from app.api.exchange_requests import router as exchange_requests_router
from app.api.exchanges import router as exchanges_router
from app.api.auth import router as auth_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI(title="BookCrossing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


app.include_router(users_router)
app.include_router(books_router)
app.include_router(genres_router)
app.include_router(profiles_router)
app.include_router(book_genres_router)
app.include_router(exchange_requests_router)
app.include_router(exchanges_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return RedirectResponse(url="/frontend/pages/login.html")
