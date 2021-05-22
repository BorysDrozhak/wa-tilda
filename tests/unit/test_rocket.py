from tests.unit.data.rocket_order_examples import example1, example_total1
from utils.rocket import parse_rocket_fmt, parse_total_kassa


def test_example1():
    assert parse_rocket_fmt(example1) == '''    Кеш = 805.7
    Безнал = 3755.4
    Total = 4561.1'''


def test_total_tip():
    # чай 85
    assert parse_total_kassa(example_total1) == '''Каса 2021-05-13\n\nРазом: 13268.5\nчай: 85.0?\n\n Not a bad day suckers. Total is 13268.5?\nHope you can more to impress me 🤗'''
