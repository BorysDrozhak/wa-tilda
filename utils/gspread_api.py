import os

import gspread

GC_CREDS = os.getenv('WA_CREDS')


def add_history(data):
    try:
        gc = gspread.service_account(GC_CREDS)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-history')
    except:
        return
    wks.append_row(data)


def get_previous_date_total(date):
    try:
        gc = gspread.service_account(GC_CREDS)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-history')
    except:
        return
    previous_weekday_row = wks.find(date.strftime('%m/%d/%Y'))
    if not previous_weekday_row:
        return
    previous_weekday_row = previous_weekday_row.row
    previous_week_total = wks.acell(f'D{previous_weekday_row}')
    if not previous_week_total:
        return
    return previous_week_total.value
