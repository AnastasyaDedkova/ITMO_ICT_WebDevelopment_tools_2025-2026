from fastapi import FastAPI
from app.api.books import router as books_router
from app.api.profiles import router as profiles_router
from app.api.genres import router as genres_router

app = FastAPI(title="BookCrossing API")

app.include_router(books_router)
app.include_router(profiles_router)
app.include_router(genres_router)


@app.get("/")
def root():
    return {"message": "BookCrossing API is working"}