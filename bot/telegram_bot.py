# -*- coding: utf-8 -*-

import json
import enum
import asyncio
import datetime
import getpass
import logging
import re
import traceback

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import MessageHandler, CommandHandler, ConversationHandler, ApplicationBuilder
from telegram.ext.filters import MessageFilter, TEXT, COMMAND

from utils.rocket import parse_rocket, parse_total_kassa
from utils.tilda import parse_order
from utils.telethon_operations import add_member
from utils.gspread_api import add_user_data
from utils.graphs import build_graphs
from utils.weather_cli import kyiv_timezone

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


application = ApplicationBuilder().token(tok).build()


async def send_parsed_order(update, context):
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
        await context.bot.send_message(
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

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
    )
    if text_for_client:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text_for_client,
        )

    if err:
        raise err


async def send_parse_rocket(update, context):
    chat_id = update.effective_chat.id
    print(str(chat_id))
    err = ""
    try:
        text = parse_rocket(update.message.text)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + "\n\n Borys will have a look ;)"

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        # parse_mode='HTML'
    )
    if err:
        raise err


async def send_parse_zvit(update, context):
    chat_id = update.effective_chat.id
    err = ""
    try:
        text = parse_total_kassa(update.message.text, env)
    except Exception as e:
        err = e
        text = str(traceback.format_exc())
        text = text + "\n\n Borys will have a look ;)"

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        # parse_mode='HTML'
    )
    try:
        await build_graphs(context, chat_id)
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
    await context.bot.send_message(
        chat_id=waiters_channel,
        text=(
            f"Нагадування: Будь ласка, запишіть чаєві "
            f"https://docs.google.com/spreadsheets/d/1Gps_LELU4rINF9WRPVaasOy1IiEjwwg9TIv9zMQ0deo/edit?usp=sharing\n{extra_text}"
            f"\n каса - {total_resto}"
        ),
        # parse_mode='HTML'
    )
    await context.bot.send_message(
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


async def send_kasa(update, context):
    chat_id = update.effective_chat.id

    text = f"""

Каса {datetime.datetime.now(tz=kyiv_timezone).date()}.

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
    await context.bot.send_message(
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
        pattern = re.compile(r'^каса$', re.IGNORECASE)
        match = pattern.search(message.text)
        return bool(match)


filter_kasa = FilterKasa()

order_handler = MessageHandler(filter_order, send_parsed_order)
rocket_handler = MessageHandler(filter_rocket, send_parse_rocket)
zvit_handler = MessageHandler(filter_zvit, send_parse_zvit)
kasa_handler = MessageHandler(filter_kasa, send_kasa)

# Define conversation states
USERNAME, DATE, ROLE = range(3)


class Roles(enum.Enum):
    waiter = 'офіціант'
    chef = 'кухар'
    bartender = 'бармен'
    admin = 'адмін'
    manager = 'управляючий'


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
    Roles.manager.value: [
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
    'кухар': 'https://docs.google.com/document/d/1CQxVj1iMJd77RmkI0jDIOA27kSJ334xePoiWevF3OlQ/edit?usp=sharing',
    'бармен': '',
    'адмін': '',
    'офіціант': 'https://docs.google.com/file/d/1Tr_MJm7HJ39GpebVy2wEH6X1Q2QYicnu/edit?usp=docslist_api&filetype=msword',
    'управляючий': '',
}
RESTO_HALL_MESSAGE = '''це основна група команди залу 🙌🏻\n\n
Тут публікуємо резерви і моменти котрі\n
відбувається на залі ресторану і треба\n
взяти до уваги 😉\n\n
Пишемо враження про гостей, чи їм усе\n
сподобалось і чи були фідбеки про сервіс.'''

OPERATIONS_MESSAGE = '''Велком в команду ВА!\n🤗️️️️️️\n\n
це основна група для адмінів ресторану\n\n
Обговорюється щоденні питання\n
пов’язані із діяльність ресторану,\n
враженням гостей від WA, завдання\n
для адмінів, рекламні пропозиції та інтеграції.\n\n
Тут можна долучатись до обговорень\n
та пропонувати свої ідеї\nта бачення 🙌🏻\n\n
Ось наш онбордінг документ, який\nми тримаємо оновленим, і завжди раді доповнити.\n
Розкажите, чи було цікаво. ну і,\nуспіхів в команді!\n'''

SITE_ORDERS_MESSAGE = 'це група де приходять наші замовлення на доставку із сайту 🛵'

CASH_FLOW_MESSAGE = '''це наша основна фінансова група\n
де ми надсилаємо фото усіх готівкових накладних\n
та вирішуємо поточні фінансові питання\n
'з фінансовим директором, управляючим та інвесторами'''

KITCHEN_MESSAGE = '''це одна із основних груп нашого ресторану 🧑🏻‍🍳👩🏻‍🍳.\n
Тут обговорюємо усі питання пов’язані із стравами, їхньою видачею, якістю.\n
Фідбеки від гостей теж ретранслюються сюди\n
щоб усі бачили результат своєї роботи.\n
Будь-які замовлення по кухні також можна писати сюди\n
ідеї по стравам, їхньому візуальному оформленню та ідеям\n
для покращення кухні в загальному 🙇🏼‍♂️'''

BAR_MESSAGE = '''це основна група для команди бару 🥃🍸.\n
Тут обговорюємо питання пов’язані із барним меню\n
коктейльною картою, новими проробками\n
враженнями гостей від безалкогольних, алкогольних напоїв, кави\n
необхідність купівлі інвентарю на бар\n
та все що пов’язане з баром та його командою 🙌🏻'''

PAYMENT_MESSAGE = '''це фінансова група ресторану\n
куди надсилаємо фото усіх банківських накладних\n
та вирішуємо питання з їхньою оплатою або відтермінуванням'''

MESSAGES_FOR_CHANNELS = {
    Channels.wa_resto_hall_channel.value: RESTO_HALL_MESSAGE,
    Channels.operations_channel.value: OPERATIONS_MESSAGE,
    Channels.site_orders_channel.value: SITE_ORDERS_MESSAGE,
    Channels.cash_flow_channel.value: CASH_FLOW_MESSAGE,
    Channels.wa_kitchen_channel.value: KITCHEN_MESSAGE,
    Channels.wa_bar_channel.value: BAR_MESSAGE,
    Channels.wa_payment_of_bills_channel.value: PAYMENT_MESSAGE,
}


async def start_adding(update, context):
    reply_keyboard = [['Cancel']]
    await update.message.reply_text(
        'Будь ласка додайте нового працівника\n\n'
        'Username:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return USERNAME


async def collect_username(update, context):
    if update.message.text == 'Cancel':
        return await cancel(update)

    context.user_data['username'] = update.message.text
    reply_keyboard = [['Cancel']]
    await update.message.reply_text(
        'Дата у форматі dd-mm-YYYY:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return DATE


async def collect_date(update, context):
    if update.message.text == 'Cancel':
        return await cancel(update)
    context.user_data['date'] = update.message.text
    roles = [r.value for r in Roles]
    await update.message.reply_text(
        f'Роль ({", ".join(roles)}):'
    )
    return ROLE


async def collect_role(update, context):
    context.user_data['role'] = update.message.text
    # Get the collected user information
    user_info = {
        'username': context.user_data['username'],
        'role': context.user_data['role'],
        'date': context.user_data['date']
    }

    if user_info.get('username') and not user_info.get('username').startswith('@'):
        user_info['username'] = f'@{user_info.get("username")}'

    await add_members(user_info, update, context)

    return ConversationHandler.END


async def onboarding_message(user_info, context):
    role = user_info.get('role').lower()
    link = ONBOARDING_LINKS.get(role)
    if not CHANNELS_BY_ROLE.get(role):
        print('Cannot find such role')
        return

    for channel in CHANNELS_BY_ROLE.get(role):
        if not MESSAGES_FOR_CHANNELS.get(channel):
            continue
        message = f'{user_info.get("username")}, {MESSAGES_FOR_CHANNELS.get(channel)}'
        if channel == Channels.operations_channel.value:
            message += link
        await context.bot.send_message(
            chat_id=str(channel),
            text=message
        )


async def add_members(user_info, update, context):
    role = user_info.get('role').lower()
    channels_to_add = CHANNELS_BY_ROLE.get(role)
    user_data = [
        *user_info.values(),
        'false',
    ]
    try:
        await add_member(user_info['username'], channels_to_add)
    except Exception as e:
        print(e)
        await update.message.reply_text(
            'Упс!\nЩось пішло не так(\nСпробуйте ще раз',
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        add_user_data(user_data)
        await update.message.reply_text(
            'Інформація про працівника успішно збережена!',
            reply_markup=ReplyKeyboardRemove()
        )
        await onboarding_message(user_info, context)


async def cancel(update):
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('add_employee', start_adding)],
    states={
        USERNAME: [MessageHandler(TEXT, collect_username)],
        DATE: [MessageHandler(TEXT, collect_date)],
        ROLE: [MessageHandler(TEXT, collect_role)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


async def echo(update, context):
    chat_id = update.effective_chat.id
    print(update.message.text)
    print("chart_id: " + str(chat_id))
    if bot_has_to_react(update):
        await context.bot.send_message(
            update.effective_chat.id, reply_to_message_id=update.message.message_id, text='🥰'
        )


def bot_has_to_react(update):
    if not update.effective_message.reply_to_message:
        return False
    if update.effective_message.reply_to_message and not \
            update.effective_message.reply_to_message.from_user.is_bot == True:
        return False
    if re.search(r'дякую|навзаєм', update.message.text, re.IGNORECASE):
        return True
    return False


echo_handler = MessageHandler(TEXT & (~COMMAND), echo)


def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(main(event, context))


async def main(event, context):
    # Initialize handlers
    application.add_handler(order_handler)
    application.add_handler(zvit_handler)
    application.add_handler(kasa_handler)
    application.add_handler(rocket_handler)
    application.add_handler(conv_handler)
    application.add_handler(echo_handler)

    try:
        await application.initialize()
        await application.process_update(
            Update.de_json(json.loads(event["body"]), application.bot)
        )

        return {
            'statusCode': 200,
            'body': 'Success'
        }

    except Exception as exc:
        return {
            'statusCode': 500,
            'body': 'Failure'
        }

if __name__ == '__main__' and env == 'dev':
    application.add_handler(order_handler)
    application.add_handler(zvit_handler)
    application.add_handler(kasa_handler)
    application.add_handler(rocket_handler)
    application.add_handler(conv_handler)
    application.add_handler(echo_handler)
    application.run_polling()
