from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister, session: Session = Depends(get_session)):
    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token({"sub": user.username})

    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user.username})

    return {"access_token": token, "token_type": "bearer"}