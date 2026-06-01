import os
import re
from typing import TypedDict

import requests
from bs4 import BeautifulSoup
from sqlalchemy import delete
from sqlmodel import select

from db import get_session
from models import Book, BookGenreLink, Genre

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}

GUTENBERG_BOOK_RE = re.compile(r"^https://www\.gutenberg\.org/ebooks/\d+$", re.IGNORECASE)

PARSER_OWNER_ID = int(os.getenv("PARSER_OWNER_ID", "1"))
PARSER_GENRE_NAME = os.getenv("PARSER_GENRE_NAME", "Project Gutenberg")
DEFAULT_BOOK_CONDITION = os.getenv("DEFAULT_BOOK_CONDITION", "good")
DEFAULT_BOOK_STATUS = os.getenv("DEFAULT_BOOK_STATUS", "available")


class BookData(TypedDict):
    title: str
    author: str
    description: str | None
    publication_year: int | None
    url: str


class ParseResult(TypedDict):
    saved: bool
    book_id: int | None
    data: BookData


def is_valid_book_url(url: str) -> bool:
    return bool(GUTENBERG_BOOK_RE.match(url))


def _normalize_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    if " by " in title:
        title = title.split(" by ", 1)[0].strip()
    return title


def _extract_title(soup: BeautifulSoup) -> str:
    tag = soup.select_one("h1")
    if tag and tag.get_text(strip=True):
        return _normalize_title(tag.get_text(" ", strip=True))
    if soup.title and soup.title.string:
        return _normalize_title(soup.title.string.split("|", 1)[0])
    return "Unknown title"


def _extract_author(soup: BeautifulSoup) -> str:
    body = soup.get_text("\n", strip=True)
    for pattern in (r"Author\s+([^\n]{2,120})", r"Creator\s+([^\n]{2,120})", r"by\s+([^\n]{2,120})"):
        match = re.search(pattern, body, flags=re.IGNORECASE)
        if match:
            author = match.group(1).strip()
            for stop in ("Language", "Subject", "LoC Class"):
                author = author.split(stop, 1)[0].strip()
            if author:
                return author
    return "Unknown author"


def _extract_description(soup: BeautifulSoup) -> str | None:
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        text = " ".join(meta["content"].split()).strip()
        if text and not text.lower().startswith("free ebook"):
            return text[:1500]
    return None


def _extract_year(soup: BeautifulSoup) -> int | None:
    body = soup.get_text("\n", strip=True)
    match = re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", body)
    if match:
        year = int(match.group(1))
        if 1500 <= year <= 2100:
            return year
    return None


def fetch_and_parse(url: str) -> BookData:
    if not is_valid_book_url(url):
        raise ValueError(f"Unsupported URL: {url}")

    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    return BookData(
        title=_extract_title(soup),
        author=_extract_author(soup),
        description=_extract_description(soup),
        publication_year=_extract_year(soup),
        url=url,
    )


def save_book(data: BookData) -> ParseResult:
    with get_session() as session:
        existing = session.exec(
            select(Book).where(
                Book.title == data["title"],
                Book.author == data["author"],
                Book.owner_id == PARSER_OWNER_ID,
            )
        ).first()

        if existing:
            return ParseResult(saved=False, book_id=existing.id, data=data)

        book = Book(
            owner_id=PARSER_OWNER_ID,
            title=data["title"],
            author=data["author"],
            description=data["description"],
            condition=DEFAULT_BOOK_CONDITION,
            status=DEFAULT_BOOK_STATUS,
            publication_year=data["publication_year"],
        )
        session.add(book)
        session.commit()
        session.refresh(book)

        genre = session.exec(select(Genre).where(Genre.name == PARSER_GENRE_NAME)).first()
        if not genre:
            genre = Genre(name=PARSER_GENRE_NAME, description="Books imported by parser")
            session.add(genre)
            session.commit()
            session.refresh(genre)

        session.add(BookGenreLink(book_id=book.id, genre_id=genre.id, is_primary=True))
        session.commit()

        return ParseResult(saved=True, book_id=book.id, data=data)


def cleanup_parser_books() -> int:
    with get_session() as session:
        genre = session.exec(select(Genre).where(Genre.name == PARSER_GENRE_NAME)).first()
        if not genre:
            return 0

        book_ids = list(
            session.exec(
                select(BookGenreLink.book_id).where(BookGenreLink.genre_id == genre.id)
            ).all()
        )
        session.exec(delete(BookGenreLink).where(BookGenreLink.genre_id == genre.id))
        if book_ids:
            session.exec(delete(Book).where(Book.id.in_(book_ids)))
        session.commit()
        return len(book_ids)
