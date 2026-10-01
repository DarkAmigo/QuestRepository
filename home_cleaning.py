class JunkItem:
    def __init__(self, name: str, quantity: int, value: float):
        self.name = name
        self.quantity = quantity
        self.value = value

    def __str__(self):
        return f"{self.name}: кількість={self.quantity}, ціна={self.value}"


class StorageBackend:
    def save(self, items: list[JunkItem]):
        raise NotImplementedError

    def load(self) -> list[JunkItem]:
        raise NotImplementedError


class JunkStorage(StorageBackend):

    def __init__(self, filename: str):
        self.filename = filename

    def serialize(self, items: list[JunkItem], filename: str):
        with open(filename, "w", encoding="utf-8") as file:
            for item in items:
                value = str(item.value).replace(".", ",")

                file.write(f"{item.name}|{item.quantity}|{value}\n")

    def parse(self, filename: str) -> list[JunkItem]:
        items = []

        with open(filename, "r", encoding="utf-8") as file:

            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                parts = line.split("|")

                if len(parts) != 3:
                    print(
                        f"УВАГА: рядок {line_number} пропущено — "
                        f"має бути 3 поля."
                    )
                    continue

                name = parts[0]
                quantity_text = parts[1]
                value_text = parts[2]

                try:
                    quantity = int(quantity_text)
                except ValueError:
                    print(
                        f"УВАГА: рядок {line_number} пропущено — "
                        f"кількість не є цілим числом."
                    )
                    continue

                try:
                    value = float(value_text.replace(",", "."))
                except ValueError:
                    print(
                        f"УВАГА: рядок {line_number} пропущено — "
                        f"ціна не є числом."
                    )
                    continue

                item = JunkItem(name, quantity, value)
                items.append(item)

        return items


    def save(self, items: list[JunkItem]):
        self.serialize(items, self.filename)

    def load(self) -> list[JunkItem]:
        try:
            return self.parse(self.filename)
        except FileNotFoundError:
            return []


class JunkRepository:
    def add(self, item: JunkItem):
        raise NotImplementedError

    def get(self, name: str):
        raise NotImplementedError

    def find(self, text: str):
        raise NotImplementedError

    def list_all(self) -> list[JunkItem]:
        raise NotImplementedError


class FileJunkRepository(JunkRepository):

    def __init__(self, storage: StorageBackend):
        self.storage = storage

        self.items = self.storage.load()

    def add(self, item: JunkItem):
        self.items.append(item)
        self.storage.save(self.items)

    def get(self, name: str):
        for item in self.items:
            if item.name == name:
                return item

        return None

    def find(self, text: str):
        result = []

        for item in self.items:
            if text.lower() in item.name.lower():
                result.append(item)

        return result

    def list_all(self) -> list[JunkItem]:
        return self.items.copy()


items = [
    JunkItem("Бляшанка", 5, 2.5),
    JunkItem("Стара плата", 3, 7.8),
    JunkItem("Купка дротів", 10, 1.2)
]

filename = "junk.txt"

storage = JunkStorage(filename)

storage.serialize(items, filename)

print("Предмети записано у файл.\n")


loaded_items = storage.parse(filename)

print("Прочитано з файлу:")

for item in loaded_items:
    print(item)


print("\nПеревірка:")

if (
    loaded_items[0].name == "Бляшанка"
    and loaded_items[0].quantity == 5
    and loaded_items[0].value == 2.5
):
    print("✓ Бляшанка прочитана правильно")

if (
    loaded_items[1].name == "Стара плата"
    and loaded_items[1].quantity == 3
    and loaded_items[1].value == 7.8
):
    print("✓ Стара плата прочитана правильно")

if (
    loaded_items[2].name == "Купка дротів"
    and loaded_items[2].quantity == 10
    and loaded_items[2].value == 1.2
):
    print("✓ Купка дротів прочитана правильно")


repository = FileJunkRepository(storage)

repository.add(
    JunkItem("Старий монітор", 2, 15.5)
)

print("\nВесь склад:")

for item in repository.list_all():
    print(item)


print("\nПошук 'Стара плата':")

item = repository.get("Стара плата")

if item is not None:
    print(item)
else:
    print("Предмет не знайдено")


print("\nПошук за словом 'дрот':")

found_items = repository.find("дрот")

for item in found_items:
    print(item)