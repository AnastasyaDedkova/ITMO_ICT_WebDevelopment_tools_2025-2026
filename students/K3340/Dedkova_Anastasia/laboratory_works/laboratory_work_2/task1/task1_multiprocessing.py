import os
import multiprocessing
import time

from task1_result_logger import save_result


MODE = os.getenv("MODE", "B")

if MODE == "A":
    MAX_NUMBER = int(os.getenv("MAX_NUMBER", "10000000000000"))
else:
    MAX_NUMBER = int(os.getenv("MAX_NUMBER", "5000000000"))

NUM_PROCESSES = int(os.getenv("WORKERS", "4"))


def calculate_sum(start: int, end: int, queue: multiprocessing.Queue) -> None:
    """
    Считает сумму чисел в диапазоне от start до end включительно
    и отправляет результат в очередь
    """
    partial_sum = 0

    for number in range(start, end + 1):
        partial_sum += number

    queue.put(partial_sum)


def split_range(max_number: int, parts: int) -> list[tuple[int, int]]:
    """
    Делит диапазон от 1 до max_number на parts частей
    """
    ranges = []
    chunk_size = max_number // parts
    start = 1

    for i in range(parts):
        end = start + chunk_size - 1

        if i == parts - 1:
            end = max_number

        ranges.append((start, end))
        start = end + 1

    return ranges


def main() -> None:
    """
    Использует предыдущие функции, запускает всё получает частичные суммы
    собирает итоговую сумму и выводит время выполнения
      """
    print("Задание 1: multiprocessing")
    print(f"Режим: {MODE}")
    print(f"Диапазон: от 1 до {MAX_NUMBER}")
    print(f"Количество процессов: {NUM_PROCESSES}")

    ranges = split_range(MAX_NUMBER, NUM_PROCESSES)
    result_queue = multiprocessing.Queue()
    processes = []

    start_time = time.perf_counter()

    for range_start, range_end in ranges:
        process = multiprocessing.Process(
            target=calculate_sum,
            args=(range_start, range_end, result_queue)
        )
        processes.append(process)
        process.start()

    total_sum = 0
    for _ in range(NUM_PROCESSES):
        total_sum += result_queue.get()

    for process in processes:
        process.join()

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    print("\nРезультаты")
    print(f"Итоговая сумма: {total_sum}")
    print(f"Время выполнения: {execution_time:.6f} секунд")
    save_result(
        approach="multiprocessing",
        mode=MODE,
        max_number=MAX_NUMBER,
        workers=NUM_PROCESSES,
        total_sum=total_sum,
        execution_time_sec=execution_time,
        result_type="real",
        comment="CPU-bound задача, запуск через multiprocessing"
    )

if __name__ == "__main__":
    main()