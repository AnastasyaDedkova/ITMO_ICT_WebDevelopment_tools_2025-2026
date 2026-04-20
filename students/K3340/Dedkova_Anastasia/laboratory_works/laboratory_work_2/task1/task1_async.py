import os
import asyncio
import time

from task1_result_logger import save_result


MODE = os.getenv("MODE", "B")

if MODE == "A":
    MAX_NUMBER = int(os.getenv("MAX_NUMBER", "10000000000000"))
else:
    MAX_NUMBER = int(os.getenv("MAX_NUMBER", "5000000000"))

NUM_TASKS = int(os.getenv("WORKERS", "4"))


async def calculate_sum(start: int, end: int) -> int:
    """
    Асинхронная функция, которая считает сумму чисел
    в диапазоне от start до end включительно
    """
    partial_sum = 0

    # Реальный перебор всех чисел в диапазоне
    for number in range(start, end + 1):
        partial_sum += number

    return partial_sum


def split_range(max_number: int, parts: int) -> list[tuple[int, int]]:
    """
    Делит диапазон от 1 до max_number на parts частей

    Возвращает список кортежей:
    [(start1, end1), (start2, end2), ...]
    """
    ranges = []
    chunk_size = max_number // parts
    start = 1

    for i in range(parts):
        end = start + chunk_size - 1

        # Последней задаче отдаём остаток диапазона
        if i == parts - 1:
            end = max_number

        ranges.append((start, end))
        start = end + 1

    return ranges


async def main() -> None:
    """
    Использует предыдущие функции, создаёт асинхроные задачи,
    запускает их через asyncio.gather(), собирает итоговую сумму
    В конце выводит время выполнения
    """
    print("Задание 1: async")
    print(f"Диапазон: от 1 до {MAX_NUMBER}")
    print(f"Количество асинхронных задач: {NUM_TASKS}")

    ranges = split_range(MAX_NUMBER, NUM_TASKS)

    # Засекаем время перед запуском задач
    start_time = time.perf_counter()

    # Создаём список корутин
    tasks = [
        calculate_sum(range_start, range_end)
        for range_start, range_end in ranges
    ]

    # Одновременно запускаем все задачи и получаем список частичных сумм
    results = await asyncio.gather(*tasks)

    # Считаем итоговую сумму
    total_sum = sum(results)

    # Засекаем время после завершения
    end_time = time.perf_counter()
    execution_time = end_time - start_time

    print("\nРезультаты")
    print(f"Итоговая сумма: {total_sum}")
    print(f"Время выполнения: {execution_time:.6f} секунд")
    save_result(
        approach="async",
        mode=MODE,
        max_number=MAX_NUMBER,
        workers=NUM_TASKS,
        total_sum=total_sum,
        execution_time_sec=execution_time,
        result_type="real",
        comment="CPU-bound задача, async-реализация"
    )

if __name__ == "__main__":
    asyncio.run(main())