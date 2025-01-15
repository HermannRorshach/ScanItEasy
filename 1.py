import asyncio
import sys
from io import StringIO

async def main():
    print("Введите что-то (ожидание 2 секунды):")
    try:
        user_input = await asyncio.wait_for(asyncio.to_thread(input), timeout=2)
    except asyncio.TimeoutError:
        # Сымитируем ввод, чтобы программа получила значение
        sys.stdin = StringIO("значение по умолчанию\n")
        user_input = input()

    print(f"Вы ввели: {user_input}")

    num = input("введи число\n")
    print(num)

asyncio.run(main())
