import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

OUTPUT_FILE = "book_urls.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}

REQUEST_DELAY_SEC = 0.7

# Несколько bookshelf-страниц Gutenberg.
# Так можно собрать заметно больше ссылок, чем с одной полки.
SOURCE_PAGES = [
    "https://www.gutenberg.org/ebooks/bookshelf/42",   # Horror
    "https://www.gutenberg.org/ebooks/bookshelf/41",   # Historical Fiction
    "https://www.gutenberg.org/ebooks/bookshelf/17",   # Children's Book Series
    "https://www.gutenberg.org/ebooks/bookshelf/138",  # Education
]

GUTENBERG_BOOK_RE = re.compile(r"^https://www\.gutenberg\.org/ebooks/\d+$", re.IGNORECASE)


def fetch_html(url: str, retries: int = 2, delay_sec: float = REQUEST_DELAY_SEC) -> str:
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
            response.encoding = response.apparent_encoding or response.encoding or "utf-8"
            return response.text
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(delay_sec)

    raise last_error


def normalize_url(url: str) -> str:
    return url.split("?", 1)[0].split("#", 1)[0].rstrip("/")


def is_valid_book_url(url: str) -> bool:
    return bool(GUTENBERG_BOOK_RE.match(url))


def extract_gutenberg_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href", "").strip()
        if not href:
            continue

        full_url = normalize_url(urljoin(base_url, href))
        if is_valid_book_url(full_url):
            urls.append(full_url)

    return list(dict.fromkeys(urls))


def extract_next_page_url(html: str, current_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href", "").strip()
        text = a_tag.get_text(" ", strip=True).lower()

        if href and "next" in text:
            return urljoin(current_url, href)

    return None


def ask_target_count(default: int = 100) -> int:
    raw_value = input(f"Сколько ссылок собрать? [по умолчанию {default}]: ").strip()

    if not raw_value:
        return default

    try:
        value = int(raw_value)
        if value <= 0:
            raise ValueError
        return value
    except ValueError:
        print(f"Некорректное значение. Будет использовано значение по умолчанию: {default}")
        return default


def collect_urls(target_count: int, delay_sec: float = REQUEST_DELAY_SEC) -> list[str]:
    collected = []
    seen = set()

    for start_url in SOURCE_PAGES:
        if len(collected) >= target_count:
            break

        current_url = start_url
        page_number = 1

        while current_url and len(collected) < target_count:
            try:
                html = fetch_html(current_url, retries=2, delay_sec=delay_sec)
                urls = extract_gutenberg_links(html, current_url)
            except Exception as e:
                print(f"[ERROR] source=gutenberg url={current_url}: {e}")
                break

            added_now = 0

            for url in urls:
                if url not in seen and is_valid_book_url(url):
                    seen.add(url)
                    collected.append(url)
                    added_now += 1

                if len(collected) >= target_count:
                    break

            print(
                f"[INFO] source={start_url} | page={page_number} | "
                f"url={current_url} | new={added_now} | total={len(collected)}"
            )

            if len(collected) >= target_count:
                break

            next_page_url = extract_next_page_url(html, current_url)
            if not next_page_url or next_page_url == current_url:
                break

            current_url = next_page_url
            page_number += 1
            time.sleep(delay_sec)

    return collected[:target_count]


def save_urls(urls: list[str], filepath: str = OUTPUT_FILE) -> None:
    path = Path(filepath)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for url in urls:
            f.write(url + "\n")


def main():
    target_count = ask_target_count(default=100)
    urls = collect_urls(target_count=target_count, delay_sec=REQUEST_DELAY_SEC)
    save_urls(urls, OUTPUT_FILE)

    print(f"\n[DONE] Saved {len(urls)} URLs to {OUTPUT_FILE}")
    print("[PREVIEW]")
    for url in urls[:20]:
        print(url)


if __name__ == "__main__":
    main()