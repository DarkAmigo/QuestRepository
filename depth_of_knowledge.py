from abc import ABC, abstractmethod

class Transport(ABC):
    def __init__(self, name: str, speed: int, capacity: int):
        if not isinstance(name, str):
            raise TypeError("name має бути рядком")

        if not isinstance(speed, int):
            raise TypeError("speed має бути цілим числом")

        if not isinstance(capacity, int):
            raise TypeError("capacity має бути цілим числом")

        self.name = name
        self.speed = speed
        self.capacity = capacity

    @abstractmethod
    def move(self, distance: float) -> float:
        pass

    @abstractmethod
    def fuel_consumption(self, distance: float) -> float:
        pass

    @abstractmethod
    def info(self) -> str:
        pass

    def calculate_cost(self, distance: float, price_per_unit: float) -> float:
        return self.fuel_consumption(distance) * price_per_unit


class Car(Transport):
    def move(self, distance: float) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance: float) -> float:
        return distance * 0.07

    def info(self) -> str:
        return (
            f"Автомобіль: {self.name}, "
            f"час на 100 км: {self.move(100):.2f} год, "
            f"витрати пального: {self.fuel_consumption(100):.2f}"
        )


class Bus(Transport):
    def __init__(self, name: str, speed: int, capacity: int, passengers: int):
        super().__init__(name, speed, capacity)

        if not isinstance(passengers, int):
            raise TypeError("passengers має бути цілим числом")

        self.passengers = passengers

    def move(self, distance: float) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance: float) -> float:
        return distance * 0.15

    def info(self) -> str:
        if self.passengers > self.capacity:
            status = "Перевантажено!"
        else:
            status = "Нормально"

        return (
            f"Автобус: {self.name}, "
            f"час на 100 км: {self.move(100):.2f} год, "
            f"витрати пального: {self.fuel_consumption(100):.2f}, "
            f"пасажири: {self.passengers}/{self.capacity}, "
            f"статус: {status}"
        )


class Bicycle(Transport):
    def __init__(self, name: str, speed: int, capacity: int):
        super().__init__(name, min(speed, 20), capacity)

    def move(self, distance: float) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance: float) -> float:
        return 0.0

    def info(self) -> str:
        return (
            f"Велосипед: {self.name}, "
            f"час на 100 км: {self.move(100):.2f} год, "
            f"витрати пального: {self.fuel_consumption(100):.2f}"
        )


class ElectricCar(Car):
    def battery_usage(self, distance: float) -> float:
        return distance * 0.2

    def fuel_consumption(self, distance: float) -> float:
        return 0.0

    def info(self) -> str:
        return (
            f"Електромобіль: {self.name}, "
            f"час на 100 км: {self.move(100):.2f} год, "
            f"витрати пального: {self.fuel_consumption(100):.2f}, "
            f"витрати батареї: {self.battery_usage(100):.2f}"
        )


def show_transports(transports: list[Transport]) -> None:
    for transport in transports:
        print(transport.info())


transports = [
    Car("Toyota", 100, 5),
    Bus("Mercedes", 80, 50, 45),
    Bus("Ikarus", 60, 40, 45),
    Bicycle("Trek", 25, 1),
    ElectricCar("Tesla", 120, 5)
]


show_transports(transports)

print()
print("Вартість поїздки Toyota:", transports[0].calculate_cost(100, 60))
print("Вартість поїздки Tesla:", transports[4].calculate_cost(100, 60))