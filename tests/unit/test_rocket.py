# -*- coding: utf-8 -*-

from tests.unit.data.rocket_order_examples import (example1, example_total1,
                                                   example_total2,
                                                   example_total3)
from utils.rocket import parse_rocket_fmt, parse_total_kassa


def test_example1():
    assert parse_rocket_fmt(example1) == '''Rocket Кеш = 805.7
Rocket Безнал = 3755.4
Rocket Total = 4561.1'''


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
        'Каса 2021-06-03 - Разом: 242996.3\nДоставка: 131516.3\nЗал ресторану: 111480.0'
        '\nНе сходиться z-звіт з айко продажем на:474.5'
        '\n\nБл* ото жесть! Даніла ю а крезі! Так тримати crazy motherfuckers!!'
        '\nВав! Новий рекорд на доставці! Був 16151 09.04, а тепер 131516.3'
        '\nВав! Новий рекорд в залі ретсорану! Був 23665 12.06, а тепер 111480.0'
    )
