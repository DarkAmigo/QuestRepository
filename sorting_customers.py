clients = [
    {
        "name": "Іван",
        "amount": 50,
        "status": "clean"
    },
    {
        "name": "Олег",
        "amount": 500.5,
        "status": "suspicious"
    },
    {
        "name": "Анна",
        "amount": 1500,
        "status": "fraud"
    }
]

for client in clients:
    name = client["name"]
    amount = client["amount"]
    status = client["status"]

    if not isinstance(amount, (int, float)):
        print(f"{name}: Фальшиві дані")
        continue

    if amount < 100:
        amount_category = "Дрібнота"
    elif amount <= 999:
        amount_category = "Середнячок"
    else:
        amount_category = "Великий клієнт"

    match status:
        case "clean":
            decision = "Працювати без питань"
        case "suspicious":
            decision = "Перевірити документи"
        case "fraud":
            decision = "У чорний список"
        case _:
            decision = "Невідомий статус"

    print(f"{name}: {amount_category}, {decision}")