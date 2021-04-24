import getpass
import logging
import re
import time
import traceback

from telegram.ext import (CommandHandler, Filters, MessageFilter,
                          MessageHandler, Updater)

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


b = "AAFiYwWlbJwvUhbwV"
c = "Zgu_caRA7oHMIp67a8"  # do not even ask why. it is gonna be used by mere people on windows man
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
a = "165506622"
tok = a + "2" + ':' + b + c

d = "1700108054:A"
f = "AFsN_Agk1G5eyh19Dxqdn_jrPmuW60Zy5"
b_bot = d + f + "4"

if getpass.getuser() == "bdrozhak":
    tok = b_bot

updater = Updater(token=tok, use_context=True)
dispatcher = updater.dispatcher


def send_parsed_order(update, context):
    chat_id = update.effective_chat.id
    print("chart_id: " + str(chat_id))
    err = ''
    try:
        text = parse_order(update.message.text)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + '\n\n Borys will have a look ;)'
    if str(chat_id) != "-1001353838635" and str(chat_id) != "84206430":
        text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
        context.bot.send_message(
            chat_id=-1001353838635,
            text=text,
        )
    if err != '':
        # if error happen, make it string and send it
        text = text
    else:
        # removing https links when sending them to main chat
        pass

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        # parse_mode='HTML'
    )
    if err:
        raise err


def send_parse_rocket(update, context):
    chat_id = update.effective_chat.id
    print("chart_id: " + str(chat_id))
    err = ''
    try:
        text = parse_rocket(update.message.text)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + '\n\n Borys will have a look ;)'
    if str(chat_id) != "-447482461" and str(chat_id) != "84206430":
        context.bot.send_message(
            chat_id=-447482461,
            text=text,
            # parse_mode='HTML'
        )

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        # parse_mode='HTML'
    )
    if err:
        raise err


class FilterOrder(MessageFilter):
    def filter(self, message):
        return 'Заказ #' in message.text
filter_order = FilterOrder()

class FilterRocket(MessageFilter):
    def filter(self, message):
        return '№' in message.text
filter_rocket = FilterRocket()

order_handler = MessageHandler(filter_order, send_parsed_order)
rocket_handler = MessageHandler(filter_rocket, send_parse_rocket)
dispatcher.add_handler(order_handler)
dispatcher.add_handler(rocket_handler)

# just logging messages recieved
def echo(update, context):
    print(update.message.text)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


# end loop of polling stopping and again.
# It seems that way I can read other bots messages in groups
# which is impossible other way
updater.start_polling()


def parse_rocket(text):
    l = []
    for i in text.split("\n"):
        if "№" in i:
            l.append({"price": 0, "type": ""})
        elif "UAH" in i:
            l[-1]["price"] = float(i.split(" ")[0])
        elif "money" in i or "credit_card" in i:
            l[-1]["type"] = i

    total = {"cash": 0, "credit_card": 0}
    for i in l:
        if i["type"] == "credit_card":
            total["credit_card"] += i["price"]
        elif i["type"] == "money":
            total["cash"] += i["price"]

    total["cash"] = round(total["cash"], 2)
    total["credit_card"] = round(total["credit_card"], 2)

    return f'Кеш: {total["cash"]}\nБезнал: {total["credit_card"]}'


def parse_order(text):
    # cleaning up before parsing the new input
    client_nocall, client_address = None, ''
    client_name, client_phone = None, None
    delivery_zone, total_order_price, order_type = None, None, None
    client_comment, persons, client_no_need = None, None, None
    result_order_block, other, utm = None, None, None
    do_not_know_zones, self_delivery = False, False

    order_block = text.split("Данные плательщика:")[0]
    add_block = text.split("Дополнительные данные:")
    if len(add_block) > 1:
        add_block = add_block[1]
    for line in add_block.split('\n'):
        if "UTM source:" in line:
            utm = line
            break

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
        print(line)
        print(client_comment, len(line.split(":")))
        if client_comment and len(line.split(":")) < 2 and no_need_bool is False:
            # in case comment is on a next line, add it to the comment, until next param happen
            client_comment = client_comment + '\n' + line
            continue

        info = line.split(":")[1].lstrip()
        if param == 'Name':
            client_name = info
        elif param == 'Address' or param == "Адрес доставки":
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
            no_need_bool = True
        elif param == 'Persons':
            persons = "Для: " + info
        elif param == 'Комент:' or param == 'Comment':
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
        result_order_block += amount + " x " + name + "\t - (" + total_price + " uah)" + "\n"
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

    parsed_text = []
    parsed_text += [client_nocall]
    if delivery_zone and "Курʼєром не орієнтуюсь яка зона" in delivery_zone:
        parsed_text += ["Не орієнтуються яка зона!"]
        do_not_know_zones = True
    elif delivery_zone and "Самовивiз" in delivery_zone:
        parsed_text += ["Самовивіз!"]
        self_delivery = True
    parsed_text += ["\n"]
    parsed_text += [client_name + " " + client_phone]
    if not self_delivery and not do_not_know_zones:
        parsed_text += [client_address, delivery_zone]
    elif not self_delivery:
        parsed_text += [client_address]

    parsed_text += [""]
    parsed_text += [total_order_price + "  (" + order_type + ")"]
    parsed_text += [""]
    parsed_text += [persons]
    if client_comment:
        parsed_text += [client_comment]
    if client_no_need:
        parsed_text += [client_no_need]
    parsed_text += [other]
    parsed_text += ['----']
    parsed_text += [result_order_block]
    if "LiqPay" in order_type:
        parsed_text += ["Разом: " + total_order_price + "  (Оплачено)", ""]
    else:
        parsed_text += ["Разом: " + total_order_price + "  (" + order_type + ")", ""]
    if utm:
        parsed_text += ['----', utm]
    if self_delivery:
        pass
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

        url = (
            f"https://www.google.com/maps/dir/Kniazia+Romana+St,+7,+Lviv,+Lviv+Oblast/"
            f"{client_address_fmt}"
            "+L'viv,+L'vivs'ka+oblast,+79000"
        )
        parsed_text += ["", url]


    return '\n'.join(
        [''.join(i) for i in parsed_text if i]
    )
