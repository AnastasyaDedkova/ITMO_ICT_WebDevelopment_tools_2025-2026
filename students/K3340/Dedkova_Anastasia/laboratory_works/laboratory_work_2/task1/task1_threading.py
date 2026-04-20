import os
import threading
import time

from task1_result_logger import save_result


MODE = os.getenv("MODE", "B")

if MODE == "A":
    MAX_NUMBER = int(os.getenv("MAX_NUMBER", "10000000000000"))
else:
    MAX_NUMBER = int(os.getenv("MAX_NUMBER", "5000000000"))

NUM_THREADS = int(os.getenv("WORKERS", "4"))


def calculate_sum(start: int, end: int, results: list, index: int) -> None:
    """
    Считает сумму чисел в диапазоне от start до end включительно
    и сохраняет результат в results

    Параметры:
    start: начало диапазона
    end: конец диапазона
    results: общий список для хранения частичных сумм
    index: индекс, по которому сохранить результат
    """
    partial_sum = 0

    # Перебор всех чисел в диапазоне.
    for number in range(start, end + 1):
        partial_sum += number

    # Сохраняем результат работы конкретного потока
    results[index] = partial_sum


def split_range(max_number: int, parts: int) -> list[tuple[int, int]]:
    """
    Делит диапазон от 1 до max_number на parts частей

    Возвращает список кортежей:
    [(start1, end1), (start2, end2), ...]

    Пример:
    split_range(10, 3) -> [(1, 3), (4, 6), (7, 10)]
    """
    ranges = []
    chunk_size = max_number // parts
    start = 1

    for i in range(parts):
        end = start + chunk_size - 1

        # Последнему потоку отдаём остаток диапазона, чтобы покрыть все числа до max_number включительно
        if i == parts - 1:
            end = max_number

        ranges.append((start, end))
        start = end + 1

    return ranges


def main() -> None:
    """
    Использует предыдущие функции, запускает всё и ждёт завершения
    собирает итоговую сумму и выводит время выполнения
    """
    print("Задание 1: threading")
    print(f"Диапазон: от 1 до {MAX_NUMBER}")
    print(f"Количество потоков: {NUM_THREADS}")

    # Список для хранения частичных сумм
    # Каждый поток записывает результат в свою ячейку
    results = [0] * NUM_THREADS

    # Делим общий диапазон на части
    ranges = split_range(MAX_NUMBER, NUM_THREADS)

    threads = []

    # Засекаем время перед запуском потоков
    start_time = time.perf_counter()

    # Создаём и запускаем потоки
    for index, (range_start, range_end) in enumerate(ranges):
        thread = threading.Thread(
            target=calculate_sum,
            args=(range_start, range_end, results, index)
        )
        threads.append(thread)
        thread.start()

        print(f"Поток {index + 1} запущен: диапазон {range_start} - {range_end}")

    # Ждём завершения всех потоков
    for thread in threads:
        thread.join()

    # Считаем итоговую сумму как сумму всех частичных результатов
    total_sum = sum(results)

    # Засекаем время после завершения работы
    end_time = time.perf_counter()
    execution_time = end_time - start_time

    print("\nРезультаты")
    print(f"Итоговая сумма: {total_sum}")
    print(f"Время выполнения: {execution_time:.6f} секунд")
    save_result(
        approach="threading",
        mode=MODE,
        max_number=MAX_NUMBER,
        workers=NUM_THREADS,
        total_sum=total_sum,
        execution_time_sec=execution_time,
        result_type="real",
        comment="CPU-bound задача, запуск через threading"
    )


if __name__ == "__main__":
    main()
