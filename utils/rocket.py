import datetime


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
    Загально = 
    Z-звіт   =

LiqPay доставки = 

Rocket
{parse_rocket_fmt(text)}

Готівка в касі:
"""


def parse_rocket_fmt(text):
    # take copy past list from rocket app and convert to meaningful info
    if "№" not in text:
        return 'No Rocket orders passed'

    l = []
    for i in text.split("\n"):
        if "№" in i:
            l.append({"price": 0, "type": ""})
        elif "UAH" in i:
            l[-1]["price"] = float(i.split(" ")[0].replace(',', ''))
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

    return f'''    Кеш = {total["cash"]}
    Безнал = {total["credit_card"]}
    Total = {total["total"]}'''


def parse_total_kassa(text):
    total = 0.0
    terminal_passed = False
    terminal_total = 0
    z_zvit = 0
    for line in text.split('\n'):
        if "Каса 202" in line:
            name = line
        elif "Загально =" in line:
            total += float(line.split('=')[1].strip())
        elif "Total =" in line:
            total += float(line.split('=')[1].strip())
        elif "LiqPay доставки =" in line:
            total += float(line.split('=')[1].strip())
        if "Термінал" in line:
            terminal_passed = True
        if "Загально =" in line and terminal_passed is True:
            terminal_passed = False
            terminal_total = float(line.split('=')[1].strip())
        if "Z-звіт" in line:
            z_zvit = float(line.split('=')[1].strip())
    delta = terminal_total - z_zvit
    tips = 0
    alarm = False
    if delta < 0:
        tips = delta * -1.0
    elif delta > 0:
        alarm = True

    if tips != 0:
        return f"{name.strip('.')}\n\nРазом: {total}\nчай: {tips}?"
    elif alarm:
        return f"{name.strip('.')}: {total}\n\n Не сходиться z-звіт з айко продажем на:{delta}"
    else:
        return f"{name.strip('.')}: {total}"
