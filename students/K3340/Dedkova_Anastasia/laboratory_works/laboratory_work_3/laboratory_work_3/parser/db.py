import os

from sqlmodel import Session, create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/bookcrossing"
)

engine = create_engine(DATABASE_URL, echo=False)


def get_session() -> Session:
    return Session(engine)
