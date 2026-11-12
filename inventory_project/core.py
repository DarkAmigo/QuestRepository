
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import math


@dataclass
class Item:
    id: int
    name: str
    category: str
    quantity: int
    price: float
    location: str
    created_at: datetime


class ValidationError(ValueError):

    def __init__(self, field, message):
        super().__init__(message)
        self.field = field


def parse_quantity(value: str) -> int:
    try:
        quantity = int(value.strip())
    except (ValueError, AttributeError):
        raise ValidationError(
            "quantity",
            "Кількість повинна бути цілим числом"
        )

    if quantity < 0:
        raise ValidationError(
            "quantity",
            "Кількість не може бути від'ємною"
        )

    return quantity


def parse_price(value: str) -> float:
    try:
        price = float(value.strip().replace(",", "."))
    except (ValueError, AttributeError):
        raise ValidationError(
            "price",
            "Ціна повинна бути числом"
        )

    if not math.isfinite(price) or price < 0:
        raise ValidationError(
            "price",
            "Ціна повинна бути невід'ємним числом"
        )

    return price


def parse_item(form: dict) -> Item:
    name = str(form.get("name", "")).strip()
    category = str(form.get("category", "")).strip()
    location = str(form.get("location", "")).strip()

    if not name:
        raise ValidationError(
            "name",
            "Назва товару не може бути порожньою"
        )

    if not category:
        raise ValidationError(
            "category",
            "Категорія не може бути порожньою"
        )

    if not location:
        raise ValidationError(
            "location",
            "Місце зберігання не може бути порожнім"
        )

    return Item(
        id=0,
        name=name,
        category=category,
        quantity=parse_quantity(
            str(form.get("quantity", ""))
        ),
        price=parse_price(
            str(form.get("price", ""))
        ),
        location=location,
        created_at=datetime.now()
    )


class ItemRepository(ABC):

    @abstractmethod
    def all(self) -> list[Item]:
        pass

    @abstractmethod
    def get(self, item_id: int) -> Item | None:
        pass

    @abstractmethod
    def add(self, item: Item) -> None:
        pass

    @abstractmethod
    def update(self, item: Item) -> None:
        pass

    @abstractmethod
    def remove(self, item_id: int) -> None:
        pass


class InventoryService:

    def __init__(self, repository: ItemRepository):
        self.repository = repository

    def all_items(self) -> list[Item]:
        return self.repository.all()

    def get_item(self, item_id: int) -> Item | None:
        return self.repository.get(item_id)

    def add_item(self, form: dict) -> Item:
        item = parse_item(form)

        existing_items = self.repository.all()

        new_id = max(
            (item.id for item in existing_items),
            default=0
        ) + 1

        item.id = new_id

        self.repository.add(item)

        return item

    def update_item(self, item_id: int, form: dict) -> Item:
        old_item = self.repository.get(item_id)

        if old_item is None:
            raise ValidationError(
                "id",
                "Товар не знайдено"
            )

        updated_item = parse_item(form)

        updated_item.id = old_item.id
        updated_item.created_at = old_item.created_at

        self.repository.update(updated_item)

        return updated_item

    def delete_item(self, item_id: int) -> None:
        item = self.repository.get(item_id)

        if item is None:
            raise ValidationError(
                "id",
                "Товар не знайдено"
            )

        self.repository.remove(item_id)

    def search_items(self, text: str) -> list[Item]:
        query = text.strip().lower()

        items = self.repository.all()

        if not query:
            return items

        return [
            item
            for item in items
            if query in item.name.lower()
            or query in item.category.lower()
        ]
