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
