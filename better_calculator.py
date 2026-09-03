expression = input("Введіть вираз: ")

position = 0


def skip_spaces():
    global position

    while position < len(expression) and expression[position] == " ":
        position += 1


def parse_number():
    global position

    skip_spaces()

    start = position

    while position < len(expression) and (
        expression[position].isdigit() or expression[position] == "."
    ):
        position += 1

    if start == position:
        raise ValueError("Очікувалося число")

    return float(expression[start:position])


def parse_factor():
    global position

    skip_spaces()

    if position < len(expression) and expression[position] == "(":
        position += 1

        result = parse_expression()

        skip_spaces()

        if position >= len(expression) or expression[position] != ")":
            raise ValueError("Не вистачає закриваючої дужки")

        position += 1

        return result

    return parse_number()


def parse_term():
    global position

    result = parse_factor()

    while True:
        skip_spaces()

        if position >= len(expression):
            break

        operation = expression[position]

        if operation != "*" and operation != "/":
            break

        position += 1

        second = parse_factor()

        if operation == "*":
            result *= second

        elif operation == "/":
            if second == 0:
                raise ValueError("Ділення на нуль")

            result /= second

    return result


def parse_expression():
    global position

    result = parse_term()

    while True:
        skip_spaces()

        if position >= len(expression):
            break

        operation = expression[position]

        if operation != "+" and operation != "-":
            break

        position += 1

        second = parse_term()

        if operation == "+":
            result += second

        elif operation == "-":
            result -= second

    return result


try:
    result = parse_expression()

    skip_spaces()

    if position != len(expression):
        raise ValueError("Некоректний вираз")

    print("Результат:", result)

except ValueError as error:
    print("Помилка:", error)