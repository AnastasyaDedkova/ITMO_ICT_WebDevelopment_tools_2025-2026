import asyncio
import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Optional

import aiohttp
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sqlmodel import select

from db import get_session
from models import Book, Genre, BookGenreLink

try:
    from models import ExchangeRequest
except ImportError:
    ExchangeRequest = None

load_dotenv()

URLS_FILE = "book_urls.txt"
DB_RESULTS_CSV = "task2_db_results.csv"
PREVIEW_RESULTS_CSV = "task2_preview_results.csv"

PARSER_OWNER_ID = int(os.getenv("PARSER_OWNER_ID", "1"))
PARSER_GENRE_NAME = os.getenv("PARSER_GENRE_NAME", "Project Gutenberg").strip() or "Project Gutenberg"
DEFAULT_BOOK_CONDITION = os.getenv("DEFAULT_BOOK_CONDITION", "good").strip() or "good"
DEFAULT_BOOK_STATUS = os.getenv("DEFAULT_BOOK_STATUS", "available").strip() or "available"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}

GUTENBERG_BOOK_RE = re.compile(r"^https://www\.gutenberg\.org/ebooks/\d+$", re.IGNORECASE)

_file_lock = threading.Lock()


def is_valid_book_url(url: str) -> bool:
    return bool(GUTENBERG_BOOK_RE.match(url))


def load_urls(filepath: str = URLS_FILE) -> list[str]:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Файл со ссылками не найден: {filepath}")

    with path.open("r", encoding="utf-8") as f:
        raw_urls = [line.strip() for line in f if line.strip()]

    cleaned_urls = []
    seen = set()

    for url in raw_urls:
        if not is_valid_book_url(url):
            continue
        if url not in seen:
            seen.add(url)
            cleaned_urls.append(url)

    return cleaned_urls


def split_into_chunks(items: list[str], parts: int) -> list[list[str]]:
    parts = max(1, parts)
    result = [[] for _ in range(parts)]
    for i, item in enumerate(items):
        result[i % parts].append(item)
    return [chunk for chunk in result if chunk]


def normalize_gutenberg_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    if " by " in title:
        title = title.split(" by ", 1)[0].strip()
    return title


def extract_gutenberg_title(soup: BeautifulSoup) -> str:
    selectors = ["h1", ".ebook h1"]

    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            text = tag.get_text(" ", strip=True)
            if text:
                return normalize_gutenberg_title(text)

    if soup.title and soup.title.string:
        title = soup.title.string.strip().split("|", 1)[0].strip()
        if title:
            return normalize_gutenberg_title(title)

    return "Unknown title"


def extract_gutenberg_author(soup: BeautifulSoup) -> str:
    body_text = soup.get_text("\n", strip=True)

    patterns = [
        r"Author\s+([^\n]{2,120})",
        r"Creator\s+([^\n]{2,120})",
        r"by\s+([^\n]{2,120})",
    ]

    for pattern in patterns:
        match = re.search(pattern, body_text, flags=re.IGNORECASE)
        if match:
            author = match.group(1).strip()
            author = author.split("Language", 1)[0].strip()
            author = author.split("Subject", 1)[0].strip()
            author = author.split("LoC Class", 1)[0].strip()
            if author:
                return author

    return "Unknown author"


def extract_gutenberg_description(soup: BeautifulSoup) -> Optional[str]:
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        return meta_desc["content"].strip()[:1500]
    return None


def extract_gutenberg_year(soup: BeautifulSoup) -> Optional[int]:
    body_text = soup.get_text("\n", strip=True)

    for pattern in [r"\b(19\d{2}|20\d{2})\b", r",\s*(19\d{2}|20\d{2})\b"]:
        match = re.search(pattern, body_text)
        if match:
            year = int(match.group(1))
            if 1500 <= year <= 2100:
                return year

    return None


def parse_book_data_from_html(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    title = extract_gutenberg_title(soup)
    if title == "Unknown title":
        raise ValueError(f"Не удалось получить title: {url}")

    return {
        "source": "gutenberg",
        "url": url,
        "title": title,
        "author": extract_gutenberg_author(soup),
        "publication_year": extract_gutenberg_year(soup),
        "description": extract_gutenberg_description(soup),
    }


def decode_response_content(response: requests.Response) -> str:
    content = response.content
    encodings_to_try = []

    if response.apparent_encoding:
        encodings_to_try.append(response.apparent_encoding)

    encodings_to_try.extend(["utf-8", "windows-1252"])

    for encoding in encodings_to_try:
        try:
            return content.decode(encoding)
        except Exception:
            continue

    return response.text


def fetch_html(url: str, retries: int = 2, delay_sec: float = 0.5) -> str:
    last_error = None

    for attempt in range(retries + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=20,
                allow_redirects=True,
            )
            response.raise_for_status()
            return decode_response_content(response)
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(delay_sec)

    raise last_error


async def fetch_html_async(
    url: str,
    session: aiohttp.ClientSession,
    retries: int = 2,
    delay_sec: float = 0.5,
) -> str:
    last_error = None

    for attempt in range(retries + 1):
        try:
            async with session.get(
                url,
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=20),
                allow_redirects=True,
            ) as response:
                response.raise_for_status()
                raw_bytes = await response.read()

                encodings_to_try = []
                if response.charset:
                    encodings_to_try.append(response.charset)

                encodings_to_try.extend(["utf-8", "windows-1252"])

                for encoding in encodings_to_try:
                    try:
                        return raw_bytes.decode(encoding)
                    except Exception:
                        continue

                return raw_bytes.decode("utf-8", errors="replace")

        except Exception as e:
            last_error = e
            if attempt < retries:
                await asyncio.sleep(delay_sec)

    raise last_error


