# -*- coding: utf-8 -*-

import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

b = "AAFiYwWlbJwvUhbwV"
c = "Zgu_caRA7oHMIp67a8"  # do not even ask why. it is gonna be used by regular people on windows man
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
a = "165506622"
updater = Updater(token=a + "2" + ':' + b + c, use_context=True)
dispatcher = updater.dispatcher


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
