from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlmodel import SQLModel

from db import engine, get_session
from models import User
from parser_core import PARSER_OWNER_ID, ParseResult, fetch_and_parse, save_book


def bootstrap() -> None:
    SQLModel.metadata.create_all(engine)
    with get_session() as session:
        if session.get(User, PARSER_OWNER_ID) is None:
            session.add(
                User(
                    id=PARSER_OWNER_ID,
                    username="parser",
                    email="parser@local",
                    hashed_password="!",
                )
            )
            session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    bootstrap()
    yield


app = FastAPI(title="Parser Service", lifespan=lifespan)


class ParseRequest(BaseModel):
    url: HttpUrl


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse")
def parse(req: ParseRequest) -> ParseResult:
    try:
        return save_book(fetch_and_parse(str(req.url)))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse failed: {e}")
