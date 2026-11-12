
import csv
import math

from pathlib import Path
from datetime import datetime

from core import Item, ItemRepository


class CsvItemRepository(ItemRepository):

    HEADERS = [
        "id",
        "name",
        "category",
        "quantity",
        "price",
        "location",
        "created_at"
    ]

    def __init__(self, path=None):
        self._path = Path(path) if path else None
        self._items = {}

        if self._path and self._path.exists():
            if self._path.stat().st_size > 0:
                self.load(self._path)
            else:
                self.save(self._path)

    def all(self) -> list[Item]:
        return list(self._items.values())

    def get(self, item_id: int) -> Item | None:
        return self._items.get(item_id)

    def add(self, item: Item) -> None:
        if item.id in self._items:
            raise ValueError(
                f"Товар з ID {item.id} вже існує"
            )

        self._items[item.id] = item

    def update(self, item: Item) -> None:
        if item.id not in self._items:
            raise ValueError(
                f"Товар з ID {item.id} не знайдено"
            )

        self._items[item.id] = item

    def remove(self, item_id: int) -> None:
        if item_id not in self._items:
            raise ValueError(
                f"Товар з ID {item_id} не знайдено"
            )

        del self._items[item_id]

    def load(self, path=None) -> None:
        file_path = Path(path) if path else self._path

        if file_path is None:
            raise ValueError(
                "Не вказано шлях до CSV-файлу"
            )

        if not file_path.exists():
            raise FileNotFoundError(
                f"Файл не знайдено: {file_path}"
            )

        loaded_items = {}

        with file_path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            if reader.fieldnames != self.HEADERS:
                raise ValueError(
                    "Неправильний формат CSV-файлу"
                )

            for row in reader:
                item = Item(
                    id=int(row["id"]),
                    name=row["name"],
                    category=row["category"],
                    quantity=int(row["quantity"]),
                    price=float(row["price"]),
                    location=row["location"],
                    created_at=datetime.fromisoformat(
                        row["created_at"]
                    )
                )

                if item.id <= 0:
                    raise ValueError("ID повинен бути додатним")

                if item.id in loaded_items:
                    raise ValueError(
                        f"Повторюється ID: {item.id}"
                    )

                if not item.name.strip():
                    raise ValueError("Назва товару порожня")

                if not item.category.strip():
                    raise ValueError("Категорія порожня")

                if not item.location.strip():
                    raise ValueError("Місце зберігання порожнє")

                if item.quantity < 0:
                    raise ValueError("Некоректна кількість")

                if item.price < 0 or not math.isfinite(item.price):
                    raise ValueError("Некоректна ціна")

                loaded_items[item.id] = item

        self._items = loaded_items
        self._path = file_path

    def save(self, path=None) -> None:
        file_path = Path(path) if path else self._path

        if file_path is None:
            raise ValueError(
                "Не вказано шлях для збереження"
            )

        with file_path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.HEADERS
            )

            writer.writeheader()

            for item in self.all():
                writer.writerow({
                    "id": item.id,
                    "name": item.name,
                    "category": item.category,
                    "quantity": item.quantity,
                    "price": item.price,
                    "location": item.location,
                    "created_at": item.created_at.isoformat()
                })

        self._path = file_path
