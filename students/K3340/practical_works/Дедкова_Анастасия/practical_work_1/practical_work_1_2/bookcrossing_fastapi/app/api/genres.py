from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.genre import Genre
from app.schemas.genre import GenreCreate, GenreRead, GenreUpdate

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("/", response_model=list[GenreRead])
def get_genres(session: Session = Depends(get_session)):
    genres = session.exec(select(Genre)).all()
    return genres


@router.get("/{genre_id}", response_model=GenreRead)
def get_genre(genre_id: int, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@router.post("/", response_model=GenreRead)
def create_genre(genre_data: GenreCreate, session: Session = Depends(get_session)):
    genre = Genre(**genre_data.model_dump())
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre


@router.patch("/{genre_id}", response_model=GenreRead)
def update_genre(genre_id: int, genre_data: GenreUpdate, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    update_data = genre_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(genre, key, value)

    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre


@router.delete("/{genre_id}")
def delete_genre(genre_id: int, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    session.delete(genre)
    session.commit()
    return {"message": "Genre deleted"}