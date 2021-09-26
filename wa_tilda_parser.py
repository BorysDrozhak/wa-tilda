# -*- coding: utf-8 -*-

import getpass
import logging
import re
import traceback

from telegram.ext import Filters, MessageFilter, MessageHandler, Updater
from utils.rocket import parse_rocket, parse_total_kassa
from utils.tilda import parse_order

waiters_channel = "-551172825"
orders_channel = "-1001353838635"
cash_flow_channel = "84206430"
cash_flow_channel2 = "-447482461"
wa_orders_channel = "-461519645"
operations_channel = "-396828808"
channels = [waiters_channel, orders_channel, cash_flow_channel, cash_flow_channel2]

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
    if str(chat_id) not in channels:
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
    print(str(chat_id))
    err = ''
    try:
        text = parse_rocket(update.message.text)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + '\n\n Borys will have a look ;)'

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        # parse_mode='HTML'
    )
    if err:
        raise err


def send_parse_zvit(update, context):
    chat_id = update.effective_chat.id
    err = ''
    try:
        text = parse_total_kassa(update.message.text)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + '\n\n Borys will have a look ;)'
    if str(chat_id) not in channels:
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
    tips = 0.0
    total_resto = 0.0
    for line in text.split('\n'):
        if "чай: " in line:
            tips = float(line.split(' ')[1].rstrip('?'))
        elif "Зал ресторану: " in line:
            total_resto = float(line.split(' ')[2])

    if tips:
        extra_text = f"не забудьте екстра чаєві через термінал: {tips}"
    else:
        extra_text = ''

    if total_resto < 1:
        return
    context.bot.send_message(
        chat_id=waiters_channel,
        text=(
            f"Нагадування: Будь ласка, запишіть чаєві "
            f"https://docs.google.com/spreadsheets/d/1Gps_LELU4rINF9WRPVaasOy1IiEjwwg9TIv9zMQ0deo/edit?usp=sharing\n{extra_text}"
            f"\n каса - {total_resto}"
        ),
        # parse_mode='HTML'
    )
    context.bot.send_message(
        chat_id=operations_channel,
        text=(
            "Good job team. Kind reminder for the end of the shift"
            "- Фоткаємо дошку з фідбеком і постимо в канал\n"
            "- Закриваємо робочу зміну в касі/айко/особисту\n"
            "- Вимикаємо світло в залі ресторану, на складі та кухні\n"
            "- Виключаємо усі девайси: чекодрук, принтер та кондиціонер\n"
            "- Прибираємо робоче місце\n"
            "- Перевіряємо заряд батереї на обох робочих телефонах та планшеті\n"
            "- Закриваємо металеві двері для входу курєрів та постачальників\n"
            "- Вимикаємо термінал\n"
            "- Скручуємо маркізу та вимикаємо ліхтарики на ній\n"
            "- Ставимо реторан на сигналізацію та закриваємо двері на ключ\n"
        ),
    )
    if err:
        raise err


class FilterOrder(MessageFilter):
    def filter(self, message):
        return 'Заказ #' in message.text
filter_order = FilterOrder()


class FilterRocket(MessageFilter):
    def filter(self, message):
        return 'arrow_right_alt' in message.text
filter_rocket = FilterRocket()


class FilterZvit(MessageFilter):
    def filter(self, message):
        return 'Каса 202' in message.text
filter_zvit = FilterZvit()

order_handler = MessageHandler(filter_order, send_parsed_order)
rocket_handler = MessageHandler(filter_rocket, send_parse_rocket)
zvit_handler = MessageHandler(filter_zvit, send_parse_zvit)
dispatcher.add_handler(order_handler)
dispatcher.add_handler(rocket_handler)
dispatcher.add_handler(zvit_handler)


# just logging messages recieved
def echo(update, context):
    chat_id = update.effective_chat.id
    print(update.message.text)
    print("chart_id: " + str(chat_id))

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


# end loop of polling stopping and again.
# It seems that way I can read other bots messages in groups
# which is impossible other way
updater.start_polling()
