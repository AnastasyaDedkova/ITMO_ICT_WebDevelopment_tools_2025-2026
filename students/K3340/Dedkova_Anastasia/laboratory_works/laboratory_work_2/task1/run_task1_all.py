import subprocess
import sys
from pathlib import Path


def run_script(script_name: str) -> None:
    """
    Запускает Python-скрипт как отдельный процесс
    Если скрипт завершился с ошибкой, выполнение останавливается
    """
    print(f"\n{'=' * 60}")
    print(f"Запуск файла: {script_name}")
    print(f"{'=' * 60}\n")

    result = subprocess.run(
        [sys.executable, script_name],
        cwd=Path(__file__).parent
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Скрипт {script_name} завершился с ошибкой. "
            f"Код возврата: {result.returncode}"
        )

    print(f"\nФайл {script_name} успешно завершён.\n")


def main() -> None:
    """
    Последовательно запускает:
    1. threading
    2. async
    3. multiprocessing
    """
    scripts = [
        "task1_threading.py",
        "task1_async.py",
        "task1_multiprocessing.py",
    ]

    print("Последовательный запуск программ задания 1")

    for script in scripts:
        run_script(script)

    print("\nВсе программы успешно выполнены")


if __name__ == "__main__":
    main()
