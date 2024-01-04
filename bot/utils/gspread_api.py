import json
import datetime
import os
import tempfile

import gspread


CREDENTIALS_DICT = {
    "type": os.environ.get('GC_TYPE'),
    "project_id": os.environ.get('GC_PROJECT_ID'),
    "private_key_id": os.environ.get('GC_PRIVATE_KEY_ID'),
    "private_key": os.environ.get('GC_PRIVATE_KEY'),
    "client_email": os.environ.get('GC_CLIENT_EMAIL'),
    "client_id": os.environ.get('GC_CLIENT_ID'),
    "auth_uri": os.environ.get('GC_AUTH_URI'),
    "token_uri": os.environ.get('GC_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.environ.get('GC_AUTH_PROVIDER'),
    "client_x509_cert_url": os.environ.get('GC_CLIENT')
}


def create_creds_json(creds):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        json.dump(creds, temp_file)
        return temp_file


def add_history(data, zvit_date, creds=None):
    if not creds or creds.closed:
        creds = create_creds_json(CREDENTIALS_DICT)
    try:
        gc = gspread.service_account(creds.name)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-history-reserved')
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


def get_previous_date_total(date, creds=None):
    if not creds or creds.closed:
        creds = create_creds_json(CREDENTIALS_DICT)
    try:
        gc = gspread.service_account(creds.name)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-history-reserved')
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


def update_total_records(data, record_name, creds=None):
    if not creds or creds.closed:
        creds = create_creds_json(CREDENTIALS_DICT)
    try:
        gc = gspread.service_account(creds.name)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-records')
    except:
        return

    existing_row = wks.find(record_name)

    try:
        col_to_update = 2
        for d in data:
            wks.update_cell(existing_row.row, col_to_update, d)
            col_to_update += 1
    except Exception as e:
        print(e)


def get_records(creds=None):
    gc_creds = CREDENTIALS_DICT
    if not creds or creds.closed:
        creds = create_creds_json(gc_creds)

    try:
        gc = gspread.service_account(creds.name)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-records')
    except:
        return {}, {}

    data = wks.get_all_records()
    resto_data, delivery_data = {}, {}
    print(data)

    for record in data:
        if record.get('name') == 'Зал':
            resto_data = record
        elif record.get('name') == 'Доставка':
            delivery_data = record

    return delivery_data, resto_data


def add_user_data(data, creds=None):
    if not creds or creds.closed:
        creds = create_creds_json(CREDENTIALS_DICT)
    try:
        gc = gspread.service_account(creds.name)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-users')
    except:
        return

    return wks.append_row(data)


def update_empl_trial(creds=None):
    if not creds or creds.closed:
        creds = create_creds_json(CREDENTIALS_DICT)
    try:
        gc = gspread.service_account(creds.name)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-users')
    except:
        return

    existing_rows = wks.get_all_records()
    today = datetime.date.today()
    col_to_update = 4
    try:
        for row in existing_rows:
            dateObj = datetime.datetime.strptime(row.get('date'), '%d-%m-%Y').date()
            if row.get('trial') != 'true' and dateObj <= today - datetime.timedelta(days=30):
                row_to_update = wks.find(row.get('username'))
                print(row_to_update.row)
                wks.update_cell(row_to_update.row, col_to_update, 'true')
    except Exception as e:
        print(e)


def get_employees(creds=None):
    if not creds or creds.closed:
        creds = create_creds_json(CREDENTIALS_DICT)
    try:
        gc = gspread.service_account(creds.name)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-users')
    except:
        return

    employees = wks.get_all_records()

    return employees


def get_all_records(table_name, creds=None):
    if not creds or creds.closed:
        creds = create_creds_json(CREDENTIALS_DICT)
    try:
        gc = gspread.service_account(creds.name)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet(table_name)
    except:
        return

    records = wks.get_all_records()
    return records


def add_weather_data(data, creds=None):
    if not creds or creds.closed:
        creds = create_creds_json(CREDENTIALS_DICT)
    try:
        gc = gspread.service_account(creds.name)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet('wa-weather')
    except:
        return

    return wks.append_row(data)


def get_records_range(table_name, date, creds=None, records_range=None):
    if not creds or creds.closed:
        creds = create_creds_json(CREDENTIALS_DICT)
    try:
        gc = gspread.service_account(creds.name)
        sh = gc.open('wa-accounting')
        wks = sh.worksheet(table_name)
    except:
        return
    headers = wks.row_values(1)
    records = wks.findall(date.strftime('%m/%d/%Y'))
    if not records:
        return []
    if records_range:
        records = wks.get_values(f'{records[0].address}:E{records[0].row + records_range}')
    else:
        records = wks.get_values(f'{records[0].address}:D{records[-1].row}')

    return form_response(headers, records)


def form_response(headers, values):
    resp = []
    if len(headers) == len(values[0]):
        for value in values:
            dictionary = dict(zip(headers, value))
            resp.append(dictionary)
    else:
        resp = []

    return resp
