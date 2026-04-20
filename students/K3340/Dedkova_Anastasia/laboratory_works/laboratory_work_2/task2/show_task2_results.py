import csv

RESULTS_FILE = "task2_results.csv"


def main():
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                print(" | ".join(row))
    except FileNotFoundError:
        print("Файл с результатами пока не создан.")


if __name__ == "__main__":
    main()
