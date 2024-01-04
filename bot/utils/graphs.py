import json
from datetime import timedelta, datetime
from io import BytesIO

from telegram import InputFile
import matplotlib.pyplot as plt
import numpy as np

from .lambda_operations import invoke_function_in_lambda
from .gspread_api import get_records_range, get_all_records
from .weather_cli import kyiv_timezone
from const import WA_HISTORY_TABLE, FOURTH_MONTH, NAME_OF_DAYS, MONDAY, WEEK


def get_average_data(dataset, fourth_months_ago):
    weekly_totals = {}
    weekly_counts = {}

    for entry in dataset:
        date_obj = datetime.strptime(entry['Date'], '%m/%d/%Y').date()
        if date_obj > fourth_months_ago.date():
            week_number = date_obj.isocalendar()[1]
            if week_number not in weekly_totals:
                weekly_totals[week_number] = int(entry['Total'])
                weekly_counts[week_number] = 1

            else:
                weekly_totals[week_number] += int(entry['Total'])
                weekly_counts[week_number] += 1

    weekly_averages = {}
    for week, total in weekly_totals.items():
        weekly_averages[week] = int(total / weekly_counts.get(week))

    averages = list(weekly_averages.values())

    return averages


async def build_graphs(contex, chat_id):
    today = datetime.now(tz=kyiv_timezone)
    filtered_dates, filtered_totals = [], []
    fourth_months_ago = today - timedelta(days=FOURTH_MONTH)
    four_months_ago_previous_year = fourth_months_ago - timedelta(days=365)
    if fourth_months_ago.weekday() != MONDAY:
        fourth_months_ago = fourth_months_ago - timedelta(days=fourth_months_ago.weekday())
    if four_months_ago_previous_year.weekday() != MONDAY:
        four_months_ago_previous_year = four_months_ago_previous_year - \
                                        timedelta(days=four_months_ago_previous_year.weekday())
    records = get_records_range(
        WA_HISTORY_TABLE,
        fourth_months_ago,
        creds=None,
        records_range=(today - fourth_months_ago).days
    )
    previous_year_records = get_records_range(
        WA_HISTORY_TABLE,
        four_months_ago_previous_year,
        creds=None,
        records_range=(today - fourth_months_ago).days + WEEK
    )
    if not records:
        return

    for entry in records:
        date_obj = datetime.strptime(entry['Date'], '%m/%d/%Y').date()
        if date_obj >= fourth_months_ago.date() and date_obj.weekday() == today.weekday():
            formatted_date = date_obj.strftime('%d-%m')
            filtered_dates.append(formatted_date)
            filtered_totals.append(int(entry['Total']))

    try:
        data = get_all_records(WA_HISTORY_TABLE)
        response = invoke_function_in_lambda({'sales_data': data})
        forecast_response = json.loads(response['Payload'].read())
        if forecast_response:
            filtered_totals.append(forecast_response.get('forecast').get('Total'))
            filtered_dates.append(forecast_response.get('forecast').get('Date'))

    except Exception as e:
        print(e)
        forecast_response = None

    plt.figure(figsize=(10, 6))
    plt.plot(
        filtered_dates,
        filtered_totals,
        marker='o',
        linestyle='-',
        label=f'Каса у {NAME_OF_DAYS[today.weekday()]}'
    )
    plt.xlabel('Дата')
    plt.ylabel('Каса')
    plt.title('Тендеція каси за останні чотири місяці')
    plt.grid(True)

    averages = get_average_data(records, fourth_months_ago)

    if len(filtered_dates) > len(averages):
        filtered_dates.pop()
    elif len(filtered_dates) < len(averages):
        averages.pop()

    plt.plot(filtered_dates, averages, marker='x', linestyle='--', label='Середня каса за тиждень')
    previous_year_averages = get_average_data(
        previous_year_records,
        four_months_ago_previous_year,
    )

    if len(filtered_dates) < len(previous_year_averages):
        previous_year_averages.pop()

    plt.plot(
        filtered_dates,
        previous_year_averages,
        marker='.',
        linestyle='--',
        label='Середня каса за тиждень (минулий рік)',
        linewidth=0.5
    )
    if len(filtered_dates) != filtered_totals:
        filtered_totals.pop()

    x = np.arange(len(filtered_dates))
    coefficients = np.polyfit(x, filtered_totals, 1)
    trendline = np.poly1d(coefficients)
    plt.plot(
        filtered_dates,
        trendline(x),
        linestyle='--',
        color='red',
        label=f'Лінія тренду у {NAME_OF_DAYS[today.weekday()]}'
    )
    max_y_value = max(max(filtered_totals), max(averages))
    plt.ylim(0, max_y_value)
    plt.legend()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    await contex.bot.send_photo(chat_id=chat_id, photo=InputFile(buffer, filename='graph.png'))
