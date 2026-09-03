num1 = float(input("Введіть перше число: "))
operation = input("Введіть операцію (+, -, *, /): ")
num2 = float(input("Введіть друге число: "))

if operation == "+":
    result = num1 + num2

elif operation == "-":
    result = num1 - num2

elif operation == "*":
    result = num1 * num2

elif operation == "/":
    if num2 == 0:
        print("Помилка: на нуль ділити не можна!")
        result = None
    else:
        result = num1 / num2

else:
    print("Помилка: невідома операція!")
    result = None

if result is not None:
    print("Результат:", result)