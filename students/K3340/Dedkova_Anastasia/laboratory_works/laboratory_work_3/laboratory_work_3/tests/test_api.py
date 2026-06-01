from __future__ import annotations

import time
from collections.abc import Iterator

import httpx
import pytest

API = "http://localhost:8000"
PARSER = "http://localhost:8001"

PRIDE_AND_PREJUDICE = "https://www.gutenberg.org/ebooks/1342"
FRANKENSTEIN = "https://www.gutenberg.org/ebooks/84"


@pytest.fixture(scope="session")
def client() -> Iterator[httpx.Client]:
    with httpx.Client(timeout=60.0) as c:
        yield c


def _poll_task(client: httpx.Client, task_id: str, timeout: float = 30.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        body = client.get(f"{API}/tasks/{task_id}").json()
        if body["status"] in {"SUCCESS", "FAILURE"}:
            return body
        time.sleep(1.0)
    pytest.fail(f"Task {task_id} did not finish in {timeout}s")


def test_api_and_parser_are_alive(client: httpx.Client) -> None:
    assert client.get(f"{API}/health").json() == {"status": "ok"}
    assert client.get(f"{PARSER}/health").json() == {"status": "ok"}


def test_parse_sync_returns_real_gutenberg_book(client: httpx.Client) -> None:
    response = client.post(f"{API}/parse", json={"url": PRIDE_AND_PREJUDICE})
    assert response.status_code == 200

    body = response.json()
    assert body["book_id"] is not None

    data = body["data"]
    assert "Pride and Prejudice" in data["title"]
    assert "Austen" in data["author"]
    assert data["publication_year"] == 1813
    assert data["url"] == PRIDE_AND_PREJUDICE


def test_parse_sync_is_idempotent(client: httpx.Client) -> None:
    first = client.post(f"{API}/parse", json={"url": PRIDE_AND_PREJUDICE}).json()
    second = client.post(f"{API}/parse", json={"url": PRIDE_AND_PREJUDICE}).json()

    assert second["saved"] is False
    assert second["book_id"] == first["book_id"]


def test_parse_async_enqueues_and_completes(client: httpx.Client) -> None:
    queued = client.post(f"{API}/parse-async", json={"url": FRANKENSTEIN}).json()
    assert queued["status"] == "queued"
    assert queued["task_id"]

    finished = _poll_task(client, queued["task_id"])
    assert finished["status"] == "SUCCESS"

    data = finished["result"]["data"]
    assert "Frankenstein" in data["title"]
    assert "Shelley" in data["author"]
    assert data["publication_year"] == 1818


def test_unsupported_domain_returns_400(client: httpx.Client) -> None:
    response = client.post(f"{API}/parse", json={"url": "https://example.com/book/1"})
    assert response.status_code == 400


def test_malformed_url_returns_422(client: httpx.Client) -> None:
    response = client.post(f"{API}/parse", json={"url": "not-a-url"})
    assert response.status_code == 422
