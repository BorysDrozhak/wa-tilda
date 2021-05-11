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
    total["total"] = total["credit_card"] + total["cash"]

    return f'''    Кеш = {total["cash"]}
    Безнал = {total["credit_card"]}
    Total = {total["total"]}'''
