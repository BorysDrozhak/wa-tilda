# -*- coding: utf-8 -*-

from tests.unit.data.weather_data import example_weather_1, expected_weather_string
from utils.weather import get_whether_forecast, DailyWeather


def test_weather_data():
    DailyWeather.weather_data = example_weather_1
    weather = get_whether_forecast()
    assert weather == expected_weather_string
    DailyWeather.weather_data.clear()
