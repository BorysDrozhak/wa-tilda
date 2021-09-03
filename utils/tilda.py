# -*- coding: utf-8 -*-

import re

# якщо треба щоб щось не показувало - то додай це сюди (повною стрічкою)
ignore_options = [
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
                    "Потрібні імбир та васабі?: Так",
                    "Потрібні імбир та васабі до онігірі?: Так",
                    "Бажаєте додати до боулу броколі(30г) чи більше лосося(30г)?: Ні",
                    "дякую",
                    "Розмір порції: Standard",
                    "Розмір порції: XS (protein balanced)",
                    "Любиш соєвий соус до гречки?: Ні",
                    "Любиш імбир та васабі до гречки?: Ні",
                    "Бажаєте більше лосося(30г) чи броколі(30г)?: Ні",
                    "Ф'южн опціі: Standard",
                    "Розмір порції: XL СЕТ (3 шт в крафтовому боксі з авторським салатом)",
    ]

# якщо хочеш переімінувати опцію на лєту - використовуй цей лист
substitute_list = [
    (
        "Бажаєте більше лосося(30г) чи броколі(30г)?: Лосось і броколі",
        "+ Лосось(30г) + Броколі(30г)"
        ),
    ('Бажаєте більше тунця (+30г)?: Так', "+ Тунця (+30г)"),
    ("Потрібні імбир та васабі?: Ні", "- Не потрібен: Імбир та васабі"),
    (
        "Бажаєте додати до боулу броколі(30г) чи більше лосося(30г)?: Лосось і броколі",
        "+ Лосось(30г) + Броколі(30г)"
    ),
    ("Бажаєте більше курячого філе (+70г)?: Так", "+ Курячого філе (+70г)"),
    ("Бажаєте додати до боулу броколі(30г) чи більше лосося(30г)?: Броколі (+30г)", "+ Броколі (+30г)"),
    ("Бажаєте додати до боулу броколі(30г) чи більше лосося(30г)?: Лосось (+30г)", "+ Лосось (+30г)"),
    ("Бажаєте більше лосося(30г) чи броколі(30г)?: Лосось (+30г)", "+ Лосось (+30г)"),
    ("Бажаєте більше лосося(30г) чи броколі(30г)?: Броколі (+30г)", "+ Броколі (+30г)"),
    ("Начинка: Cheesy black вугор під соусом Унагі", "- Cheesy black вугор під соусом Унагі"),
    ("Начинка: Класичний японський онігірі з тунцем під стружкою Боніто", "- Класичний японський онігірі з тунцем під стружкою Боніто"),
    ("Начинка: Кріспі & plant-based", "- Кріспі & plant-based"),
]




