# -*- coding: utf-8 -*-

from tests.unit.data.rocket_order_examples import (example1, example_total1,
                                                   example_total2,
                                                   example_total3)
from utils.rocket import parse_rocket_fmt, parse_total_kassa


def test_example1():
    assert parse_rocket_fmt(example1) == '''Rocket Кеш = 0
Rocket Безнал = 0
Rocket Total = 0'''


def test_total_tip():
    # чай 85
    assert parse_total_kassa(example_total1) == (
        'Каса 2021-05-13 - Разом: 13268.5\n'
        'Доставка: 5458.5\n'
        'Зал ресторану: 7810.0\n'
        'чай: 85.0?'
        '\n\nНепогано, але для лютого :) Певен, ви можете ліпше 🤗'
    )

    assert parse_total_kassa(example_total2) == (
        'Каса 2021-06-03 - Разом: 19671.3\nДоставка: 8191.3\nЗал ресторану: 11480.0'
        '\nНе сходиться z-звіт з айко продажем на:474.5'
        '\n\nВав! Маю надію ви всі добре почуваєтесь, бережіть себе і будьте бережні, як будете їхати додомку ❤️'
    )

    assert parse_total_kassa(example_total3) == (
        'Каса 2021-06-03 - Разом: 243008.3\nДоставка: 131518.3\nЗал ресторану: 111490.0'
        '\nНе сходиться z-звіт з айко продажем на:474.5'
        '\n\nЕй Йоу! Рілі???? О_О. ВАУ! Я хоч і бот в телеграмі, але вас дуже люблю <3'
        '\nВав! Новий рекорд на доставці! Був 21155 13.01.21, а тепер 131518.3'
        '\nВав! Новий рекорд в залі ретсорану! Був 31845 26.12, а тепер 111490.0'
    )
