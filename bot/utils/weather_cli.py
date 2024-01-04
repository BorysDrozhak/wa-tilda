import datetime

import pytz
from weather import Weather

from .gspread_api import add_weather_data, get_records_range

kyiv_timezone = pytz.timezone('Europe/Kiev')

weather_smiles = {
    'clear sky': '☀️',
    'thunderstorm with light rain': '⛈️',
    'thunderstorm with rain': '⛈️',
    'thunderstorm with heavy rain': '⛈️',
    'light thunderstorm': '⛈️',
    'thunderstorm': '⛈️',
    'heavy thunderstorm': '⛈️',
    'ragged thunderstorm': '⛈️',
    'thunderstorm with light drizzle': '⛈️',
    'thunderstorm with drizzle': '⛈️',
    'thunderstorm with heavy drizzle': '⛈️',
    'light intensity drizzle': '🌨️',
    'drizzle': '🌧️',
    'heavy intensity drizzle': '🌧️',
    'light intensity drizzle rain': '🌧️',
    'drizzle rain': '🌧️',
    'heavy intensity drizzle rain': '🌧️',
    'shower rain and drizzle': '🌧️',
    'heavy shower rain and drizzle': '🌧️',
    'shower drizzle': '🌧️',
    'light rain': '🌦️',
    'moderate rain': '🌦️',
    'heavy intensity rain': '🌦️',
    'very heavy rain': '🌦️',
    'extreme rain': '🌦️',
    'freezing rain': '🌧️',
    'light intensity shower rain': '🌧️',
    'shower rain': '🌧️',
    'heavy intensity shower rain': '🌧️',
    'ragged shower rain': '🌧️',
    'light snow': '❄️',
    'snow': '❄️',
    'heavy snow': '❄️',
    'sleet': '❄️',
    'light shower sleet': '❄️',
    'shower sleet': '❄️',
    'light rain and snow': '❄️',
    'rain and snow': '❄️',
    'light shower snow': '❄️',
    'shower snow': '❄️',
    'heavy shower snow': '❄️',
    'mist': '😶‍🌫️',
    'smoke': '😶‍🌫️',
    'haze': '😶‍🌫️',
    'sand/dust whirls': '😶‍🌫️',
    'fog': '😶‍🌫️',
    'sand': '😶‍🌫️',
    'dust': '😶‍🌫️',
    'volcanic ash': '😶‍🌫️',
    'squalls': '😶‍🌫️',
    'tornado': '😶‍🌫️',
    'few clouds': '🌤️',
    'scattered clouds': '🌥️',
    'broken clouds': '☁️',
    'overcast clouds': '☁️',
}


def get_weather():
    try:
        wttr = Weather(temperature_unit=None)
        forecast = wttr.fetch_weather(city='Lviv', only_temp=False)
    except:
        return None

    return forecast


def save_weather():
    daily_weather = []
    start = datetime.time(9, 0, 0, tzinfo=kyiv_timezone)
    end = datetime.time(23, 00, 0, tzinfo=kyiv_timezone)
    now = datetime.datetime.now(tz=kyiv_timezone)
    if not now.time() > start or not now.time() < end:
        return

    current_weather = get_weather()
    if not current_weather:
        return

    weather_data = get_records_range('wa-weather', now.date())
    time = now.strftime('%H:%M')
    if not any(w['time'] == time for w in weather_data):
        daily_weather.extend(
            [
                now.date().strftime('%m/%d/%Y'),
                time,
                current_weather.get('Description: '),
                current_weather.get('Temperature In Celsius: ')
            ]
        )
        add_weather_data(daily_weather)


def get_whether_forecast():
    try:
        weather_description = get_records_range('wa-weather', datetime.datetime.now(tz=kyiv_timezone).date())
    except Exception as e:
        print(e)
        return ''

    weather_string = ''
    if not weather_description:
        return ''

    for wd in weather_description:
        weather_smile = weather_smiles.get(wd.get('weather_desc'))
        emoji = weather_smile if weather_smile else wd.get('weather_desc')
        time = wd.get('time')
        temp = wd.get('feels')
        weather_string += f"{time}{emoji} {temp}\n"

    return weather_string
