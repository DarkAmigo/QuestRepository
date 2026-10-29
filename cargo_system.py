from abc import ABC, abstractmethod
from typing import List, Optional
import os

class Cargo(ABC):
    def __init__(self, batch: str, name: str, qty: int, weight_kg: float, sector: str, status: str):
        self.batch = batch
        self.name = name
        self.qty = qty
        self.weight_kg = weight_kg
        self.sector = sector.strip()
        self.status = status.strip().lower()

    @abstractmethod
    def label(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(batch={self.batch}, name='{self.name}', qty={self.qty}, weight={self.weight_kg}kg, sector={self.sector}, status={self.status})"


class Antibiotic(Cargo):
    def label(self) -> str:
        return " [АНТИБІОТИК] Температурний режим: +2...+8°C"


class Vitamin(Cargo):
    def label(self) -> str:
        return " [ВІТАМІН] Захищати від прямих сонячних променів"


class Vaccine(Cargo):
    def label(self) -> str:
        return " [ВАКЦИНА] Терміново! Холодовий ланцюг!"


class UnknownCargo(Cargo):
    def label(self) -> str:
        return " [НЕВІДОМИЙ ВАНТАЖ] Потребує ручної перевірки"


class StorageRepository(ABC):
    @abstractmethod
    def all(self) -> List[Cargo]:
        pass

    @abstractmethod
    def get(self, batch: str) -> Optional[Cargo]:
        pass

    @abstractmethod
    def by_sector(self, sector: str) -> List[Cargo]:
        pass


class FileStorageRepository(StorageRepository):
    def __init__(self, filepath: str):
        self._cargoes: List[Cargo] = []
        self._load_from_file(filepath)

    def _load_from_file(self, filepath: str):
        if not os.path.exists(filepath):
            print(f"[-] Попередження: Файл {filepath} не знайдено.")
            return

        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        if not lines:
            return

        for idx, line in enumerate(lines[1:], start=2):
            line = line.strip()
            if not line:
                continue

            parts = [p.strip() for p in line.split('|')]
            
            if len(parts) < 7:
                print(f"[!] Попередження (рядок {idx}): Замало полів ({len(parts)}). Рядок пропущено: '{line}'")
                continue

            batch = parts[0]
            sector = parts[-2]
            status = parts[-1]
            qty_str = parts[-4]
            weight_str = parts[-3]
            name = "|".join(parts[1:-5])
            category = parts[-5]

            try:
                qty = int(qty_str)
                weight_kg = float(weight_str.replace(',', '.'))
            except ValueError:
                print(f"[!] Попередження (рядок {idx}): Неможливо конвертувати кількість або вагу ('{qty_str}', '{weight_str}'). Рядок пропущено.")
                continue

            cat_lower = category.lower()
            
            if "антибіотик" in cat_lower or "antibiotic" in cat_lower:
                cargo = Antibiotic(batch, name, qty, weight_kg, sector, status)
            elif "вітамін" in cat_lower or "vitamin" in cat_lower:
                cargo = Vitamin(batch, name, qty, weight_kg, sector, status)
            elif "вакцина" in cat_lower or "vaccine" in cat_lower:
                cargo = Vaccine(batch, name, qty, weight_kg, sector, status)
            else:
                cargo = UnknownCargo(batch, name, qty, weight_kg, sector, status)

            self._cargoes.append(cargo)

    def all(self) -> List[Cargo]:
        return self._cargoes

    def get(self, batch: str) -> Optional[Cargo]:
        for cargo in self._cargoes:
            if cargo.batch == batch:
                return cargo
        return None

    def by_sector(self, sector: str) -> List[Cargo]:
        return [c for c in self._cargoes if c.sector.upper() == sector.upper()]


class InMemoryStorageRepository(StorageRepository):
    def __init__(self, initial_cargoes: List[Cargo] = None):
        self._cargoes = initial_cargoes or []

    def all(self) -> List[Cargo]:
        return self._cargoes

    def get(self, batch: str) -> Optional[Cargo]:
        for cargo in self._cargoes:
            if cargo.batch == batch:
                return cargo
        return None

    def by_sector(self, sector: str) -> List[Cargo]:
        return [c for c in self._cargoes if c.sector.upper() == sector.upper()]

def generate_burned_sector_c_report(storage: StorageRepository):
    print("\n" + "="*50)
    print(" ЗВІТ: Партії в секторі C, записані як «згоріло»")
    print("="*50)

    sector_c_cargoes = storage.by_sector("C")
    
    burned_in_c = [c for c in sector_c_cargoes if "згоріл" in c.status or "згор" in c.status]

    total_weight = 0.0

    if not burned_in_c:
        print("У секторі C не знайдено партій зі статусом «згоріло».")
    else:
        for idx, cargo in enumerate(burned_in_c, 1):
            print(f"{idx}. Партія: {cargo.batch} | Категорія: {cargo.__class__.__name__} | Вага: {cargo.weight_kg} кг | Статус: {cargo.status}")
            total_weight += cargo.weight_kg

    print("-" * 50)
    print(f" Загальна кількість таких партій: {len(burned_in_c)}")
    print(f" Сумарна вага: {total_weight:.1f} кг")
    print("="*50 + "\n")


if __name__ == "__main__":
    filename = "inventory_recovered.txt"

    print("[+] Читання файлу із сервера/диска...")
    file_storage = FileStorageRepository(filename)

    generate_burned_sector_c_report(file_storage)

    print("[+] Запуск додаткового тесту для In-Memory сховища (без файлу)...")
    
    mem_cargoes = [
        Vaccine("TEST-01", "TestVac", 100, 10.5, "C", "згоріло"),
        UnknownCargo("TEST-02", "UnknownItem", 50, 5.0, "C", "згоріло"),
        Antibiotic("TEST-03", "SafeMed", 200, 15.0, "A", "ціле")
    ]
    
    mem_storage = InMemoryStorageRepository(mem_cargoes)
    
    assert len(mem_storage.all()) == 3
    assert mem_storage.get("TEST-01") is not None
    
    generate_burned_sector_c_report(mem_storage)
    print("[+] Плюс-тест успішно пройдено!")