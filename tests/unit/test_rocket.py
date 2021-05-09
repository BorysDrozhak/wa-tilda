from tests.unit.data.rocket_order_examples import example1
from utils.rocket import parse_rocket


def test_default():
    assert parse_rocket('') == 'No Rocket orders passed'


def test_example1():
    assert parse_rocket(example1) == 'Кеш: 805.7\nБезнал: 3755.4\nTotal: 4561.1'
