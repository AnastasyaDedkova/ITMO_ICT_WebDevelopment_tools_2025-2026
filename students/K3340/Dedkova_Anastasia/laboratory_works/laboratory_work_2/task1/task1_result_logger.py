import csv
import os


RESULTS_FILE = "task1_results.csv"


def save_result(
    approach: str,
    mode: str,
    max_number: int,
    workers: int,
    total_sum: int,
    execution_time_sec: float,
    result_type: str = "real",
    comment: str = ""
) -> None:
    """
    Сохраняет результат запуска программы в CSV-файл.

    Параметры:
    - approach: подход (threading, multiprocessing, async)
    - mode: режим (A или B)
    - max_number: верхняя граница диапазона
    - workers: количество потоков / процессов / задач
    - total_sum: итоговая сумма
    - execution_time_sec: время выполнения в секундах
    - result_type: тип результата (real / estimated)
    - comment: дополнительный комментарий
    """
    file_exists = os.path.exists(RESULTS_FILE)

    with open(RESULTS_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "approach",
                "mode",
                "max_number",
                "workers",
                "total_sum",
                "execution_time_sec",
                "result_type",
                "comment"
            ])

        writer.writerow([
            approach,
            mode,
            max_number,
            workers,
            total_sum,
            f"{execution_time_sec:.6f}",
            result_type,
            comment
        ])