from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.exchange import Exchange
from app.models.exchange_request import ExchangeRequest
from app.schemas.exchange import ExchangeCreate, ExchangeRead, ExchangeUpdate

from app.models.book import Book

from datetime import datetime

router = APIRouter(prefix="/exchanges", tags=["Exchanges"])


@router.get("/", response_model=list[ExchangeRead])
def get_exchanges(session: Session = Depends(get_session)):
    exchanges = session.exec(select(Exchange)).all()
    return exchanges


@router.get("/{exchange_id}", response_model=ExchangeRead)
def get_exchange(exchange_id: int, session: Session = Depends(get_session)):
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return exchange


@router.post("/", response_model=ExchangeRead)
def create_exchange(
    exchange_data: ExchangeCreate,
    session: Session = Depends(get_session)
):
    exchange_request = session.get(ExchangeRequest, exchange_data.request_id)
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    exchange = Exchange(**exchange_data.model_dump())
    session.add(exchange)
    session.commit()
    session.refresh(exchange)
    return exchange


@router.patch("/{exchange_id}", response_model=ExchangeRead)
def update_exchange(
    exchange_id: int,
    exchange_data: ExchangeUpdate,
    session: Session = Depends(get_session)
):
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    update_data = exchange_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(exchange, key, value)

    session.add(exchange)
    session.commit()
    session.refresh(exchange)
    return exchange


@router.delete("/{exchange_id}")
def delete_exchange(exchange_id: int, session: Session = Depends(get_session)):
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    session.delete(exchange)
    session.commit()
    return {"message": "Exchange deleted"}

@router.post("/{exchange_id}/complete")
def complete_exchange(exchange_id: int, session: Session = Depends(get_session)):
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    exchange_request = session.get(ExchangeRequest, exchange.request_id)
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    book = session.get(Book, exchange_request.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    exchange.status = "completed"
    exchange_request.status = "completed"
    book.status = "exchanged"

    session.add(exchange)
    session.add(exchange_request)
    session.add(book)
    session.commit()

    return {
        "message": "Exchange completed successfully",
        "exchange_id": exchange.id,
        "book_id": book.id,
        "book_status": book.status
    }

@router.post("/from-request/{request_id}", response_model=ExchangeRead)
def create_exchange_from_request(request_id: int, session: Session = Depends(get_session)):
    exchange_request = session.get(ExchangeRequest, request_id)
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    if exchange_request.status != "accepted":
        raise HTTPException(status_code=400, detail="Only accepted requests can be converted into exchange")

    existing_exchange = session.exec(
        select(Exchange).where(Exchange.request_id == request_id)
    ).first()

    if existing_exchange:
        raise HTTPException(status_code=400, detail="Exchange already exists for this request")

    exchange = Exchange(
        request_id=request_id,
        place="Место не указано",
        exchange_date=datetime.now(),
        status="planned",
        comment="Создано автоматически из принятого запроса"
    )

    session.add(exchange)
    session.commit()
    session.refresh(exchange)
    return exchange