# -*- coding: utf-8 -*-
from http import HTTPStatus

from tests.unit.data.rocket_order_examples import (example1, example_total1,
                                                   example_total2,
                                                   example_total3, resto_record_data,
                                                   delivery_record_data, example_total4)
from utils.rocket import parse_rocket_fmt, parse_total_kassa
from utils.weather_cli import get_whether_forecast


def test_example1():
    assert parse_rocket_fmt(example1) == ''''''


def test_total_tip(mocker):
    # чай 85

    mocker.patch('utils.rocket.get_previous_date_total', return_value='10800')
    mock_gspread = mocker.patch('utils.rocket.get_records')
    mock_gspread.return_value = delivery_record_data, resto_record_data
    assert parse_total_kassa(example_total1, 'dev') == (
        'Каса 2021-05-13 - ВП: 7083 - 39%\n'
        '(МТ ВП: 10800 -52%)\n'
        'Доставка: 3719\n'
        'Зал ресторану: 7810\n'
        'Разом: 11529\n'
        'чай: 85.0?\n'
        f"{get_whether_forecast()}"
    )

    assert parse_total_kassa(example_total2, 'dev') == (
        'Каса 2021-06-03 - ВП: 8754 - 38%\n'
        '(МТ ВП: 10800 -23%)\n'
        'Доставка: 2633\n'
        'Зал ресторану: 11480\n'
        'Разом: 14113\n'
        'Не сходиться z-звіт з айко продажем на:474.5\n'
        f"{get_whether_forecast()}"
    )

    assert parse_total_kassa(example_total3, 'dev') == (
        'Каса 2021-06-03 - ВП: 117700 - 40%\n'
        '(МТ ВП: 10800 91%)\n'
        'Доставка: 81959\n'
        'Зал ресторану: 111490\n'
        'Разом: 193449\n'
        'Не сходиться z-звіт з айко продажем на:474.5'
        '\n\nYa perdolive'
        '\nВав! Новий рекорд на доставці! Був 42560 31.12.2022, а тепер 81959.0'
        '\nВав! Новий рекорд в залі ретсорану! Був 31845 26.12.2022, а тепер 111490.0\n'
        f"{get_whether_forecast()}"
    )
    assert parse_total_kassa(example_total4, 'dev') == (
        'Каса 2023-05-13 - ВП: 39105 - 40%\n'
        '(МТ ВП: 10800 73%)\n'
        'Доставка: 35000\n'
        'Зал ресторану: 30000\n'
        'Разом: 65000\n'
        '\n'
        'Ya perdolive\n'
        'До рекорду в залі ресторану недотягнули.Досі рекорд 31845, якби мали ще 2 '
        'чека - то мали б новий\n'
    )


def test_total_none_previous_week(mocker):
    mocker.patch('utils.rocket.get_previous_date_total', return_value=None)
    mock_gspread = mocker.patch('utils.rocket.get_records')
    mock_gspread.return_value = delivery_record_data, resto_record_data
    assert parse_total_kassa(example_total1, 'dev') == (
        'Каса 2021-05-13 - ВП: 7083 - 39%\n'
        'Доставка: 3719\n'
        'Зал ресторану: 7810\n'
        'Разом: 11529\n'
        'чай: 85.0?\n'
        f"{get_whether_forecast()}"
    )


def test_total_api_exception_previous_week(mocker):
    prev = mocker.patch('utils.gspread_api.gspread.service_account', return_value=None)
    prev.side_effect = Exception(HTTPStatus.GATEWAY_TIMEOUT)
    mock_gspread = mocker.patch('utils.rocket.get_records')
    mock_gspread.return_value = {}, {}
    assert parse_total_kassa(example_total1, 'dev') == (
        'Каса 2021-05-13 - ВП: 7083 - 39%\n'
        'Доставка: 3719\n'
        'Зал ресторану: 7810\n'
        'Разом: 11529\n'
        'чай: 85.0?\n'
        f"{get_whether_forecast()}"
    )
