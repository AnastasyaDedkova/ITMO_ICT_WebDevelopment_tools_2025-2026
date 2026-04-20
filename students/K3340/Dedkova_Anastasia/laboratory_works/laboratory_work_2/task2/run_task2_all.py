import asyncio
import multiprocessing as mp

from task2_threading import run_threading
from task2_multiprocessing import run_multiprocessing
from task2_async import run_async


def main():
    print("1 - threading")
    print("2 - multiprocessing")
    print("3 - async")
    print("4 - all")

    choice = input("Выбери режим: ").strip()

    if choice == "1":
        run_threading()

    elif choice == "2":
        mp.freeze_support()
        run_multiprocessing()

    elif choice == "3":
        asyncio.run(run_async())

    elif choice == "4":
        run_threading()
        mp.freeze_support()
        run_multiprocessing()
        asyncio.run(run_async())

    else:
        print("Неизвестный режим.")


if __name__ == "__main__":
    main()