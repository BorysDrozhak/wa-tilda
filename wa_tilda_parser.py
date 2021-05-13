import getpass
import logging
import re
import traceback

from telegram.ext import Filters, MessageFilter, MessageHandler, Updater
from utils.rocket import parse_rocket, parse_total_kassa
from utils.tilda import parse_order

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
    err = ''
    try:
        text = parse_rocket(update.message.text)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + '\n\n Borys will have a look ;)'
    # Do not send in cache-flow
    # if str(chat_id) != "-447482461" and str(chat_id) != "84206430":
    #     context.bot.send_message(
    #         chat_id=-447482461,
    #         text=text,
    #         # parse_mode='HTML'
    #     )

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
    print(update.message.text)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


# end loop of polling stopping and again.
# It seems that way I can read other bots messages in groups
# which is impossible other way
updater.start_polling()
