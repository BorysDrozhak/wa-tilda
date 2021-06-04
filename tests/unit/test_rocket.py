from tests.unit.data.rocket_order_examples import (example1, example_total1,
                                                   example_total2,
                                                   example_total3)
from utils.rocket import parse_rocket_fmt, parse_total_kassa


def test_example1():
    assert parse_rocket_fmt(example1) == '''    Кеш = 805.7
    Безнал = 3755.4
    Total = 4561.1'''


def test_total_tip():
    # чай 85
    assert parse_total_kassa(example_total1) == (
        'Каса 2021-05-13 - Разом: 13268.5\nДоставка: 5458.5\nчай: 85.0?'
        '\n\nНепогано, але для минулого місяцю. Маю надію ви здивуєте мене іншими цифрами 🤗'
    )

    assert parse_total_kassa(example_total2) == (
        'Каса 2021-06-03 - Разом: 19571.3\nДоставка: 8091.3'
        '\nНе сходиться z-звіт з айко продажем на:474.5'
        '\n\nНепогано, але для минулого місяцю. Маю надію ви здивуєте мене іншими цифрами 🤗'
    )

    assert parse_total_kassa(example_total3) == (
        'Каса 2021-06-03 - Разом: 242996.3\nДоставка: 131516.3'
        '\nНе сходиться z-звіт з айко продажем на:474.5'
        '\n\nНепогано, але для минулого місяцю. Маю надію ви здивуєте мене іншими цифрами 🤗'
        '\nВав! Новий рекорд на доставці! Був 16151 09.04, а тепер 131516.3'
        '\nВав! Новий рекорд в залі ретсорану! Був 111480.0 13.03, а тепер 111480.0'
    )
