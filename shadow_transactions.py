
from functools import wraps

WARNING = "Тіньовий ліміт перевищено. Активую схему"

def parse_transaction(line):
    if not isinstance(line, str):
        return None

    parts = line.split()

    if len(parts) != 2:
        return None

    try:
        return float(parts[1])
    except ValueError:
        return None


def shadow(limit=200):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            total = 0.0
            warning_shown = False

            for line in func(*args, **kwargs):
                amount = parse_transaction(line)

                if amount is not None:
                    total += amount

                    if total > limit and not warning_shown:
                        print(WARNING)
                        warning_shown = True

                yield line

            return total

        return wrapper
    return decorator


def suspicious_counter(threshold=100, limit=200):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            total = 0.0
            overflow_total = 0.0
            warning_shown = False

            source = func(*args, **kwargs)

            while True:
                try:
                    line = next(source)
                except StopIteration as stop:
                    return stop.value

                amount = parse_transaction(line)

                if amount is not None:
                    previous_total = total
                    total += amount

                    if total > limit:
                        overflow_total += amount

                        if (
                            overflow_total > threshold
                            and not warning_shown
                        ):
                            print(
                                "Підозрілий ліміт перевищено! "
                                f"Сума: {overflow_total:g}"
                            )
                            warning_shown = True

                yield line

        return wrapper
    return decorator


@suspicious_counter(threshold=100, limit=200)
@shadow(limit=200)
def transactions():
    yield "payment 120"
    yield "refund 50"
    yield "transfer 300"
    yield "payment nope"
    yield "malformed"
    yield "payment 40"


def consume(generator):
    while True:
        try:
            item = next(generator)
        except StopIteration as stop:
            return stop.value

        print("Транзакція:", item)


if __name__ == "__main__":
    final_sum = consume(transactions())
    print(f"Фінальна сума: {final_sum:g}")
