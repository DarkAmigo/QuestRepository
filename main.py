
import threading
import random
import time

print_lock = threading.Lock()

class Warehouse:

    def __init__(self, name, meds, price_per_unit):
        self.name = name
        self.meds = meds
        self.initial_meds = meds
        self.price_per_unit = price_per_unit

        self.stolen = 0
        self.lock = threading.Lock()

    def steal(self, amount, use_lock=True, delay=False):

        def operation():

            if self.meds <= 0:
                return 0

            if random.random() < 0.2:
                return 0

            if self.meds < amount:
                return 0

            if delay:
                time.sleep(0.001)

            stolen_amount = random.randint(1, amount)

            self.meds -= stolen_amount
            self.stolen += stolen_amount

            return stolen_amount

        if use_lock:
            with self.lock:
                return operation()

        return operation()

class Runner(threading.Thread):

    def __init__(self, warehouse, name, show_progress=True,
                 use_lock=True, fixed_amount=False):

        super().__init__()

        self.warehouse = warehouse
        self.name = name
        self.show_progress = show_progress
        self.use_lock = use_lock
        self.fixed_amount = fixed_amount

        self.profit = 0
        self.attempts = 10

    def run(self):

        for i in range(self.attempts):

            if self.fixed_amount:
                amount = 30
            else:
                amount = random.randint(10, 30)

            stolen_amount = self.warehouse.steal(
                amount,
                use_lock=self.use_lock,
                delay=not self.use_lock
            )

            self.profit += (
                stolen_amount * self.warehouse.price_per_unit
            )

            if self.show_progress:
                progress = int((i + 1) / self.attempts * 20)
                bar = "█" * progress + "░" * (20 - progress)

                with print_lock:
                    print(
                        f"{self.name:12} "
                        f"[{bar}] {i + 1}/10 "
                        f"| Викрадено: {stolen_amount}"
                    )

            time.sleep(random.uniform(0.1, 0.5))

class Simulation:

    def __init__(self):
        self.warehouses = []
        self.runners = []

    def create_world(self):

        self.warehouses = []
        self.runners = []

        for i in range(5):

            warehouse = Warehouse(
                name=f"Склад-{i + 1}",
                meds=random.randint(100, 300),
                price_per_unit=random.uniform(10, 50)
            )

            self.warehouses.append(warehouse)

        for i in range(5):

            runner = Runner(
                warehouse=self.warehouses[i],
                name=f"Бігунок-{i + 1}"
            )

            self.runners.append(runner)

    def run(self, show_progress=True):

        self.create_world()

        for runner in self.runners:
            runner.show_progress = show_progress

        for runner in self.runners:
            runner.start()

        for runner in self.runners:
            runner.join()

        return self.check_invariants()

    def check_invariants(self):

        total_stolen = 0
        total_profit = 0

        for warehouse in self.warehouses:

            assert warehouse.meds >= 0, (
                f"ПОМИЛКА: {warehouse.name} "
                f"має від'ємну кількість медикаментів!"
            )

            assert warehouse.initial_meds == (
                warehouse.meds + warehouse.stolen
            ), (
                f"ПОМИЛКА: порушено баланс {warehouse.name}!"
            )

            total_stolen += warehouse.stolen

            total_profit += (
                warehouse.stolen * warehouse.price_per_unit
            )

        runners_profit = sum(
            runner.profit for runner in self.runners
        )

        assert abs(total_profit - runners_profit) < 0.000001, (
            "ПОМИЛКА: загальний прибуток не збігається!"
        )

        return {
            "stolen": total_stolen,
            "profit": total_profit
        }

    def show_report(self, results):

        print("\n" + "=" * 55)
        print("             ЗВІТ СИМУЛЯЦІЇ")
        print("=" * 55)

        for warehouse in self.warehouses:

            print(f"\n{warehouse.name}")
            print(f"  Було:       {warehouse.initial_meds}")
            print(f"  Залишилось: {warehouse.meds}")
            print(f"  Викрадено:  {warehouse.stolen}")
            print(
                f"  Прибуток:   "
                f"{warehouse.stolen * warehouse.price_per_unit:.2f}"
            )

        print("\n" + "-" * 55)
        print(f"Загалом викрадено: {results['stolen']}")
        print(f"Загальний прибуток: {results['profit']:.2f}")
        print("Усі інваріанти виконані!")
        print("=" * 55)

def test_100_runs():

    print("\nПеревірка 100 прогонів...\n")

    for i in range(100):

        simulation = Simulation()

        results = simulation.run(show_progress=False)

        print(
            f"\rПрогін: {i + 1}/100 | "
            f"Викрадено: {results['stolen']}",
            end=""
        )

    print("\n\n100 прогонів успішно завершено!")
    print("Жоден інваріант не порушено.")

def test_without_lock():

    print("\n" + "=" * 55)
    print("       ДЕМОНСТРАЦІЯ RACE CONDITION")
    print("=" * 55)

    for run_number in range(1, 101):

        warehouse = Warehouse(
            name="Тестовий склад",
            meds=100,
            price_per_unit=20
        )

        barrier = threading.Barrier(5)

        def unsafe_worker():

            amount = 30

            if warehouse.meds >= amount:

                barrier.wait()

                time.sleep(0.001)

                warehouse.meds -= amount
                warehouse.stolen += amount

        threads = []

        for i in range(5):

            thread = threading.Thread(
                target=unsafe_worker
            )

            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        try:

            assert warehouse.meds >= 0

            assert warehouse.initial_meds == (
                warehouse.meds + warehouse.stolen
            )

        except AssertionError:

            print(f"\nІнваріант порушено на прогоні №{run_number}!")

            print(f"Було: {warehouse.initial_meds}")
            print(f"Залишилось: {warehouse.meds}")
            print(f"Викрадено: {warehouse.stolen}")

            print("\nПричина: декілька потоків одночасно")
            print("пройшли перевірку залишку медикаментів.")

            return

    print("Помилку не вдалося відтворити за 100 прогонів.")


if __name__ == "__main__":

    test_100_runs()

    print("\n\nЗАПУСК ОСНОВНОЇ СИМУЛЯЦІЇ")

    simulation = Simulation()

    results = simulation.run(show_progress=True)

    simulation.show_report(results)

    test_without_lock()
