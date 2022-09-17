import datetime

from pywttr import Wttr


weather_smiles = {
    'Partly cloudy': '🌤️',
    'Overcast': '🌥️',
    'Light drizzle': '🌦️',
    'Light rain': '🌦️',
    'Patchy rain possible': '🌦️',
    'Cloudy': '☁️',
    'Mist': '😶‍🌫️',
    'Sunny': '☀️',
    'Clear': '☀️',
    'Rainy': '🌧️',
    'Windy': '🌬️',
    'Snowy': '🌨️',
    'Light rain shower': '🌧️',
    'Moderate rain': '🌧️',
}


class DailyWeather:
    weather_data = []


daily_weather = DailyWeather()


def get_weather():
    try:
        wttr = Wttr("Lviv")
    except:
        return None
    else:
        forecast = wttr.en()
        current_weather = forecast.current_condition[0] if forecast else None
    return current_weather


def save_weather():
    start = datetime.time(9, 0, 0)
    end = datetime.time(22, 0, 0)
    now = datetime.datetime.now().time()
    if not now > start or not now < end:
        return
    current_weather = get_weather()
    if not current_weather:
        return

    date_time_str = current_weather.local_obs_date_time
    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %I:%M %p')
    time = date_time_obj.time().hour
    daily_weather.weather_data.append({
        'time': time,
        'weather_desc': current_weather.weather_desc[0].value,
        'feels': current_weather.feels_like_c
    })


def get_whether_forecast():
    weather_description = daily_weather.weather_data
    weather_string = ''
    if not weather_description:
        return ''

    for wd in weather_description:
        weather_smile = weather_smiles.get(wd.get('weather_desc'))
        emoji = weather_smile if weather_smile else wd.get('weather_desc')
        time = wd.get('time')
        temp = wd.get('feels')
        weather_string += f"{time}{emoji} {temp}C "

    daily_weather.weather_data.clear()
    return weather_string
