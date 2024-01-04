# -*- coding: utf-8 -*-
import json
import enum
import asyncio
import datetime
import getpass
import logging
import re
import traceback
import pytz
from retry import retry

import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Filters, MessageFilter, MessageHandler, Updater, CommandHandler, ConversationHandler

from utils.rocket import parse_rocket, parse_total_kassa
from utils.tilda import parse_order
from utils.poll_data import POLLS, BUTTONS
from utils.filters import filter_generate, filter_cancel
from utils.states import state_obj
from utils.weather_cli import save_weather
from utils.telethon_operations import get_messages, bot_respond, add_member, wa_bot_id
from utils.gspread_api import add_user_data, update_empl_trial
from utils.graphs import build_graphs

waiters_channel = "-1001792566598"
site_orders_channel = "-1001353838635"
cash_flow_channel = "-1001658828551"
cash_flow_channel2 = "-447482461"
wa_orders_channel = "-461519645"
operations_channel = "-1001719165729"
stakeholders_channel = "-1001524640483"
channels = [waiters_channel, site_orders_channel, cash_flow_channel, cash_flow_channel2]

def get_bot(tok):
    bot = telegram.Bot(token=tok)
    return bot

b = "AAFiYwWlbJwvUhbwV"
c = "Zgu_caRA7oHMIp67a8"  # do not even ask why. it is gonna be used by mere people on windows man
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
a = "165506622"
tok = a + "2" + ":" + b + c

d = "1700108054:A"
f = "AFsN_Agk1G5eyh19Dxqdn_jrPmuW60Zy5"
b_bot = d + f + "4"

a_1 = "2092656899:A"
a_2 = "AGHqh_IFd1li2aVxNBHVqx7WaCVHqqHwN"

a_bot = a_1 + a_2 + "I"

env = "prod"

loop = asyncio.get_event_loop()

if getpass.getuser() == "bdrozhak":
    tok = b_bot
    env = "dev"

elif getpass.getuser() == "andriyzhyhil":
    tok = a_bot
    env = "dev"
    bot = telegram.Bot(token=tok)
    # loop.run_until_complete(start_jobs(int(operations_channel)))

@retry(Exception, tries=3, delay=3)
def send_parsed_order(message, chat_id, bot):
    print("chart_id: " + str(chat_id))
    err = ""
    text_for_client = ""
    try:
        text, text_for_client = parse_order(message)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + "\n\n Borys will have a look ;)"
    if str(chat_id) not in channels and env == "prod":
        text = re.sub(r"^https?:\/\/.*[\r\n]*", "", text, flags=re.MULTILINE)
        bot.send_message(
            chat_id=site_orders_channel,
            text=text,
        )
    if err != "":
        # if error happen, make it string and send it
        text = text
        text_for_client = ""
    else:
        # removing https links when sending them to main chat
        pass

    bot.send_message(
        chat_id=wa_bot_id,
        text=text,
    )
    if text_for_client:
        bot.send_message(
            chat_id=wa_bot_id,
            text=text_for_client,
        )

    if err:
        raise err


def send_parse_rocket(message, chat_id, bot):
    print(str(chat_id))
    err = ""
    try:
        text = parse_rocket(message)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + "\n\n Borys will have a look ;)"

    bot.send_message(
        chat_id=wa_bot_id,
        text=text,
        # parse_mode='HTML'
    )
    if err:
        raise err


