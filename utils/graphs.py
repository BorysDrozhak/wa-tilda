from datetime import timedelta, datetime
from io import BytesIO

from telegram import InputFile
import matplotlib.pyplot as plt
import numpy as np

from utils.gspread_api import get_all_records
from const import WEEK, WA_HISTORY_TABLE, THREE_MONTH, NAME_OF_DAYS, MONDAY


def build_graphs(context, chat_id):
    today = datetime.today()
    records = get_all_records(WA_HISTORY_TABLE)
    filtered_dates, filtered_totals = [], []
    three_months_ago = today - timedelta(days=THREE_MONTH)
    for entry in records:
        date_obj = datetime.strptime(entry['Date'], '%m/%d/%Y').date()
        if date_obj >= three_months_ago.date() and date_obj.weekday() == today.weekday():
            formatted_date = date_obj.strftime('%d-%m')
            filtered_dates.append(formatted_date)
            filtered_totals.append(int(entry['Total']))

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
    plt.title('Тендеція каси за останні три місяці')
    plt.grid(True)
    # Initialize dictionaries to store weekly data
    weekly_totals = {}
    weekly_counts = {}

    for entry in records:
        date_obj = datetime.strptime(entry['Date'], '%m/%d/%Y').date()
        if three_months_ago.weekday() != MONDAY:
            three_months_ago = three_months_ago - timedelta(days=three_months_ago.weekday())
        if date_obj > three_months_ago.date():
            week_number = date_obj.isocalendar()[1]
            # Skip the current week (week number of today's date)
            if week_number == today.isocalendar()[1]:
                continue
            if week_number not in weekly_totals:
                weekly_totals[week_number] = int(entry['Total'])
                weekly_counts[week_number] = 1
            else:
                weekly_totals[week_number] += int(entry['Total'])
                weekly_counts[week_number] += 1

    weekly_averages = {}
    for week, total in weekly_totals.items():
        weekly_averages[week] = int(total / WEEK)

    # Plotting the weekly averages
    averages = list(weekly_averages.values())
    if len(filtered_dates) != len(averages):
        averages = averages[1:]
    plt.plot(filtered_dates, averages, marker='x', linestyle='--', label='Середня каса за тиждень')
    # Fit a linear trendline
    x = np.arange(len(filtered_dates))
    coefficients = np.polyfit(x, filtered_totals, 1)
    trendline = np.poly1d(coefficients)
    plt.plot(filtered_dates, trendline(x), linestyle='--', color='red', label='Лінія тренду')
    # Set y-axis limits to start from zero
    max_y_value = max(max(filtered_totals), max(averages))
    plt.ylim(0, max_y_value)
    # Enable legend
    plt.legend()
    # Save the graph to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Send the graph to the Telegram channel
    context.bot.send_photo(chat_id=chat_id, photo=InputFile(buffer, filename='graph.png'))
