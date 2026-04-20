from task1_result_logger import save_result


TARGET = 10_000_000_000_000


def expected_sum(n: int) -> int:
    return n * (n + 1) // 2


def add_estimate(approach: str, workers: int, estimated_seconds: float, comment: str) -> None:
    save_result(
        approach=approach,
        mode="A",
        max_number=TARGET,
        workers=workers,
        total_sum=expected_sum(TARGET),
        execution_time_sec=estimated_seconds,
        result_type="estimated",
        comment=comment
    )


if __name__ == "__main__":
    add_estimate(
        approach="threading",
        workers=4,
        estimated_seconds=227777.0,
        comment="Оценка по локальному тесту; полный запуск не завершался за разумное время"
    )

    add_estimate(
        approach="async",
        workers=4,
        estimated_seconds=227777.0,
        comment="Оценка по локальному тесту; async не даёт ускорения для CPU-bound задачи"
    )