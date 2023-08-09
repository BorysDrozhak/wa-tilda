import datetime

from weather import Weather

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
    'few clouds: 11-25%': '🌤️',
    'scattered clouds': '🌥️',
    'broken clouds': '☁️',
    'overcast clouds': '☁️',
}


class DailyWeather:
    weather_data = []


daily_weather = DailyWeather()


def get_weather():
    try:
        wttr = Weather(temperature_unit=None)
        forecast = wttr.fetch_weather(city='Lviv', only_temp=False)
    except:
        return None

    return forecast


def save_weather():
    start = datetime.time(9, 0, 0)
    end = datetime.time(23, 00, 0)
    now = datetime.datetime.now().time()
    if not now > start or not now < end:
        return
    current_weather = get_weather()
    if not current_weather:
        return

    current_time = datetime.datetime.now()
    time = current_time.strftime('%H:%M')
    if not any(w['time'] == time for w in daily_weather.weather_data):
        daily_weather.weather_data.append({
            'time': time,
            'weather_desc': current_weather.get('Description: '),
            'feels': current_weather.get('Temperature In Celsius: ')
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
        weather_string += f"{time}{emoji} {temp}\n"

    daily_weather.weather_data.clear()
    return weather_string
