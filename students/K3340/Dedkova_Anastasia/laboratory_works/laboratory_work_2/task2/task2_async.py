import asyncio
import aiohttp

from parser_utils import (
    DB_RESULTS_CSV,
    append_csv_result,
    clear_parser_import,
    load_urls,
    parse_url_async,
    save_book_to_db,
)

import time


async def run_async(limit: int = 8) -> float:
    urls = load_urls()
    clear_parser_import()

    start = time.perf_counter()
    semaphore = asyncio.Semaphore(limit)

    async def worker(url: str, session: aiohttp.ClientSession) -> None:
        async with semaphore:
            try:
                book_data = await parse_url_async(url, session)
                save_book_to_db(book_data)
            except Exception as e:
                print(f"[ASYNC ERROR] {url}: {e}")

    async with aiohttp.ClientSession() as session:
        tasks = [worker(url, session) for url in urls]
        await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start
    append_csv_result(DB_RESULTS_CSV, "async_db", elapsed, len(urls))
    print(f"\nAsync DB finished in {elapsed:.4f} sec")
    return elapsed


if __name__ == "__main__":
    asyncio.run(run_async())