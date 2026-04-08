from fastapi import APIRouter, HTTPException
from app.schemas.genre import Genre

router = APIRouter(prefix="/genres", tags=["Genres"])

temp_genres = [
    {"id": 1, "name": "Dystopia"},
    {"id": 2, "name": "Classic"},
    {"id": 3, "name": "Fantasy"}
]


@router.get("/", response_model=list[Genre])
def get_genres():
    return temp_genres


@router.get("/{genre_id}", response_model=Genre)
def get_genre(genre_id: int):
    for genre in temp_genres:
        if genre["id"] == genre_id:
            return genre
    raise HTTPException(status_code=404, detail="Genre not found")


@router.post("/", response_model=Genre)
def create_genre(genre: Genre):
    new_genre = genre.model_dump()
    new_genre["id"] = len(temp_genres) + 1
    temp_genres.append(new_genre)
    return new_genre


@router.delete("/{genre_id}")
def delete_genre(genre_id: int):
    for i, genre in enumerate(temp_genres):
        if genre["id"] == genre_id:
            deleted = temp_genres.pop(i)
            return {"message": "Genre deleted", "genre": deleted}
    raise HTTPException(status_code=404, detail="Genre not found")