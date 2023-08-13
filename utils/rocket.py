# -*- coding: utf-8 -*-

import datetime
import dateutil.parser as dparser

from utils.gspread_api import add_history, get_previous_date_total, get_records, update_total_records
from utils.weather_cli import get_whether_forecast
from const import (
    DELIVERY_NET_RATE,
    DAILY_SPEND,
    BOLT_DELIVEY_NET_RATE,
    GLOVO_DELIVEY_NET_RATE,
    RESTO_CASH_NET_RATE,
    RESTO_CARD_NET_RATE,
    SHAKE_TO_PAY_NET_RATE,
    TOTAL_NET_RATE,
    AVERAGE_BILL_AMOUNT,
    PERCENTAGE_THRESHOLD
)


def parse_rocket(text):
    return f"""

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

{parse_rocket_fmt(text)}

Glovo Кеш = 
Glovo Безнал = 
Glovo Total = 

Bolt Кеш = 
Bolt Безнал = 
Bolt Total = 

Готівка в касі:
"""


def parse_rocket_fmt(text):
    # take copy past list from rocket app and convert to meaningful info
    if "arrow_right_alt" not in text:
        return "No Rocket orders passed"

    l = []
    for i in text.split("\n"):
        if (
            len(i) >= 7
            and "UAH" not in i
            and " " not in i.rstrip(" ")
            and "arrow" not in i
            and ":" not in i
            and "." not in i
            and "money" not in i
            and "credit_card" not in i
        ) or "№" in i:
            l.append({"price": 0, "type": ""})
        elif "UAH" in i:
            l[-1]["price"] = float(i.split(" ")[0].replace(",", ""))
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
    total["total"] = round(total["credit_card"] + total["cash"], 2)

    return f""""""


def parse_number_in_zvit(line):
    return float(line.split("=")[1].strip().split(" ")[0].replace(",", "."))


