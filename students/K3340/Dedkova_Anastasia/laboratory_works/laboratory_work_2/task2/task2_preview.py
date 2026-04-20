import asyncio
import multiprocessing as mp
import threading
import time

import aiohttp

from parser_utils import (
    PREVIEW_RESULTS_CSV,
    append_csv_result,
    append_preview_record,
    clear_file,
    load_urls,
    parse_url_async,
    parse_url_sync,
    split_into_chunks,
)


def run_sequential_preview() -> float:
    urls = load_urls()
    output_file = "parsed_preview_sequential.jsonl"
    clear_file(output_file)

    print(f"[SEQ] Загружено ссылок: {len(urls)}")
    print(f"[SEQ] Результат будет записан в: {output_file}")

    start = time.perf_counter()

    for index, url in enumerate(urls, start=1):
        try:
            book_data = parse_url_sync(url)
            append_preview_record(book_data, output_file)
            print(f"[SEQ {index}/{len(urls)}] {book_data['title']} | {book_data['author']}")
        except Exception as e:
            print(f"[SEQ ERROR {index}/{len(urls)}] {url}: {e}")

    elapsed = time.perf_counter() - start
    append_csv_result(PREVIEW_RESULTS_CSV, "sequential_preview", elapsed, len(urls))
    print(f"\n[SEQ] Готово за {elapsed:.4f} сек")
    return elapsed


def threading_worker(urls_chunk: list[str], output_file: str, total_urls: int) -> None:
    for index, url in enumerate(urls_chunk, start=1):
        try:
            book_data = parse_url_sync(url)
            append_preview_record(book_data, output_file)
            print(
                f"[THREAD {threading.current_thread().name} "
                f"{index}/{len(urls_chunk)} of chunk | total={total_urls}] "
                f"{book_data['title']}"
            )
        except Exception as e:
            print(f"[THREAD ERROR {threading.current_thread().name}] {url}: {e}")


def run_threading_preview(thread_count: int = 4) -> float:
    urls = load_urls()
    output_file = "parsed_preview_threading.jsonl"
    clear_file(output_file)

    print(f"[THREAD] Загружено ссылок: {len(urls)}")
    print(f"[THREAD] Количество потоков: {thread_count}")
    print(f"[THREAD] Результат будет записан в: {output_file}")

    start = time.perf_counter()
    chunks = split_into_chunks(urls, thread_count)
    threads = []

    for chunk_index, chunk in enumerate(chunks, start=1):
        print(f"[THREAD] Запуск потока {chunk_index}, ссылок в чанке: {len(chunk)}")
        thread = threading.Thread(
            target=threading_worker,
            args=(chunk, output_file, len(urls)),
            name=f"Thread-{chunk_index}",
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    elapsed = time.perf_counter() - start
    append_csv_result(PREVIEW_RESULTS_CSV, "threading_preview", elapsed, len(urls))
    print(f"\n[THREAD] Готово за {elapsed:.4f} сек")
    return elapsed


def multiprocessing_worker(urls_chunk: list[str], output_file: str, total_urls: int) -> None:
    for index, url in enumerate(urls_chunk, start=1):
        try:
            book_data = parse_url_sync(url)
            append_preview_record(book_data, output_file)
            print(
                f"[PROC {mp.current_process().pid} "
                f"{index}/{len(urls_chunk)} of chunk | total={total_urls}] "
                f"{book_data['title']}"
            )
        except Exception as e:
            print(f"[PROC ERROR {mp.current_process().pid}] {url}: {e}")


def run_multiprocessing_preview(process_count: int = 4) -> float:
    urls = load_urls()
    output_file = "parsed_preview_multiprocessing.jsonl"
    clear_file(output_file)

    print(f"[PROC] Загружено ссылок: {len(urls)}")
    print(f"[PROC] Количество процессов: {process_count}")
    print(f"[PROC] Результат будет записан в: {output_file}")

    start = time.perf_counter()
    chunks = split_into_chunks(urls, process_count)
    processes = []

    for chunk_index, chunk in enumerate(chunks, start=1):
        print(f"[PROC] Запуск процесса {chunk_index}, ссылок в чанке: {len(chunk)}")
        process = mp.Process(
            target=multiprocessing_worker,
            args=(chunk, output_file, len(urls)),
            name=f"Process-{chunk_index}",
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    elapsed = time.perf_counter() - start
    append_csv_result(PREVIEW_RESULTS_CSV, "multiprocessing_preview", elapsed, len(urls))
    print(f"\n[PROC] Готово за {elapsed:.4f} сек")
    return elapsed


async def run_async_preview(limit: int = 8) -> float:
    urls = load_urls()
    output_file = "parsed_preview_async.jsonl"
    clear_file(output_file)

    print(f"[ASYNC] Загружено ссылок: {len(urls)}")
    print(f"[ASYNC] Лимит одновременных задач: {limit}")
    print(f"[ASYNC] Результат будет записан в: {output_file}")

    start = time.perf_counter()
    semaphore = asyncio.Semaphore(limit)

    completed = 0
    completed_lock = asyncio.Lock()

    async def worker(url: str, session: aiohttp.ClientSession) -> None:
        nonlocal completed

        async with semaphore:
            try:
                book_data = await parse_url_async(url, session)
                append_preview_record(book_data, output_file)

                async with completed_lock:
                    completed += 1
                    print(f"[ASYNC {completed}/{len(urls)}] {book_data['title']}")
            except Exception as e:
                async with completed_lock:
                    completed += 1
                    print(f"[ASYNC ERROR {completed}/{len(urls)}] {url}: {e}")

    async with aiohttp.ClientSession() as session:
        tasks = [worker(url, session) for url in urls]
        await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start
    append_csv_result(PREVIEW_RESULTS_CSV, "async_preview", elapsed, len(urls))
    print(f"\n[ASYNC] Готово за {elapsed:.4f} сек")
    return elapsed


def main():
    print("1 - sequential preview")
    print("2 - threading preview")
    print("3 - multiprocessing preview")
    print("4 - async preview")
    print("5 - all preview")

    choice = input("Выбери режим: ").strip()

    if choice == "1":
        run_sequential_preview()

    elif choice == "2":
        run_threading_preview()

    elif choice == "3":
        mp.freeze_support()
        run_multiprocessing_preview()

    elif choice == "4":
        asyncio.run(run_async_preview())

    elif choice == "5":
        print("\n=== START SEQUENTIAL PREVIEW ===")
        run_sequential_preview()

        print("\n=== START THREADING PREVIEW ===")
        run_threading_preview()

        print("\n=== START MULTIPROCESSING PREVIEW ===")
        mp.freeze_support()
        run_multiprocessing_preview()

        print("\n=== START ASYNC PREVIEW ===")
        asyncio.run(run_async_preview())

        print("\n=== ALL PREVIEW FINISHED ===")

    else:
        print("Неизвестный режим.")


if __name__ == "__main__":
    main()