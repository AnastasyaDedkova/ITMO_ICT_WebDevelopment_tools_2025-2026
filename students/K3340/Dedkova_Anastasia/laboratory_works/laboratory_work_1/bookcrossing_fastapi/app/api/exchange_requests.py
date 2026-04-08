from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.exchange_request import ExchangeRequest
from app.models.book import Book
from app.models.user import User
from app.schemas.exchange_request import (
    ExchangeRequestCreate,
    ExchangeRequestRead,
    ExchangeRequestUpdate,
)

router = APIRouter(prefix="/exchange-requests", tags=["ExchangeRequests"])


@router.get("/", response_model=list[ExchangeRequestRead])
def get_exchange_requests(session: Session = Depends(get_session)):
    requests = session.exec(select(ExchangeRequest)).all()
    return requests


@router.get("/{request_id}", response_model=ExchangeRequestRead)
def get_exchange_request(request_id: int, session: Session = Depends(get_session)):
    exchange_request = session.get(ExchangeRequest, request_id)
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    return exchange_request


@router.post("/", response_model=ExchangeRequestRead)
def create_exchange_request(
    request_data: ExchangeRequestCreate,
    session: Session = Depends(get_session)
):
    book = session.get(Book, request_data.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    requester = session.get(User, request_data.requester_id)
    if not requester:
        raise HTTPException(status_code=404, detail="Requester not found")

    owner = session.get(User, request_data.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    exchange_request = ExchangeRequest(**request_data.model_dump())
    session.add(exchange_request)
    session.commit()
    session.refresh(exchange_request)
    return exchange_request


@router.patch("/{request_id}", response_model=ExchangeRequestRead)
def update_exchange_request(
    request_id: int,
    request_data: ExchangeRequestUpdate,
    session: Session = Depends(get_session)
):
    exchange_request = session.get(ExchangeRequest, request_id)
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    update_data = request_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(exchange_request, key, value)

    session.add(exchange_request)
    session.commit()
    session.refresh(exchange_request)
    return exchange_request


@router.delete("/{request_id}")
def delete_exchange_request(request_id: int, session: Session = Depends(get_session)):
    exchange_request = session.get(ExchangeRequest, request_id)
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    session.delete(exchange_request)
    session.commit()
    return {"message": "Exchange request deleted"}

@router.post("/{request_id}/accept", response_model=ExchangeRequestRead)
def accept_exchange_request(request_id: int, session: Session = Depends(get_session)):
    exchange_request = session.get(ExchangeRequest, request_id)
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    exchange_request.status = "accepted"
    session.add(exchange_request)
    session.commit()
    session.refresh(exchange_request)
    return exchange_request


@router.post("/{request_id}/reject", response_model=ExchangeRequestRead)
def reject_exchange_request(request_id: int, session: Session = Depends(get_session)):
    exchange_request = session.get(ExchangeRequest, request_id)
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    exchange_request.status = "rejected"
    session.add(exchange_request)
    session.commit()
    session.refresh(exchange_request)
    return exchange_request