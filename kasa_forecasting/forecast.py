import json
from datetime import datetime, timedelta

from workalendar.europe.ukraine import Ukraine
import pandas as pd
import statsmodels.api as sm


LAST_DAY_IN_THE_YEAR = '12/31'


def get_tomorrow_forecast(event, context):
    data = event.get('sales_data')
    if not data:
        return {
            'statusCode': 404,
            'body':  json.dumps({"message": 'Missing sales data'})
        }
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    tomorrow = datetime.today() + timedelta(days=1)
    weekday = tomorrow.strftime('%A')
    weekday_data = df[df['Date'].dt.strftime('%A') == weekday]
    model = sm.tsa.ARIMA(weekday_data['Total'], order=(3, 2, 1))
    fitted = model.fit()
    trend_fc = fitted.forecast(steps=1).values.max()
    last_year = tomorrow - timedelta(days=365)
    last_year_data = df[df['Date'].dt.date == last_year.date()]
    historical_sales = last_year_data['Total'].values[0]
    weight_historical_sales = 0.2
    weight_trend_analysis = 0.8
    if check_is_holiday(tomorrow):
        weight_historical_sales = 0.8
        weight_trend_analysis = 0.2
    forecast_total = int(weight_historical_sales * historical_sales + weight_trend_analysis * trend_fc)
    return {
        'forecast': {
            'Total': forecast_total,
            'Date': tomorrow.date().strftime('%d-%m')
        },
        'previous_year': {
            'Total': last_year_data['Total'].values[0],
            'Date': pd.to_datetime(last_year_data['Date'].values[0]).strftime('%d-%m')
        }
    }


def check_is_holiday(tomorrow):
    cal = Ukraine()
    if cal.is_holiday(tomorrow):
        return True
    if f'{tomorrow.month}/{tomorrow.day}' == LAST_DAY_IN_THE_YEAR:
        return True

    return False
