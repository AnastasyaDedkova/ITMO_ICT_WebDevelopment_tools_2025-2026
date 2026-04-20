import multiprocessing as mp
import time

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
            print(f"[PROC ERROR] {url}: {e}")


def run_multiprocessing(process_count: int = 4) -> float:
    urls = load_urls()
    clear_parser_import()

    start = time.perf_counter()

    chunks = split_into_chunks(urls, process_count)
    processes = []

    for chunk in chunks:
        process = mp.Process(target=worker, args=(chunk,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    elapsed = time.perf_counter() - start
    append_csv_result(DB_RESULTS_CSV, "multiprocessing_db", elapsed, len(urls))
    print(f"\nMultiprocessing DB finished in {elapsed:.4f} sec")
    return elapsed


if __name__ == "__main__":
    mp.freeze_support()
    run_multiprocessing()