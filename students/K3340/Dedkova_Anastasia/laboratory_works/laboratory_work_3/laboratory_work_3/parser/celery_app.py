import os

from celery import Celery
from celery.schedules import crontab

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery("parser", broker=BROKER_URL, backend=RESULT_BACKEND, include=["tasks"])

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
)

celery_app.conf.beat_schedule = {
    "cleanup-parser-books-daily": {
        "task": "tasks.cleanup_parser_books_task",
        "schedule": crontab(hour=3, minute=0),
    },
}
