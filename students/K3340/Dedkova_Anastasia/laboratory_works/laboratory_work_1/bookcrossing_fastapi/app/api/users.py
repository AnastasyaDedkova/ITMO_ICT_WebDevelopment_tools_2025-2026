from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

from app.core.dependencies import get_current_user
from app.core.security import verify_password, hash_password
from app.schemas.user import ChangePasswordRequest

from app.models.book import Book
from app.models.exchange_request import ExchangeRequest
from app.models.exchange import Exchange

router = APIRouter(prefix="/users", tags=["Users"])



@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=list[UserRead])
def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserRead)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    user = User(**user_data.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_data: UserUpdate, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return {"message": "User deleted"}


@router.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    current_user.hashed_password = hash_password(password_data.new_password)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return {"message": "Password changed successfully"}


@router.get("/me/books")
def get_my_books(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    books = session.exec(
        select(Book).where(
            Book.owner_id == current_user.id,
            Book.status == "available"
        )
    ).all()

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "books": [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "condition": book.condition,
                "status": book.status
            }
            for book in books
        ]
    }


@router.get("/me/exchange-requests/incoming")
def get_my_incoming_requests(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    requests = session.exec(
        select(ExchangeRequest).where(ExchangeRequest.owner_id == current_user.id)
    ).all()

    result = []

    for req in requests:
        book = session.get(Book, req.book_id)
        requester = session.get(User, req.requester_id)
        owner = session.get(User, req.owner_id)

        result.append({
            "id": req.id,
            "message": req.message,
            "status": req.status,
            "created_at": req.created_at,
            "book": {
                "id": book.id if book else None,
                "title": book.title if book else None,
                "author": book.author if book else None
            },
            "requester": {
                "id": requester.id if requester else None,
                "username": requester.username if requester else None
            },
            "owner": {
                "id": owner.id if owner else None,
                "username": owner.username if owner else None
            }
        })

    return result

@router.get("/me/exchange-requests/outgoing")
def get_my_outgoing_requests(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    requests = session.exec(
        select(ExchangeRequest).where(ExchangeRequest.requester_id == current_user.id)
    ).all()

    result = []

    for req in requests:
        book = session.get(Book, req.book_id)
        requester = session.get(User, req.requester_id)
        owner = session.get(User, req.owner_id)

        result.append({
            "id": req.id,
            "message": req.message,
            "status": req.status,
            "created_at": req.created_at,
            "book": {
                "id": book.id if book else None,
                "title": book.title if book else None,
                "author": book.author if book else None
            },
            "requester": {
                "id": requester.id if requester else None,
                "username": requester.username if requester else None
            },
            "owner": {
                "id": owner.id if owner else None,
                "username": owner.username if owner else None
            }
        })

    return result


@router.get("/me/exchanges")
def get_my_exchanges(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    my_requests = session.exec(
        select(ExchangeRequest).where(
            (ExchangeRequest.owner_id == current_user.id) |
            (ExchangeRequest.requester_id == current_user.id)
        )
    ).all()

    request_ids = [request.id for request in my_requests]

    if not request_ids:
        return []

    exchanges = session.exec(
        select(Exchange).where(Exchange.request_id.in_(request_ids))
    ).all()

    return exchanges