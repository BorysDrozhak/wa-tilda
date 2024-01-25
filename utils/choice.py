import random
from datetime import datetime

from .weather_cli import kyiv_timezone



def parse_order(text):
    smile = random.choice(['🥰', '😇', '😊', '🙇‍♂️', '🤩', '😎', '😉', '🙂', '🥳', ])
    delivery_smile = random.choice(['🙇‍♂️', '🚀'])
    client_name, client_address = None, None
    result_order_block_for_client = ''
    total_order_price = None
    self_delivery = False
    paid = None
    order_block = False

    for line in text.split("\n"):
        if 'Нове Навинос' in line:
            self_delivery = True
            continue
        elif 'Нове Доставка' in line:
            continue

        if not line:
            continue

        if 'Замовлення' in line:
            order_block = True
            continue

        if '🤑🤑🤑Чайові' in line:
            order_block = False
        elif 'Всього' in line:
            order_block = False

        if order_block:
            result_order_block_for_client += f'\n{line}' if 'X' in line else line
            continue

        if 'Всього' in line:
            total_order_price = parse_line(line, ":")
        if 'Адреса клієнта' in line:
            client_address = parse_line(line, ":")
        if 'Клієнт' in line:
            end_index = line.find("(")
            client_name = line[:end_index].strip()
            client_name = parse_line(client_name, ":")

        if '☝️ Спосіб оплати: Онлайн оплата' in line:
            paid = 'Оплачено'
            continue

    if self_delivery:
        about_delivery_block = ''
    else:
        about_delivery_block = '(включно з доставкою 🙇‍♂️)'

    greeting = greetings(client_name)
    parsed_text_for_client = f"""
{greeting} {smile}
Ми підтверджуємо ваше замовлення на сайті, або ж Команда WA уже розпочала приготування вашого замовлення

{result_order_block_for_client}

🏡 Доставка за адресом: {client_address or ''}
💰 Разом: {total_order_price} {about_delivery_block} {paid or 'Оплата готівкою'}

Дякуємо вам за замовлення!{smile}
Орієнтовний час приготування та доставки 40-80 хвилин 🧭
Обов'язково повідомимо як кур'єр вирушить від нас {delivery_smile}
"""

    return parsed_text_for_client


def parse_line(line, separator):
    start_index = line.find(separator) + 1
    parsed_line = line[start_index:].strip()
    return parsed_line


def greetings(client_name):
    current_hours = datetime.now(tz=kyiv_timezone).hour
    return (
        f"Доброго ранку, {client_name}"
        if 5 <= current_hours <= 11
        else f"Доброго дня, {client_name}"
        if 12 <= current_hours <= 17
        else f"Доброго вечора, {client_name}"
        if 18 <= current_hours <= 23
        else f"Доброї ночі, {client_name}"
    )
