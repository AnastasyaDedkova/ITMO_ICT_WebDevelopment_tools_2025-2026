import time
import threading

from parser_utils import (
    DB_RESULTS_CSV,
    append_csv_result,
    clear_parser_import,
    load_urls,
    parse_url_sync,
    save_book_to_db,
    split_into_chunks,
)


def worker(urls_chunk: list[str]) -> None:
    for url in urls_chunk:
        try:
            book_data = parse_url_sync(url)
            save_book_to_db(book_data)
        except Exception as e:
            print(f"[THREAD ERROR] {url}: {e}")


def run_threading(thread_count: int = 4) -> float:
    urls = load_urls()
    clear_parser_import()

    start = time.perf_counter()

    chunks = split_into_chunks(urls, thread_count)
    threads = []

    for chunk in chunks:
        thread = threading.Thread(target=worker, args=(chunk,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    elapsed = time.perf_counter() - start
    append_csv_result(DB_RESULTS_CSV, "threading_db", elapsed, len(urls))
    print(f"\nThreading DB finished in {elapsed:.4f} sec")
    return elapsed


if __name__ == "__main__":
    run_threading()