@retry(Exception, tries=3, delay=3)
def send_parse_zvit(message, chat_id, bot):
    err = ""
    try:
        text = parse_total_kassa(message, env)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + "\n\n Borys will have a look ;)"
    if str(chat_id) not in channels:
        bot.send_message(
            chat_id=-447482461,
            text=text,
            # parse_mode='HTML'
        )

    bot.send_message(
        chat_id=cash_flow_channel,
        text=text,
        # parse_mode='HTML'
    )
    try:
        build_graphs(bot)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }

    tips = 0.0
    total_resto = 0.0
    for line in text.split("\n"):
        if "чай: " in line:
            tips = float(line.split(" ")[1].rstrip("?"))
        elif "Зал ресторану: " in line:
            total_resto = float(line.split(" ")[2])

    if tips:
        extra_text = f"не забудьте екстра чаєві через термінал: {tips}"
    else:
        extra_text = ""

    if total_resto < 1:
        return
    bot.send_message(
        chat_id=waiters_channel,
        text=(
            f"Нагадування: Будь ласка, запишіть чаєві "
            f"https://docs.google.com/spreadsheets/d/1Gps_LELU4rINF9WRPVaasOy1IiEjwwg9TIv9zMQ0deo/edit?usp=sharing\n{extra_text}"
            f"\n каса - {total_resto}"
        ),
        # parse_mode='HTML'
    )
    bot.send_message(
        chat_id=operations_channel,
        text=(
            "Люблю вас пупсики. незабудьте про\n\n"
            "- Cвітло на складі та кухні\n"
            "- Кондиціонер\n"
            "- Прибираємо робочі місця\n"
            "- Телефонах та планшет зарядка\n"
            "- Закриваємо металеві двері\n"
            "- Термінал виключаєм\n"
            "- Маркізу та ліхтарики на ній скручуємо і вимикаєм\n\n"
            "Кухня\n"
            "- не забувайте будь ласка вимикати ваги 🙏🏻"
        ),
    )
    if err:
        return {
            'statusCode': 500,
            'body': json.dumps(str(err))
        }


def send_kasa(message, chat_id, bot):

    text = f"""

Каса {datetime.date.today()}.

Готівка
    Доставка = 
    Ресторан = 
    Загально = 

Термінал
    Доставка = 
    Ресторан = 
    Shake to pay = 
    Загально = 
    Z-звіт   = 

LiqPay доставки = 

Glovo Кеш = 
Glovo Безнал = 
Glovo Total = 

Bolt Кеш = 
Bolt Безнал = 
Bolt Total = 

Готівка в касі:
"""
    bot.send_message(
        chat_id=cash_flow_channel,
        text=text,
    )


class FilterOrder(MessageFilter):
    def filter(self, message):
        return "Заказ №" in message if message else False


filter_order = FilterOrder()


class FilterRocket(MessageFilter):
    def filter(self, message):
        return "arrow_right_alt" in message if message else False


filter_rocket = FilterRocket()


class FilterZvit(MessageFilter):
    def filter(self, message):
        return "Каса 202" in message if message else False


filter_zvit = FilterZvit()


class FilterKasa(MessageFilter):
    def filter(self, message):
        text = ''
        if message:
            text = message.lower()
        return "каса" in text and not "202" in text


filter_kasa = FilterKasa()

# daily poll job
def poll_cancel(bot):
    state_obj.reset()
    bot.send_message(chat_id=operations_channel, text="Дякую!", reply_markup=ReplyKeyboardRemove())


