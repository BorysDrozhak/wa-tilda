# -*- coding: utf-8 -*-

import datetime

from utils.gspread_api import add_history, get_previous_date_total
from utils.weather import get_whether_forecast


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
    week_difference = 0
    for line in text.split("\n"):
        if "Каса 202" in line:
            name = line.strip(".")
        elif "Загально =" in line or "Total =" in line:
            total += parse_number_in_zvit(line)
        elif "Ресторан =" in line:
            total_resto += parse_number_in_zvit(line)
        elif "LiqPay доставки =" in line:
            price_liqpay = parse_number_in_zvit(line)
            total_delivery += price_liqpay
            total += price_liqpay
        if "Доставка =" in line:
            total_delivery += parse_number_in_zvit(line)
        if "Термінал" in line:
            terminal_passed = True
        if "Загально =" in line and terminal_passed is True:
            terminal_passed = False
            terminal_total = parse_number_in_zvit(line)
        if "Total Glovo =" in line or "Glovo Total =" in line:
            total_delivery += parse_number_in_zvit(line)
        if "Total Bolt =" in line or "Bolt Total =" in line:
            print(total_delivery)
            total_delivery += parse_number_in_zvit(line)
            print(total_delivery)
        if "Z-звіт" in line:
            z_zvit = parse_number_in_zvit(line)
        if "Shake to pay" in line:
            total_resto += parse_number_in_zvit(line)
            total += parse_number_in_zvit(line)  # shake to pay and liqpay added separetly to total
    data.extend(
        [datetime.date.today().strftime('%m/%d/%Y'), total_resto, total_delivery, total]
    )
    if data:
        add_history(data)
    previous_week_total = get_previous_date_total(datetime.date.today() - datetime.timedelta(days=7))
    if previous_week_total:
        week_difference = compute_week_difference(int(previous_week_total), total)
    delta = terminal_total - z_zvit
    tips = 0
    alarm = False
    if delta < 0:
        tips = delta * -1.0
    elif delta > 0:
        alarm = True

    new_records = ""
    top_delivery = 21155
    top_delivery_date = "13.01.21"
    top_resto = 31845
    top_resto_date = "26.12"

    if total_delivery > top_delivery:
        new_records += (
            f"\nВав! Новий рекорд на доставці! Був {top_delivery} {top_delivery_date}, а тепер {total_delivery}"
        )
    if total_resto > top_resto:
        new_records += f"\nВав! Новий рекорд в залі ретсорану! Був {top_resto} {top_resto_date}, а тепер {total_resto}"

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
        previous_week = f"\n(Минулий тиждень {previous_week_total} {week_difference}%)"
    return (
        f"{name} - Разом: {int(total)}"
        f"{previous_week}"
        f"\nДоставка: {int(total_delivery)}"
        f"\nЗал ресторану: {int(total_resto)}"
        f"{tip_check}{congrats}{new_records}\n"
        f"{get_whether_forecast()}"
    )


def compute_week_difference(previous_week_total, total):
    return int((previous_week_total - total) / total * 100.0)
