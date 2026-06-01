from celery_app import celery_app
from parser_core import ParseResult, cleanup_parser_books, fetch_and_parse, save_book


@celery_app.task(name="tasks.parse_url_task", bind=True, max_retries=2, default_retry_delay=10)
def parse_url_task(self, url: str) -> ParseResult:
    try:
        return save_book(fetch_and_parse(url))
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(name="tasks.cleanup_parser_books_task")
def cleanup_parser_books_task() -> dict[str, int]:
    return {"deleted": cleanup_parser_books()}
