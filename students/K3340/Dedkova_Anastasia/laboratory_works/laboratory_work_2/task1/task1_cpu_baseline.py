import time


def calculate_sum_naive(max_number: int) -> int:
    total = 0
    for i in range(1, max_number + 1):
        total += i
    return total


def formula_sum(max_number: int) -> int:
    return max_number * (max_number + 1) // 2


def main() -> None:
    raw_value = input("Введите верхнюю границу N [по умолчанию 100000000]: ").strip()

    if not raw_value:
        max_number = 100_000_000
    else:
        try:
            max_number = int(raw_value)
            if max_number <= 0:
                raise ValueError
        except ValueError:
            print("Некорректное значение. Будет использовано N = 100000000")
            max_number = 100_000_000

    print(f"\nЗапуск обычного последовательного вычисления для диапазона 1..{max_number}")
    print("Считается сумма в цикле, без threading / multiprocessing / asyncio.\n")

    start = time.perf_counter()
    total_sum = calculate_sum_naive(max_number)
    elapsed = time.perf_counter() - start

    expected = formula_sum(max_number)
    is_correct = total_sum == expected

    print("Результат:")
    print(f"sum = {total_sum}")
    print(f"expected = {expected}")
    print(f"correct = {is_correct}")
    print(f"execution_time_sec = {elapsed:.6f}")


if __name__ == "__main__":
    main()