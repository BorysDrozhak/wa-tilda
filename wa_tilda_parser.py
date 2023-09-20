# -*- coding: utf-8 -*-
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
from utils.telethon_operations import get_messages, bot_respond, start_jobs, add_member
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

if env == "prod":
    bot = telegram.Bot(token=tok)
    bot.send_message(
        chat_id=operations_channel,
        text="Наш ВА бот був успішно перегружений.",
    )
    try:
        loop.run_until_complete(start_jobs(int(operations_channel)))
    except:
        pass

updater = Updater(token=tok, use_context=True)
dispatcher = updater.dispatcher


@retry(Exception, tries=3, delay=3)
def send_parsed_order(update, context):
    chat_id = update.effective_chat.id
    print("chart_id: " + str(chat_id))
    err = ""
    text_for_client = ""
    try:
        text, text_for_client = parse_order(update.message.text)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + "\n\n Borys will have a look ;)"
    if str(chat_id) not in channels and env == "prod":
        text = re.sub(r"^https?:\/\/.*[\r\n]*", "", text, flags=re.MULTILINE)
        context.bot.send_message(
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

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
    )
    if text_for_client:
        context.bot.send_message(
            chat_id=chat_id,
            text=text_for_client,
        )

    if err:
        raise err


def send_parse_rocket(update, context):
    chat_id = update.effective_chat.id
    print(str(chat_id))
    err = ""
    try:
        text = parse_rocket(update.message.text)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + "\n\n Borys will have a look ;)"

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        # parse_mode='HTML'
    )
    if err:
        raise err


@retry(Exception, tries=3, delay=3)
def send_parse_zvit(update, context):
    chat_id = update.effective_chat.id
    err = ""
    try:
        text = parse_total_kassa(update.message.text, env)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + "\n\n Borys will have a look ;)"
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
    try:
        build_graphs(context, chat_id)
    except Exception as e:
        print(e)

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
        raise err


def send_kasa(update, context):
    chat_id = update.effective_chat.id

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
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
    )


class FilterOrder(MessageFilter):
    def filter(self, message):
        return "Заказ №" in message.text if message.text else False


filter_order = FilterOrder()


class FilterRocket(MessageFilter):
    def filter(self, message):
        return "arrow_right_alt" in message.text if message.text else False


filter_rocket = FilterRocket()


class FilterZvit(MessageFilter):
    def filter(self, message):
        return "Каса 202" in message.text if message.text else False


filter_zvit = FilterZvit()


class FilterKasa(MessageFilter):
    def filter(self, message):
        text = ''
        if message.text:
            text = message.text.lower()
        return "каса" in text and not "202" in text


filter_kasa = FilterKasa()

order_handler = MessageHandler(filter_order, send_parsed_order)
rocket_handler = MessageHandler(filter_rocket, send_parse_rocket)
zvit_handler = MessageHandler(filter_zvit, send_parse_zvit)
kasa_handler = MessageHandler(filter_kasa, send_kasa)
dispatcher.add_handler(order_handler)
dispatcher.add_handler(rocket_handler)
dispatcher.add_handler(zvit_handler)
dispatcher.add_handler(kasa_handler)


# daily poll job
def poll_cancel(update, context):
    state_obj.reset()
    context.bot.send_message(chat_id=operations_channel, text="Дякую!", reply_markup=ReplyKeyboardRemove())


def create_poll(update, context):
    """Sends a predefined poll"""
    todays_date = datetime.date.today()
    day_in_year = todays_date.day
    poll_index = day_in_year - len(POLLS) * (day_in_year // len(POLLS))
    poll_data = POLLS[poll_index]
    message = context.bot.send_poll(
        update.effective_chat.id,
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


dispatcher.add_handler(CommandHandler("daily_poll", run_jobs, pass_job_queue=True))
dispatcher.add_handler(CommandHandler("stop_daily", stop_daily, pass_job_queue=True))
poll_handler = MessageHandler(
    filter_generate,
    create_poll,
)
dispatcher.add_handler(poll_handler)
cancel_poll_handler = MessageHandler(
    filter_cancel,
    poll_cancel,
)
dispatcher.add_handler(cancel_poll_handler)

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


def start_adding(update, context):
    reply_keyboard = [['Cancel']]
    update.message.reply_text(
        'Будь ласка додайте нового працівника\n\n'
        'Username:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return USERNAME


def collect_username(update, context):
    context.user_data['username'] = update.message.text
    reply_keyboard = [['Cancel']]
    update.message.reply_text(
        'Дата у форматі dd-mm-YYYY:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return DATE


def collect_date(update, context):
    context.user_data['date'] = update.message.text
    reply_keyboard = [['Cancel']]
    roles = [r.value for r in Roles]
    update.message.reply_text(
        f'Роль ({", ".join(roles)}):',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ROLE


def collect_role(update, context):
    context.user_data['role'] = update.message.text

    # Get the collected user information
    user_info = {
        'username': context.user_data['username'],
        'role': context.user_data['role'],
        'date': context.user_data['date']
    }

    if user_info.get('username') and not user_info.get('username').startswith('@'):
        user_info['username'] = f'@{user_info.get("username")}'

    add_members(user_info, update, context)

    return ConversationHandler.END


def onboarding_message(user_info, context):
    role = user_info.get('role').lower()
    link = ONBOARDING_LINKS.get(role)
    context.bot.send_message(
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


def add_members(user_info, update, context):
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
        update.message.reply_text('Упс!\nЩось пішло не так(\nСпробуйте ще раз')
    else:
        add_user_data(user_data)
        update.message.reply_text('Інформація про працівника успішно збережена!')
        onboarding_message(user_info, context)


def cancel(update, context):
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('add_employee', start_adding)],
    states={
        USERNAME: [MessageHandler(Filters.text, collect_username)],
        DATE: [MessageHandler(Filters.text, collect_date)],
        ROLE: [MessageHandler(Filters.text, collect_role)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

# Add the conversation handler to the dispatcher
dispatcher.add_handler(conv_handler)


# just logging messages recieved
def echo(update, context):
    chat_id = update.effective_chat.id
    print(update.message.text)
    print("chart_id: " + str(chat_id))
    if bot_has_to_react(update):
        context.bot.send_message(update.effective_chat.id, reply_to_message_id=update.message.message_id, text='🥰')


def bot_has_to_react(update):
    if not update.effective_message.reply_to_message:
        return False
    if update.effective_message.reply_to_message and not \
            update.effective_message.reply_to_message.from_user.is_bot == True:
        return False
    if re.search(r'дякую|навзаєм', update.message.text, re.IGNORECASE):
        return True
    return False


echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)
# end loop of polling stopping and again.
# It seems that way I can read other bots messages in groups
# which is impossible other way
updater.start_polling()
