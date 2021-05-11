from tests.unit.data.rocket_order_examples import example1
from utils.rocket import parse_rocket, parse_rocket_fmt


def test_example1():
    assert parse_rocket_fmt(example1) == '''    Кеш = 805.7
    Безнал = 3755.4
    Total = 4561.1'''
