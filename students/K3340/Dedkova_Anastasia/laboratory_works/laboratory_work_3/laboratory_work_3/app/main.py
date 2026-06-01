import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from celery import Celery
from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

PARSER_URL = os.getenv("PARSER_URL", "http://parser:8001")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_client = Celery("api", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with httpx.AsyncClient(base_url=PARSER_URL, timeout=60) as client:
        app.state.http = client
        yield


app = FastAPI(title="BookCrossing API", lifespan=lifespan)


class ParseRequest(BaseModel):
    url: HttpUrl


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse")
async def parse_sync(req: ParseRequest) -> dict[str, Any]:
    try:
        resp = await app.state.http.post("/parse", json={"url": str(req.url)})
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Parser unreachable: {e}")


@app.post("/parse-async")
async def parse_async(req: ParseRequest) -> dict[str, str]:
    result = celery_client.send_task("tasks.parse_url_task", args=[str(req.url)])
    return {"task_id": result.id, "status": "queued"}


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> dict[str, Any]:
    result = AsyncResult(task_id, app=celery_client)
    payload: Any = None
    if result.ready():
        try:
            payload = result.get(timeout=1)
        except Exception as e:
            payload = {"error": str(e)}
    return {"task_id": task_id, "status": result.status, "result": payload}