def create_poll(bot):
    """Sends a predefined poll"""
    todays_date = datetime.date.today()
    day_in_year = todays_date.day
    poll_index = day_in_year - len(POLLS) * (day_in_year // len(POLLS))
    poll_data = POLLS[poll_index]
    bot.send_poll(
        operations_channel,
        poll_data["title"],
        poll_data["questions"],
        is_anonymous=False,
        allows_multiple_answers=False,
        reply_markup=ReplyKeyboardRemove(),
    )
    state_obj.reset()


#  run job for daily poll
def callback_daily(context):
    state_obj.generate()
    context.bot.send_message(
        chat_id=operations_channel,
        text='''Запустити Командний челендж?\nАдміни, не забудьте переглянути
        https://docs.google.com/document/d/1t7syqEJAOvpT8Vso7VE5BYfFP5zng_tNpsGJYXMEUi0/edit?usp=sharing''',
        reply_markup=ReplyKeyboardMarkup(BUTTONS, resize_keyboard=True, one_time_keyboard=True),
    )


#  run job for daily poll
def callback_daily_stakeholders(context):
    message = '''
Привіт всім. Давайте пропишем:
- успіхи за вчора
- блокери та виклики
- плани на сьогодні
'''
    if datetime.date.today().weekday() == 0:
        message += '''- репорт по минулому тижню
- план на цей тиждень
        '''
    message += '''
    
Всім дякую, і продуктивного дня
    '''
    context.bot.send_message(
        chat_id=stakeholders_channel,
        text=message,
    )


def callback_repeating(context):
    save_weather()


def callback_last_order_alarm(context):
    try:
        messages = loop.run_until_complete(get_messages(int(site_orders_channel)))
    except:
        pass
    else:
        if not bot_respond(messages):
            context.bot.send_message(
                chat_id=site_orders_channel,
                text="@bd_xz_b @yanochka_s_s @serhiy_yurta \nАгов! Замовлення вже більше 5 хвилин висить без обробки!"
            )


def callback_onboarding_monthly(context):
    update_empl_trial()


#  create queue for daily running jobs
def run_jobs(update, context):
    chat_id = update.message.chat_id
    context.job_queue.run_daily(
        callback_daily,
        time=datetime.time(hour=9, minute=00, tzinfo=pytz.timezone("Europe/Kiev")),
        days=(0, 1, 2, 3, 4, 5, 6),
        context=chat_id,
        name=str(chat_id),
    )
    context.bot.send_message(
        chat_id=operations_channel, text="Дякую, тепер челенджі будуть працювати! Продуктивного дня вам там! 😌"
    )
    context.job_queue.run_repeating(callback_repeating, interval=10800, first=1, context=None, name='Daily weather')
    context.job_queue.run_repeating(callback_last_order_alarm, interval=300, first=1, context=None, name='Order alarm')
    context.job_queue.run_daily(
        callback_daily_stakeholders,
        time=datetime.time(hour=9, minute=00, tzinfo=pytz.timezone("Europe/Kiev")),
        days=(0, 1, 2, 3, 4),
        context=chat_id,
        name=str(chat_id),
    )
    context.job_queue.run_monthly(
        callback_onboarding_monthly,
        when=datetime.time(hour=9, minute=00, tzinfo=pytz.timezone("Europe/Kiev")),
        day=8,
        context=chat_id,
        name='Onboarding',
    )


#  stop daily jobs
def stop_daily(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Stoped!")
    context.job_queue.stop()


# Define conversation states
USERNAME, DATE, ROLE = range(3)


class Roles(enum.Enum):
    waiter = 'офіціант'
    chef = 'кухар'
    bartender = 'бармен'
    admin = 'адмін'


class Channels(enum.Enum):
    operations_channel = -1001719165729
    cash_flow_channel = -1001658828551
    site_orders_channel = -1001353838635
    wa_bar_channel = -1001749242642
    wa_kitchen_channel = -1001230684288
    wa_resto_hall_channel = -1001796662118
    wa_payment_of_bills_channel = -1001981228751
    wa_announcement_channel = -1001798929013


CHANNELS_BY_ROLE = {
    Roles.chef.value: [
        Channels.operations_channel.value,
        Channels.cash_flow_channel.value,
        Channels.site_orders_channel.value,
        Channels.wa_kitchen_channel.value,
        Channels.wa_announcement_channel.value,
    ],
    Roles.waiter.value: [
        Channels.operations_channel.value,
        Channels.cash_flow_channel.value,
        Channels.site_orders_channel.value,
        Channels.wa_announcement_channel.value,
        Channels.wa_resto_hall_channel.value,
    ],
    Roles.bartender.value: [
        Channels.operations_channel.value,
        Channels.cash_flow_channel.value,
        Channels.site_orders_channel.value,
        Channels.wa_bar_channel.value,
        Channels.wa_announcement_channel.value,
        Channels.wa_resto_hall_channel.value,
    ],
    Roles.admin.value: [
        Channels.operations_channel.value,
        Channels.cash_flow_channel.value,
        Channels.site_orders_channel.value,
        Channels.wa_payment_of_bills_channel.value,
        Channels.wa_announcement_channel.value,
        Channels.wa_kitchen_channel.value,
        Channels.wa_bar_channel.value,
        Channels.wa_resto_hall_channel.value,
    ],
}

ONBOARDING_LINKS = {
    'офіціант': '',
    'кухар': '',
    'бармен': '',
    'адмін': '',
}


def start_adding(bot, user_info, chat_id):
    user_info_list = user_info.split(',')
    user_info_dict = {'username': user_info_list[0], 'role': user_info_list[1], 'date': user_info_list[2]}
    if user_info_dict.get('username') and not user_info_dict.get('username').startswith('@'):
        user_info_dict['username'] = f'@{user_info_dict.get("username")}'

    add_members(user_info, bot, chat_id)


def onboarding_message(user_info, bot):
    role = user_info.get('role').lower()
    link = ONBOARDING_LINKS.get(role)
    bot.send_message(
        chat_id=operations_channel, text=f'{user_info.get("username")}, Велком в команду ВА!\n🤗️️️️️️\n\n'
                                         'це основна група для адмінів ресторану\n\n'
                                         'Обговорюється щоденні питання\n'
                                         'пов’язані із діяльність ресторану,\n'
                                         'враженням гостей від WA, завдання\n'
                                         'для адмінів, рекламні пропозиції та інтеграції.\n\n'
                                         'Тут можна долучатись до обговорень\n'
                                         'та пропонувати свої ідеї\nта бачення 🙌🏻\n\n'
                                         'Ось наш онбордінг документ, який\nми тримаємо оновленим, і завжди\n'
                                         f'раді доповнити.\n'
                                         f'{link}\n\n'
                                         f'Розкажите, чи було цікаво. ну і,\nуспіхів в команді!\n'
    )


def add_members(user_info, bot, chat_id):
    role = user_info.get('role').lower()
    channels_to_add = CHANNELS_BY_ROLE.get(role)
    user_data = [
        *user_info.values(),
        'false',
    ]
    try:
        loop.run_until_complete(add_member(user_info['username'], channels_to_add))
    except Exception as e:
        print(e)
        bot.send_message(text='Упс!\nЩось пішло не так(\nСпробуйте ще раз')
    else:
        add_user_data(user_data)
        bot.send_message(text='Інформація про працівника успішно збережена!')
        onboarding_message(user_info, bot)


def run(event=None, context=None):
    try:
        body = json.loads(event['body'])
        message = body['message']['text']
        chat_id = body['message']['chat']['id']
        print(message)
        print(body)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
    b = "AAFiYwWlbJwvUhbwV"
    c = "Zgu_caRA7oHMIp67a8"  # do not even ask why. it is gonna be used by mere people on windows man
    a = "165506622"
    tok = a + "2" + ":" + b + c
    bot = get_bot(tok)
    try:
        if filter_order.filter(message):
            send_parsed_order(message, chat_id, bot)
        if filter_rocket.filter(message):
            send_parse_rocket(message, chat_id, bot)
        if filter_zvit.filter(message):
            send_parse_zvit(message, chat_id, bot)
        if filter_kasa.filter(message):
            send_kasa(message, chat_id, bot)
        if filter_generate.filter(message):
            create_poll(bot)
        if filter_cancel.filter(message):
            poll_cancel(bot)
        # if message == '/add_employee':
        #     bot.send_message(
        #         text='''Додайте інформацію про нового працівника у наступному форматі:'''
        #         '''Ролі (Кухар|Офіціант|Адмін|Бармен)'''
        #         '''@нік користувача, роль одна з вище вказаних, дата у форматі dd-mm-YYY'''
        #     )
        # if chat_id == str(wa_bot_id):
        #     try:
        #         start_adding(bot, message, chat_id)
        #     except:
        #         return
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Message processed successfully')
        }
