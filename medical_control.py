medicines = [
    {
        "name": "Амоксицилін",
        "quantity": 20,
        "category": "antibiotic",
        "temperature": 20.0
    },
    {
        "name": "Вітамін C",
        "quantity": 50,
        "category": "vitamin",
        "temperature": 27.0
    },
    {
        "name": "Вакцина",
        "quantity": 10,
        "category": "vaccine",
        "temperature": 3.0
    }
]

for medicine in medicines:
    name = medicine["name"]
    quantity = medicine["quantity"]
    category = medicine["category"]
    temperature = medicine["temperature"]

    if not isinstance(quantity, int) or not isinstance(temperature, float):
        print(name, "- Помилка даних")
        continue

    if temperature < 5:
        temperature_status = "Надто холодно"
    elif temperature > 25:
        temperature_status = "Надто жарко"
    else:
        temperature_status = "Норма"

    match category:
        case "antibiotic":
            category_status = "Рецептурний препарат"
        case "vitamin":
            category_status = "Вільний продаж"
        case "vaccine":
            category_status = "Потребує спецзберігання"
        case _:
            category_status = "Невідома категорія"

    print(f"{name}: {category_status}, {temperature_status}")