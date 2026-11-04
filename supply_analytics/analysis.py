import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(
        description="Аналіз поставок препаратів із CSV-файлу"
    )
    parser.add_argument(
        "csv",
        nargs="?",
        default="supplies.csv",
        help="Шлях до CSV-файлу (за замовчуванням: supplies.csv)"
    )
    args = parser.parse_args()

    df = pd.read_csv(args.csv)

    required_columns = {
        "supplier", "category", "quantity", "price_per_unit"
    }
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"У CSV відсутні колонки: {', '.join(sorted(missing))}")

    average_price = np.mean(df["price_per_unit"].to_numpy())
    median_quantity = np.median(df["quantity"].to_numpy())
    std_price = np.std(df["price_per_unit"].to_numpy())  

    df["total_price"] = df["quantity"] * df["price_per_unit"]

    supplier_totals = df.groupby("supplier")["total_price"].sum()
    top_supplier = supplier_totals.idxmax()
    top_supplier_total = supplier_totals.max()

    category_totals = df.groupby("category")["quantity"].sum()
    print("\nСумарна кількість препаратів за категоріями:")
    print(category_totals)

    low_supply = df[df["quantity"] < 100]
    low_supply.to_csv("low_supply.csv", index=False)

    top_three = df.sort_values(
        by="total_price", ascending=False
    ).head(3)

    print("\nТри найбільші поставки за загальною вартістю:")
    print(top_three.to_string(index=False))

    category_totals.plot(kind="bar")
    plt.title("Кількість препаратів за категоріями")
    plt.xlabel("Категорія")
    plt.ylabel("Сумарна кількість")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("quantity_by_category.png")
    plt.close()

    with open("report.txt", "w", encoding="utf-8") as report:
        report.write("ЗВІТ З АНАЛІЗУ ПОСТАВОК ПРЕПАРАТІВ\n")
        report.write("=" * 42 + "\n")
        report.write(f"Середня ціна препаратів: {average_price:.2f}\n")
        report.write(f"Медіана кількості (quantity): {median_quantity:.2f}\n")
        report.write(f"Стандартне відхилення ціни: {std_price:.2f}\n")
        report.write(
            f"Постачальник із найбільшою загальною вартістю поставок: "
            f"{top_supplier} ({top_supplier_total:.2f})\n"
        )
        report.write("Файл із дефіцитними поставками: low_supply.csv\n")
        report.write("\nСумарна кількість за категоріями:\n")
        for category, quantity in category_totals.items():
            report.write(f"- {category}: {quantity}\n")

    print("\nАналіз завершено.")
    print("Створено файли: low_supply.csv, report.txt, quantity_by_category.png")


if __name__ == "__main__":
    main()