def parse_order(text):
    # cleaning up before parsing the new input
    client_nocall, client_address = None, ''
    client_name, client_phone = None, None
    delivery_zone, total_order_price, order_type = None, None, None
    client_comment, persons, client_no_need = None, None, None
    result_order_block, other, utm = None, None, None
    do_not_know_zones, self_delivery = False, False
    promocode = None

    order_block = text.split("Данные плательщика:")[0]
    add_block = text.split("Дополнительные данные:")
    if len(add_block) > 1:
        add_block = add_block[1]
    ## utm
    for line in add_block.split('\n'):
        if "UTM source:" in line:
            utm = line
            break
    if utm:
        utm = f'----\n{utm}'
    else:
        utm = ''

    client_block = (
        text
        .split("Данные плательщика:")[1]
        .split("Дополнительные данные")[0]
    )

    other = []
    no_need_bool = False
    for line in client_block.split("\n"):
        if not line:
            continue
        param = line.split(":")[0]
        if client_comment and len(line.split(":")) < 2 and no_need_bool is False:
            # in case comment is on a next line, add it to the comment, until next param happen
            client_comment = client_comment + '\n' + line
            continue

        info = line.split(":")[1].lstrip()
        if param == 'Name' or param == 'name':
            client_name = info
        elif param == 'Address' or param == 'addr' or param == "Адрес доставки":
            client_address = info
        elif param == 'Промокод':
            promocode = info
        elif param == 'Phone' or param == 'phone':
            client_phone = (
                info
                .replace(' ', '')
                .replace('(', '')
                .replace(')', '')
                .replace('-', '')
            )
        elif param == 'не_треба':
            client_no_need = info
            no_need_bool = True
        elif param == 'Persons' or param == 'persons':
            persons = "Для: " + info
        elif param == 'Комент:' or param == 'Comment' or param == 'comment':
            client_comment = "Comment: " + info
        elif param == 'НЕдзвонити-НАПИСАТИ':
            if info == 'yes':
                client_nocall = 'NO CALL'
        else:
            other += line
    if not other:
        other = ''
    if not client_nocall:
        client_nocall = 'Треба дзвонити клієнту!'

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
        elif 'Промокод' in line:
            promocode = line.split(": ")[1]
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
            name = options.split(": ")[1] + " " + name
            options = False
        elif "Розмір порції: Одинарні ( 1 шт в японській упаковці)" in options:
            name = name + " (Одинарна упаковка)"
        elif "Розмір порції: XL СЕТ (3 шт в крафтовому боксі з авторським салатом)" in options:
            name = name + " (XL СЕТ 3 шт)"
        elif "Розмір порції: XS (protein balanced)" in options:
            name = name + " (XS protein balanced)"
        result_order_block += amount + " x " + name + " - (" + total_price + " uah)" + "\n"
        if options:
            for option in options.split(","):
                if option.strip() in ignore_options:
                    continue
                elif 'Оберіть Лассі: Індійське Лассі "Манго" безлактозне' in option.strip():
                    option = option.split(":")[1]
                elif 'Оберіть Сет Онігірь: Green Juicy Salmon' in option.strip():
                    option = option.split(":")[1]
                elif 'Бажаєте додати до боулу броколі(30г) чи більше лосося(30г)?: Лосось (+30г)' in option.strip():
                    option = option.split(":")[1]

                for item in substitute_list:
                    if item[0] == option.strip():
                        option = item[1]
                result_order_block += "     " + option + "\n"

    # note to admin about address zone. type of address delivery
    if delivery_zone and "Курʼєром не орієнтуюсь яка зона" in delivery_zone:
        address_note = "Не орієнтуються яка зона!\n"
        do_not_know_zones = True
    elif delivery_zone and "Самовивiз" in delivery_zone:
        address_note = "Самовивіз!\n"
        self_delivery = True
    else:
        address_note = ''

    ## comment info
    if not client_comment:
        client_comment = ''
    else:
        client_comment += '\n'
    if not client_no_need:
        client_no_need = ''
    else:
        client_no_need += '\n'

    if not promocode:
        promocode = ''
    else:
        promocode = f'\nPROMOCODE: {promocode} (10%)'


    ### smart parsing
    # extra = ""
    if "0682582930" in client_phone or "0982454975" in client_phone:
        if 'кульпарків' in client_address or 'Кульпарк' in client_address:
            client_address = "Кульпарківська 226Б (Місто Трав), Перший домофон 3#36, другий ліворуч 36, другий поверх"


    parsed_text = f"""{client_nocall}
{address_note}

{client_name} {client_phone}
{address_block(self_delivery, do_not_know_zones, delivery_zone, client_address)}
{total_order_price}  ({order_type})
{persons}
{client_comment}{client_no_need}
{other}
----
{result_order_block}
{billing_info(order_type, total_order_price)}
{utm}
{url(self_delivery, client_address)}{promocode}"""

    return parsed_text


def address_block(self_delivery, do_not_know_zones, delivery_zone, client_address):
    ## address block with info where to deliver
    # вул.С.Петлюри 17/16
    # or nothing if self delivery
    if not self_delivery and not do_not_know_zones and not delivery_zone:
        return client_address + "\n"
    elif not self_delivery and not do_not_know_zones and delivery_zone:
            return client_address + "\n" + delivery_zone
    elif not self_delivery:
        return client_address
    else:
        return ''


def billing_info(order_type, total_order_price):
    ## billing info
    if "LiqPay" in order_type:
        return f"Разом: {total_order_price}  (Оплачено)"
    else:
        return f"Разом: {total_order_price}  ({order_type})"


def url(self_delivery, client_address):
     ## URL to google maps
    if self_delivery:
        return ''
    else:
        # форматнути щоб url працювало
        client_address_fmt = (
            client_address
            .replace(" ", "+")
            .replace('/', '+')
            .replace("'", '+')
            .replace("‘", '')
            .replace("’", '')
            .replace('"', '')
        )
        # забрати зайву інфу від адреси
        client_address_fmt = client_address_fmt.split(',')[0]
        client_address_fmt = client_address_fmt.split('під')[0]
        client_address_fmt = client_address_fmt.split('буд')[0]
        client_address_fmt = client_address_fmt.split('кв')[0]

        return (
            f"https://www.google.com/maps/dir/Kniazia+Romana+St,+7,+Lviv,+Lviv+Oblast/"
            f"{client_address_fmt}"
            "+L'viv,+L'vivs'ka+oblast,+79000"
        )
