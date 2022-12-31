# -*- coding: utf-8 -*-

from tests.unit.data.rocket_order_examples import (example1, example_total1,
                                                   example_total2,
                                                   example_total3)
from utils.rocket import parse_rocket_fmt, parse_total_kassa
from utils.weather import get_whether_forecast


def test_example1():
    assert parse_rocket_fmt(example1) == ''''''


def test_total_tip():
    # чай 85
    assert parse_total_kassa(example_total1, 'dev') == (
        'Каса 2021-05-13 - Разом: 11529\n'
        'Доставка: 3719\n'
        'Зал ресторану: 7810\n'
        'чай: 85.0?\n'
        f"{get_whether_forecast()}"
    )

    assert parse_total_kassa(example_total2, 'dev') == (
        'Каса 2021-06-03 - Разом: 14113\nДоставка: 2633\nЗал ресторану: 11480'
        '\nНе сходиться z-звіт з айко продажем на:474.5\n'
        f"{get_whether_forecast()}"
    )

    assert parse_total_kassa(example_total3, 'dev') == (
        'Каса 2021-06-03 - Разом: 193449\nДоставка: 81959\nЗал ресторану: 111490'
        '\nНе сходиться z-звіт з айко продажем на:474.5'
        '\n\nYa perdolive'
        '\nВав! Новий рекорд на доставці! Був 42560 13.01.21, а тепер 81959.0'
        '\nВав! Новий рекорд в залі ретсорану! Був 31845 26.12, а тепер 111490.0\n'
        f"{get_whether_forecast()}"
    )
