from models import Antibiotic, Vitamin, Vaccine, Medicine


def show_medicines(medicines: list[Medicine]) -> None:
    for medicine in medicines:
        print(medicine.info())
        print("-" * 50)


medicines = [
    Antibiotic("Амоксицилін", 10, 25.0),
    Vitamin("Вітамін C", 20, 12.5),
    Vaccine("Вакцина X", 5, 100.0)
]

show_medicines(medicines)