def parse_total_kassa(text, env):
    total = 0.0
    total_delivery = 0.0
    total_resto = 0.0
    total_main = 0.0
    terminal_passed = False
    # rocket_passed = False
    terminal_total = 0
    z_zvit = 0
    data = []
    zvit_date = datetime.date.today().strftime('%m/%d/%Y')
    week_difference = 0
    total_net_profit = 0.0
    for line in text.split("\n"):
        if "Каса 202" in line:
            name = line.strip(".")
            try:
                zvit_date = dparser.parse(name, fuzzy=True)
            except Exception as e:
                print(e)
        elif "Загально =" in line or "Total =" in line:
            total += parse_number_in_zvit(line)
        elif "Ресторан =" in line:
            total_resto += parse_number_in_zvit(line)
            total_net_profit += parse_number_in_zvit(line) * (1 - RESTO_CASH_NET_RATE)
        elif "LiqPay доставки =" in line:
            price_liqpay = parse_number_in_zvit(line)
            total_delivery += price_liqpay
            total += price_liqpay
            total_net_profit += parse_number_in_zvit(line) * (1 - DELIVERY_NET_RATE)
        if "Доставка =" in line:
            total_delivery += parse_number_in_zvit(line)
            total_net_profit += parse_number_in_zvit(line) * (1 - DELIVERY_NET_RATE)
        if "Термінал" in line:
            terminal_passed = True
        if "Загально =" in line and terminal_passed is True:
            terminal_passed = False
            terminal_total = parse_number_in_zvit(line)
        if "Total Glovo =" in line or "Glovo Total =" in line:
            total_delivery += parse_number_in_zvit(line)
            total_net_profit += parse_number_in_zvit(line) * (1 - GLOVO_DELIVEY_NET_RATE)
        if "Total Bolt =" in line or "Bolt Total =" in line:
            print(total_delivery)
            total_delivery += parse_number_in_zvit(line)
            print(total_delivery)
            total_net_profit += parse_number_in_zvit(line) * (1 - BOLT_DELIVEY_NET_RATE)
        if "Z-звіт" in line:
            z_zvit = parse_number_in_zvit(line)
        if "Shake to pay" in line:
            total_resto += parse_number_in_zvit(line)
            total += parse_number_in_zvit(line)  # shake to pay and liqpay added separetly to total
            total_net_profit += parse_number_in_zvit(line) * (1 - SHAKE_TO_PAY_NET_RATE)
    total_net_profit -= total_net_profit * TOTAL_NET_RATE
    data.extend(
        [
            zvit_date.strftime('%m/%d/%Y'),
            str(int(total_resto)),
            str(int(total_delivery)),
            str(int(total)),
            str(int(total_net_profit)),
        ]
    )
    if data:
        add_history(data, zvit_date.strftime('%m/%d/%Y'))
    previous_week_total = get_previous_date_total(zvit_date - datetime.timedelta(days=7))
    if previous_week_total:
        week_difference = compute_week_difference(previous_week_total, total_net_profit)
    delta = terminal_total - z_zvit
    tips = 0
    alarm = False
    if delta < 0:
        tips = delta * -1.0
    elif delta > 0:
        alarm = True

    new_records = ""
    delivery_records_dict, resto_records_dict = get_records()
    print(resto_records_dict)
    resto_records_total, delivery_records_total = 0, 0
    if delivery_records_dict.get('total') and resto_records_dict.get('total'):
        resto_records_total = int(resto_records_dict.get('total'))
        delivery_records_total = int(delivery_records_dict.get('total'))

    if delivery_records_total != 0 and total_delivery > delivery_records_total:
        new_records += (
            f"\nВав! Новий рекорд на доставці! "
            f"Був {delivery_records_total} {delivery_records_dict.get('date')}, а тепер {total_delivery}"
        )
        delivery_record_data = [str(int(total_delivery)), zvit_date.strftime('%m/%d/%Y')]
        update_total_records(delivery_record_data, 'Доставка')
        delivery_records_total = total_delivery
    if resto_records_total != 0 and total_resto > resto_records_total:
        new_records += f"\nВав! Новий рекорд в залі ретсорану!" \
                       f" Був {resto_records_total} {resto_records_dict.get('date')}, а тепер {total_resto}"
        resto_record_data = [str(int(total_resto)), zvit_date.strftime('%m/%d/%Y')]
        update_total_records(resto_record_data, 'Зал')
        resto_records_total = total_resto

    is_almost_new_delivery_record = total_delivery >= delivery_records_total - (PERCENTAGE_THRESHOLD * total_delivery)
    is_almost_new_resto_record = total_resto >= resto_records_total - (PERCENTAGE_THRESHOLD * total_resto)
    if not new_records and resto_records_dict and is_almost_new_resto_record:
        bills = int((resto_records_total - total_resto) / AVERAGE_BILL_AMOUNT)
        new_records += f"\nДо рекорду в залі ресторану недотягнули." \
                       f"Досі рекорд {resto_records_total}, якби мали ще {bills} чека - то мали б новий"
    if not new_records and delivery_records_dict and is_almost_new_delivery_record:
        bills = int((delivery_records_total - total_delivery) / AVERAGE_BILL_AMOUNT)
        new_records += f"\nДо рекорду на доставці недотягнули." \
                       f"Досі рекорд {delivery_records_total}, якби мали ще {bills} чека - то мали б новий"
    if total > 50000:
        congrats = f"\n\nYa perdolive"
    elif total > 45000:
        congrats = (
            f"\n\nТааакс, ви що хочите щоб ваш бот отримав інфаркт!? О_О. У вас все добре, які ж ви молодці!!❤️❤️"
        )
    elif total > 40000:
        congrats = f"\n\nЕй Йоу! Рілі???? О_О. ВАУ! Я хоч і бот в телеграмі, але вас дуже люблю <3"
    elif total > 30000:
        congrats = f"\n\nНу і пупсики!! Вау Вау Вау"
    elif total > 18000:
        congrats = (
            f"\n\nВав! Маю надію ви всі добре почуваєтесь, бережіть себе і будьте бережні, як будете їхати додомку ❤️"
        )
    elif total > 15000:
        congrats = f"\n\nНепогано, але для лютого :) Певен, ви можете ліпше 🤗"
    else:
        congrats = ""

    tip_check = ""
    if tips != 0:
        tip_check = f"\nчай: {tips}?"
    elif alarm:
        tip_check = f"\nНе сходиться z-звіт з айко продажем на:{delta}"
    previous_week = ""
    if previous_week_total and week_difference:
        previous_week = f"\n(МТ ВП: {previous_week_total} {week_difference}%)"
    total_net_rate = 100 - int(total_net_profit/total*100)
    return (
        f"{name} - ВП: {int(total_net_profit)} - {total_net_rate}%"
        f"{previous_week}"
        f"\nДоставка: {int(total_delivery)}"
        f"\nЗал ресторану: {int(total_resto)}"
        f"\nРазом: {int(total)}"
        f"{tip_check}{congrats}{new_records}\n"
        f"{get_whether_forecast()}"
    )


def compute_week_difference(previous_week_total, total):
    try:
        previous_week_total = int(previous_week_total)
    except Exception as e:
        print(e)
        return
    else:
        return 100 - int(previous_week_total/total*100)
