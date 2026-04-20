import csv
import os
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).parent
RESULTS_FILE = BASE_DIR / "task1_workers_experiment.csv"

MAX_NUMBER = 5_000_000_000
MODE = "B"

# Список значений workers для эксперимента
WORKERS_LIST = [1, 2, 4, 8, 16]

# Файлы программ
SCRIPTS = [
    ("threading", "task1_threading.py"),
    ("async", "task1_async.py"),
    ("multiprocessing", "task1_multiprocessing.py"),
]


def ensure_results_file() -> None:
    """
    Создаёт CSV-файл с заголовком, если его ещё нет.
    """
    if RESULTS_FILE.exists():
        return

    with open(RESULTS_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "approach",
            "mode",
            "max_number",
            "workers",
            "return_code",
            "status",
        ])


def append_result(
    approach: str,
    mode: str,
    max_number: int,
    workers: int,
    return_code: int,
    status: str,
) -> None:
    """
    Дописывает краткий результат запуска в CSV.
    """
    with open(RESULTS_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            approach,
            mode,
            max_number,
            workers,
            return_code,
            status,
        ])


def run_script(script_name: str, workers: int) -> int:
    """
    Запускает один скрипт с нужными параметрами через переменные окружения.
    """
    env = os.environ.copy()
    env["MODE"] = MODE
    env["MAX_NUMBER"] = str(MAX_NUMBER)
    env["WORKERS"] = str(workers)

    result = subprocess.run(
        [sys.executable, script_name],
        cwd=BASE_DIR,
        env=env
    )

    return result.returncode


def main() -> None:
    ensure_results_file()

    print("=== Эксперимент по числу workers для задания 1 ===")
    print(f"Режим: {MODE}")
    print(f"Диапазон: 1..{MAX_NUMBER}")
    print(f"Workers: {WORKERS_LIST}")
    print()

    for workers in WORKERS_LIST:
        print("=" * 80)
        print(f"Запуск серии для workers = {workers}")
        print("=" * 80)

        for approach, script_name in SCRIPTS:
            print(f"\n>>> Запуск {approach} ({script_name}), workers = {workers}")

            return_code = run_script(script_name, workers)

            if return_code == 0:
                status = "ok"
                print(f"<<< Успешно завершено: {approach}, workers = {workers}")
            else:
                status = "error"
                print(
                    f"<<< Ошибка: {approach}, workers = {workers}, "
                    f"код возврата = {return_code}"
                )

            append_result(
                approach=approach,
                mode=MODE,
                max_number=MAX_NUMBER,
                workers=workers,
                return_code=return_code,
                status=status,
            )

    print("\n=== Эксперимент завершён ===")
    print("Основные времена смотри в task1_results.csv")
    print("Технический журнал запусков сохранён в task1_workers_experiment.csv")


if __name__ == "__main__":
    main()