import os

import gspread

GC_CREDS = os.getenv('WA_CREDS')


def add_history(data, zvit_date):
    try:
        gc = gspread.service_account(GC_CREDS)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-history')
    except:
        return
    existing_row = wks.find(zvit_date)
    if not existing_row:
        return wks.append_row(data)
    try:
        col_to_update = 1
        for d in data:
            wks.update_cell(existing_row.row, col_to_update, d)
            col_to_update += 1
    except Exception as e:
        print(e)


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
    previous_week_total = wks.acell(f'E{previous_weekday_row}')
    if not previous_week_total:
        return
    return previous_week_total.value
