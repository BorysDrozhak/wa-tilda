import logging
import re

from telegram.ext import (CommandHandler, Filters, MessageFilter,
                          MessageHandler, Updater)

b = "AAFiYwWlbJwvUhbwV"
c = "Zgu_caRA7oHMIp67a8"  # do not even ask why. it is gonna be used by regular people on windows man
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
a = "165506622"
tok = a + "2" + ':' + b + c

updater = Updater(token=tok, use_context=True)
dispatcher = updater.dispatcher

def send_parsed_order(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=parse_order(update.message.text)
    )

class FilterAwesome(MessageFilter):
    def filter(self, message):
        return 'Заказ #' in message.text
filter_awesome = FilterAwesome()

order_handler = MessageHandler(filter_awesome, send_parsed_order)
dispatcher.add_handler(order_handler)

# just logging messages recieved
def echo(update, context):
    print(update.message.text)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)




updater.start_polling()


def parse_order(text):
    # cleaning up before parsing the new input
    client_nocall, client_address = None, None
    client_name, client_phone = None, None
    delivery_zone, total_order_price, order_type = None, None, None
    client_comment, persons, client_no_need = None, None, None
    result_order_block, other, utm = None, None, None

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
            persons = "Для: " + info
        elif param == 'Комент:':
            client_comment = "Comment: " + info
        elif param == 'НЕдзвонити-НАПИСАТИ':
            if info == 'yes':
                client_nocall = 'NO CALL\n'
        else:
            other += line
    if not other:
        other = ''
    if not client_nocall:
        client_nocall = 'Треба дзвонити клієнту!\n'

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
        elif "Розмір порції: XL СЕТ (3 шт в крафтовому боксі з авторським салатом)" in options:
            name = name + " (XL СЕТ 3 шт)"
        elif "Розмір порції: XS (protein balanced)" in options:
            name = name + " (XS protein balanced)"
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
                    "Потрібні імбир та васабі?: Так",
                    "Бажаєте додати до боулу броколі(30г) чи більше лосося(30г)?: Ні",
                    "дякую",
                    "Розмір порції: Standard",
                    "Розмір порції: XS (protein balanced)",
                ]:
                    continue
                result_order_block += "    " + option + "\n"

    parsed_text = []
    parsed_text += [client_nocall]
    parsed_text += [client_name + " " + client_phone]
    if "Самовивiз" in delivery_zone:
        parsed_text += ["Самовивіз!"]
    else:
        parsed_text += [client_address]
        parsed_text += [delivery_zone]
    parsed_text += [""]
    parsed_text += [total_order_price + " " + order_type]
    parsed_text += [""]
    parsed_text += [persons]
    if client_comment:
        parsed_text += [client_comment]
    if client_no_need:
        parsed_text += [client_no_need]
    parsed_text += [other]
    parsed_text += ['----']
    parsed_text += [result_order_block]
    if utm:
        parsed_text += ['----', utm]

    return '\n'.join(
        [i for i in parsed_text if i]
    )
