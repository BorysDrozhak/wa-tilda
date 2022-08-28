# -*- coding: utf-8 -*-

from tests.unit.data.rocket_order_examples import (example1, example_total1,
                                                   example_total2,
                                                   example_total3)
from utils.rocket import parse_rocket_fmt, parse_total_kassa


def test_example1():
    assert parse_rocket_fmt(example1) == '''Flashback Кеш = 0
Flashback Безнал = 0
Flashback Total = 0'''


def test_total_tip():
    # чай 85
    assert parse_total_kassa(example_total1) == (
        'Каса 2021-05-13 - Разом: 13268\n'
        'Доставка: 5458\n'
        'Зал ресторану: 7810\n'
        'чай: 85.0?'
    )

    assert parse_total_kassa(example_total2) == (
        'Каса 2021-06-03 - Разом: 19671\nДоставка: 8191\nЗал ресторану: 11480'
        '\nНе сходиться z-звіт з айко продажем на:474.5'
        '\n\nВав! Маю надію ви всі добре почуваєтесь, бережіть себе і будьте бережні, як будете їхати додомку ❤️'
    )

    assert parse_total_kassa(example_total3) == (
        'Каса 2021-06-03 - Разом: 243008\nДоставка: 131518\nЗал ресторану: 111490'
        '\nНе сходиться z-звіт з айко продажем на:474.5'
        '\n\nYa perdolive'
        '\nВав! Новий рекорд на доставці! Був 21155 13.01.21, а тепер 131518.3'
        '\nВав! Новий рекорд в залі ретсорану! Був 31845 26.12, а тепер 111490.0'
    )
