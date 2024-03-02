import asyncio
import datetime
import getpass

from telegram import ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder

from utils.weather_cli import save_weather, kyiv_timezone
from utils.gspread_api import update_empl_trial, create_creds_json, CREDENTIALS_DICT, get_employees
from utils.telethon_operations import bot_respond, get_messages, send_messages
from utils.poll_data import POLLS

loop = asyncio.get_event_loop()

b = "AAFiYwWlbJwvUhbwV"
c = "Zgu_caRA7oHMIp67a8"  # do not even ask why. it is gonna be used by mere people on windows man
a = "165506622"
tok = a + "2" + ":" + b + c

d = "1700108054:A"
f = "AFsN_Agk1G5eyh19Dxqdn_jrPmuW60Zy5"
b_bot = d + f + "4"

a_1 = "2092656899:A"
a_2 = "AGHqh_IFd1li2aVxNBHVqx7WaCVHqqHwN"

a_bot = a_1 + a_2 + "I"

env = "prod"

if getpass.getuser() == "bdrozhak":
    tok = b_bot
    env = "dev"

elif getpass.getuser() == "andriyzhyhil":
    tok = a_bot
    env = "dev"


wa_bar_channel = '-1001749242642'
site_orders_channel = "-1001353838635"
operations_channel = "-1001719165729"
stakeholders_channel = "-1001524640483"

application = ApplicationBuilder().token(tok).build()

BARTENDER_REMINDER_TEXT = '''
@luluk_vb @Yakuza00777 

Замовлення молока на бар 🥛
- безлактозне 1 ящик
- класичне 2 ящика

Переглянути склад на залишок молока❗
'''

BLOGGERS_REMINDER_TEXT = '''
Написати @bd_xz_b список кооперацій по 
бартеру з блогерами на поточний і
наступний тиждень
'''


def callback_daily(event, context):
    todays_date = datetime.datetime.now(tz=kyiv_timezone).date()
    day_in_year = todays_date.day
    poll_index = day_in_year - len(POLLS) * (day_in_year // len(POLLS))
    poll_data = POLLS[poll_index]
    loop.run_until_complete(application.bot.send_poll(
        operations_channel,
        poll_data["title"],
        poll_data["questions"],
        is_anonymous=False,
        allows_multiple_answers=False,
        reply_markup=ReplyKeyboardRemove(),
    ))


def callback_bartenders(event, context):
    loop.run_until_complete(application.bot.send_message(
        wa_bar_channel,
        text=BARTENDER_REMINDER_TEXT
    ))


def callback_bloggers(event, context):
    loop.run_until_complete(application.bot.send_message(
        wa_bar_channel,
        text=BLOGGERS_REMINDER_TEXT
    ))


def callback_daily_stakeholders(event, context):
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
    loop.run_until_complete(application.bot.send_message(
        chat_id=stakeholders_channel,
        text=message,
    ))


def callback_repeating(event, context):
    save_weather()


def callback_last_order_alarm(event, context):
    try:
        messages = loop.run_until_complete(get_messages(int(site_orders_channel)))
    except Exception as e:
        print(e)
    else:
        if not bot_respond(messages):
            loop.run_until_complete(application.bot.send_message(
                chat_id=site_orders_channel,
                text="@bd_xz_b @yanochka_s_s @violetochkalllll\nАгов! Замовлення вже більше 5 хвилин висить без обробки!"
            ))


def weekly_reminder(event=None, context=None):
    try:
        gc_creds = create_creds_json(CREDENTIALS_DICT)
        employees = get_employees(creds=gc_creds)
    except Exception as e:
        print(e)
        return
    try:
        loop.run_until_complete(send_messages(employees))
    except Exception as e:
        print(e)


def callback_onboarding_monthly(event=None, context=None):
    gc_creds = create_creds_json(CREDENTIALS_DICT)
    employees = update_empl_trial(creds=gc_creds)
    employees_success_trial = []
    for empl in employees:
        employees_success_trial.append(f"{empl.get('username')}: {empl.get('role')}")

    if employees_success_trial:
        loop.run_until_complete(application.bot.send_message(
            chat_id=stakeholders_channel,
            text=f"@bd_xz_b\nПрацівники: {', '.join(employees_success_trial)} успішно завершили випробувальний термін"
        ))