def parse_url_sync(url: str) -> dict:
    html = fetch_html(url)
    return parse_book_data_from_html(html, url)


async def parse_url_async(url: str, session: aiohttp.ClientSession) -> dict:
    html = await fetch_html_async(url, session)
    return parse_book_data_from_html(html, url)


def normalize_description(description: str | None) -> str | None:
    if not description:
        return None

    cleaned = " ".join(description.split()).strip()
    if cleaned.lower().startswith("free ebook"):
        return None

    return cleaned[:1500] if cleaned else None


def normalize_publication_year(year: int | None) -> int | None:
    if year is None:
        return None
    if 1500 <= year <= 2100:
        return year
    return None


def get_or_create_genre(session, genre_name: str) -> Genre:
    existing_genre = session.exec(
        select(Genre).where(Genre.name == genre_name)
    ).first()

    if existing_genre:
        return existing_genre

    genre = Genre(
        name=genre_name,
        description=f"Книги, импортированные парсером из {genre_name}"
    )
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre


def find_existing_book(session, title: str, author: str, owner_id: int) -> Book | None:
    return session.exec(
        select(Book).where(
            Book.title == title,
            Book.author == author,
            Book.owner_id == owner_id
        )
    ).first()


def find_existing_link(session, book_id: int, genre_id: int) -> BookGenreLink | None:
    return session.exec(
        select(BookGenreLink).where(
            BookGenreLink.book_id == book_id,
            BookGenreLink.genre_id == genre_id
        )
    ).first()


def save_book_to_db(book_data: dict) -> None:
    with get_session() as session:
        existing_book = find_existing_book(
            session=session,
            title=book_data["title"],
            author=book_data["author"],
            owner_id=PARSER_OWNER_ID,
        )

        if existing_book:
            print(f"[SKIP] Уже есть в БД: {book_data['title']} | {book_data['author']}")
            return

        book = Book(
            owner_id=PARSER_OWNER_ID,
            title=book_data["title"],
            author=book_data["author"],
            description=normalize_description(book_data.get("description")),
            condition=DEFAULT_BOOK_CONDITION,
            status=DEFAULT_BOOK_STATUS,
            publication_year=normalize_publication_year(book_data.get("publication_year")),
        )

        session.add(book)
        session.commit()
        session.refresh(book)

        genre = get_or_create_genre(session, PARSER_GENRE_NAME)

        existing_link = find_existing_link(session, book.id, genre.id)
        if not existing_link:
            link = BookGenreLink(
                book_id=book.id,
                genre_id=genre.id,
                is_primary=True,
            )
            session.add(link)
            session.commit()


def clear_parser_import() -> None:
    with get_session() as session:
        parser_genre = session.exec(
            select(Genre).where(Genre.name == PARSER_GENRE_NAME)
        ).first()

        if not parser_genre:
            return

        links = session.exec(
            select(BookGenreLink).where(BookGenreLink.genre_id == parser_genre.id)
        ).all()

        parser_book_ids = [link.book_id for link in links]

        if parser_book_ids and ExchangeRequest is not None:
            exchange_requests = session.exec(
                select(ExchangeRequest).where(ExchangeRequest.book_id.in_(parser_book_ids))
            ).all()
            for request in exchange_requests:
                session.delete(request)
            session.commit()

        if links:
            for link in links:
                session.delete(link)
            session.commit()

        if parser_book_ids:
            books = session.exec(
                select(Book).where(Book.id.in_(parser_book_ids))
            ).all()
            for book in books:
                session.delete(book)
            session.commit()

        parser_genre = session.exec(
            select(Genre).where(Genre.name == PARSER_GENRE_NAME)
        ).first()

        if parser_genre:
            remaining_links = session.exec(
                select(BookGenreLink).where(BookGenreLink.genre_id == parser_genre.id)
            ).all()

            if not remaining_links:
                session.delete(parser_genre)
                session.commit()


def append_csv_result(csv_file: str, mode: str, elapsed: float, total_urls: int) -> None:
    file_exists = Path(csv_file).exists()

    with open(csv_file, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("mode,elapsed_sec,total_urls\n")
        f.write(f"{mode},{elapsed:.4f},{total_urls}\n")


def clear_file(filepath: str) -> None:
    Path(filepath).write_text("", encoding="utf-8")


def append_preview_record(record: dict, filepath: str) -> None:
    with _file_lock:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")