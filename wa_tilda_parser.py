import re
import sys

while True:
    print("Enter/Paste your content. Ctrl-D or Ctrl-Z ( windows ) to save it.")
    try:
        text = ''.join(sys.stdin.readlines())
    except EOFError:
        break

    # cleaning up before parsing the new input
    client_nocall, client_address = None, None
    client_name, client_phone = None, None
    delivery_zone, total_order_price, order_type = None, None, None
    client_comment, persons, client_no_need = None, None, None
    result_order_block, other = None, None

    order_block = text.split("Данные плательщика:")[0]
    client_block = (
        text
        .split("Данные плательщика:")[1]
        .split("Дополнительные данные")[0]
    )

    print('----')
    other = []
    for line in client_block.split("\n"):
        if not line:
            continue
        param = line.split(":")[0]
        info = line.split(":")[1][1:]
        if param == 'Name':
            client_name = info
        elif param == 'Address':
            client_address = info
        elif param == 'Phone':
            client_phone = (
                info
                .replace(' ', '')
                .replace('(', '')
                .replace(')', '')
                .replace('-', '')
            )
        elif param == 'не_треба':
            client_no_need = info
        elif param == 'Persons':
            persons = "For: " + info
        elif param == 'Comment':
            client_comment = "Comment: " + info
        elif param == 'НЕдзвонити-НАПИСАТИ':
            if info == 'yes':
                client_nocall = 'NO CALL'
            else:
                client_nocall = 'Please CALL the Client!'
        else:
            other += line
    if not other:
        other = ''


    result_order_block = ''
    for line in order_block.split("\n"):
        order = re.findall(r"(\d+\.) (.+)", line)
        if "Курʼєром " in line or "Самовивiз" in line:
            delivery_zone = line
            continue
        elif "Сумма оплаты" in line:
            total_order_price = line.split(": ")[1]
            continue
        elif "Платежная система" in line or "Код платежа" in line:
            order_type = ' '.join(line.split(": ")[1:])
            continue
        elif not order or len(order[0]) != 2:
            continue
        order = order[0][1]
        name, info = order.split(": ")[0], ": ".join(order.split(": ")[1:])
        price_block = re.findall(r"(\d+) \((\d+) x (\d+)\)(.*)", info)
        if not price_block:
            continue
        price_block = price_block[0]
        total_price = price_block[0]
        amount = price_block[1]
        dish_price = price_block[2]
        if len(price_block) >= 4:
            options = price_block[3]
        else:
            options = ''

        if name == 'Моті':
            name = name + " " + options.split(": ")[1]
            options = False
        elif "Розмір порції: Одинарні ( 1 шт в японській упаковці)" in options:
            name = name + " (Одинарна упаковка)"
        result_order_block += amount + " x " + name + "\t - (" + total_price + " uah)" + "\n"
        if options:
            for option in options.split(","):
                if option.strip() in [
                    "Бажаєте більше тунця (+30г)?: Ні",
                    "Хотілось би більше рису (100г)?: Ні",
                    "Пікантне?: Так",
                    "Посипати кунжутом?: Так",
                    "Бажаєте більше лосося (+30 г) ?: Ні",
                    "Безлактозний йогурт?: Ні",
                    "Більше перепелиних яєць (+2 шт)?: Ні",
                    "Розмір порції: Одинарні ( 1 шт в японській упаковці)",
                    "Поливати горіховим соусом?: Так",
                    "Бажаєте більше курячого філе (+70г)?: Ні",
                    "Потрібні імбир та васабі?: Так"
                ]:
                    continue
                result_order_block += "    " + option + "\n"

    print('-' * 100)
    print(client_nocall)
    print(client_name, client_phone)
    if "Самовивiз" in delivery_zone:
        print("Самовивіз!")
    else:
        print(client_address)
        print(delivery_zone)
    print()
    print(total_order_price, order_type)
    print()
    print(persons)
    if client_comment:
        print(client_comment)
    if client_no_need:
        print(client_no_need)
    print(other)
    print('----')
    print(result_order_block)
    print('-' * 50)
    print('-' * 50)
