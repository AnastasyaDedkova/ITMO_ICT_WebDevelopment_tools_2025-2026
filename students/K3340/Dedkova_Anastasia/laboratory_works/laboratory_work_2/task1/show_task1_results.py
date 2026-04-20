import csv


RESULTS_FILE = "task1_results.csv"
TARGET_MAX_NUMBER = 10_000_000_000_000


def expected_sum(n: int) -> int:
    """
    Считает сумму чисел от 1 до n по формуле
    """
    return n * (n + 1) // 2


def read_results(file_name: str) -> list[dict]:
    """
    Читает CSV-файл с результатами и возвращает список словарей
    """
    with open(file_name, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def seconds_to_human(seconds: float) -> str:
    """
    Переводит секунды в более удобный вид: часы и сутки
    """
    hours = seconds / 3600
    days = hours / 24
    return f"{seconds:.6f} сек | {hours:.2f} ч | {days:.2f} сут"


def estimate_time(base_time: float, base_n: int, target_n: int) -> float:
    """
    Линейная экстраполяция времени выполнения
    """
    return base_time * (target_n / base_n)


def find_best_real_b_rows(rows: list[dict]) -> dict[str, dict]:
    """
    Для каждого подхода ищет лучший реальный результат режима B
    Если реальных B несколько, берёт запись с самым большим max_number
    """
    best_rows = {}
    approaches = ["threading", "async", "multiprocessing"]

    for approach in approaches:
        candidates = [
            row for row in rows
            if row["approach"] == approach
            and row["mode"] == "B"
            and row["result_type"] == "real"
        ]

        if candidates:
            best_row = max(candidates, key=lambda row: int(row["max_number"]))
            best_rows[approach] = best_row

    return best_rows


def build_estimated_rows(best_b_rows: dict[str, dict]) -> list[dict]:
    """
    Строит теоретические значения для режима A
    на основе лучших реальных значений режима B
    """
    estimated_rows = []

    for approach, row in best_b_rows.items():
        base_n = int(row["max_number"])
        base_time = float(row["execution_time_sec"])
        workers = int(row["workers"])

        estimated_execution_time = estimate_time(
            base_time=base_time,
            base_n=base_n,
            target_n=TARGET_MAX_NUMBER
        )

        estimated_rows.append({
            "approach": approach,
            "mode": "A",
            "max_number": TARGET_MAX_NUMBER,
            "workers": workers,
            "total_sum": expected_sum(TARGET_MAX_NUMBER),
            "execution_time_sec": estimated_execution_time,
            "result_type": "estimated",
            "comment": (
                f"Оценка по результату B={base_n}; "
                f"линейная экстраполяция"
            )
        })

    return estimated_rows


def print_real_results(rows: list[dict]) -> None:
    """
    Печатает реальные результаты из CSV
    """
    print("=" * 100)
    print("РЕАЛЬНЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 100)

    if not rows:
        print("Нет данных для отображения.\n")
        return

    for row in rows:
        print(f"Подход            : {row['approach']}")
        print(f"Режим             : {row['mode']}")
        print(f"Диапазон          : 1..{row['max_number']}")
        print(f"Воркеры           : {row['workers']}")
        print(f"Сумма             : {row['total_sum']}")
        print(f"Время             : {seconds_to_human(float(row['execution_time_sec']))}")
        print(f"Тип результата    : {row['result_type']}")
        print(f"Комментарий       : {row['comment']}")
        print("-" * 100)


def print_estimated_results(rows: list[dict]) -> None:
    """
    Печатает оценочные результаты для режима A
    """
    print("\n" + "=" * 100)
    print("ТЕОРЕТИЧЕСКИЕ ОЦЕНКИ ДЛЯ РЕЖИМА A")
    print("=" * 100)

    if not rows:
        print("Не удалось построить оценочные значения.\n")
        return

    for row in rows:
        print(f"Подход            : {row['approach']}")
        print(f"Режим             : {row['mode']}")
        print(f"Диапазон          : 1..{row['max_number']}")
        print(f"Воркеры           : {row['workers']}")
        print(f"Ожидаемая сумма   : {row['total_sum']}")
        print(f"Оценка времени    : {seconds_to_human(float(row['execution_time_sec']))}")
        print(f"Тип результата    : {row['result_type']}")
        print(f"Комментарий       : {row['comment']}")
        print("-" * 100)


def print_summary_table(real_rows: list[dict], estimated_rows: list[dict]) -> None:
    """
    Печатает компактную сводную таблицу
    """
    print("\n" + "=" * 100)
    print("СВОДКА")
    print("=" * 100)

    print(
        f"{'Подход':<18}"
        f"{'Режим':<8}"
        f"{'Диапазон':<18}"
        f"{'Время (сек)':<18}"
        f"{'Тип':<12}"
    )
    print("-" * 100)

    for row in real_rows:
        print(
            f"{row['approach']:<18}"
            f"{row['mode']:<8}"
            f"{('1..' + row['max_number']):<18}"
            f"{float(row['execution_time_sec']):<18.6f}"
            f"{row['result_type']:<12}"
        )

    for row in estimated_rows:
        print(
            f"{row['approach']:<18}"
            f"{row['mode']:<8}"
            f"{('1..' + str(row['max_number'])):<18}"
            f"{float(row['execution_time_sec']):<18.6f}"
            f"{row['result_type']:<12}"
        )


def main() -> None:
    try:
        rows = read_results(RESULTS_FILE)

        print_real_results(rows)

        best_b_rows = find_best_real_b_rows(rows)
        estimated_rows = build_estimated_rows(best_b_rows)

        print_estimated_results(estimated_rows)
        print_summary_table(rows, estimated_rows)

    except FileNotFoundError:
        print("Файл с результатами пока не найден.")


if __name__ == "__main__":
    main()