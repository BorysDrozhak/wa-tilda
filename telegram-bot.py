# -*- coding: utf-8 -*-

import logging
import datetime
import pytz

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, MessageFilter, JobQueue

from utils.filters import filter_initial, filter_additional, filter_end_questions, filter_questions
from utils.states import user_data, state_obj

BUTTONS = [['Так', 'Ні']]

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

def callback_daily(context):
    state_obj.slowdown()
    context.bot.send_message(chat_id=context.job.context, text='Виберіть тему для сьогоднішнього опитування')


def set_title(update, context):
    chat_id = update.effective_chat.id
    title = update.message.text
    if not user_data.USER_DATA.get('title'):
        user_data.USER_DATA.update({'title': title})
    context.bot.send_message(chat_id=chat_id, text='Надішліть текст запитання')
    if state_obj.current_state.name != 'Questions':
        state_obj.question()


def create_questions(update, context):
    chat_id = update.effective_chat.id
    question = update.message.text
    data = user_data.USER_DATA
    data.get('questions').append(question)
    context.bot.send_message(chat_id=chat_id, text='Чи бажаєте добавити ще запитань?',
                             reply_markup=ReplyKeyboardMarkup(BUTTONS, resize_keyboard=True, one_time_keyboard=True))


def create_poll(update, context):
    """Sends a predefined poll"""
    questions = user_data.USER_DATA.get('questions')
    title = user_data.USER_DATA.get('title')
    message = context.bot.send_poll(
        update.effective_chat.id,
        title,
        questions,
        is_anonymous=True,
        allows_multiple_answers=False,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)
    user_data.USER_DATA.update({'title': None, 'questions': []})
    state_obj.reverse()



def set_daily_message(update, context):
    chat_id = update.message.chat_id
    context.job_queue.run_daily(callback_daily, time=datetime.time(hour=14, minute=00, tzinfo=pytz.timezone('Europe/Kiev')),
                                days=(0, 1, 2, 3, 4, 5, 6), context=chat_id, name=str(chat_id))


def stop_daily(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id,
                      text='Stoped!')
    context.job_queue.stop()


dispatcher.add_handler(CommandHandler("daily_message", set_daily_message, pass_job_queue=True))
dispatcher.add_handler(CommandHandler('stop_daily', stop_daily, pass_job_queue=True))
title_handler = MessageHandler(filter_initial, set_title, )
dispatcher.add_handler(title_handler)
additional_questions_handler = MessageHandler(filter_additional, set_title, )
dispatcher.add_handler(additional_questions_handler)
end_questions_handler = MessageHandler(filter_end_questions, create_poll, )
dispatcher.add_handler(end_questions_handler)
questions_handler = MessageHandler(filter_questions, create_questions, )
dispatcher.add_handler(questions_handler)

updater.start_polling()
