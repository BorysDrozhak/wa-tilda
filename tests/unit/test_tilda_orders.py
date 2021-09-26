# -*- coding: utf-8 -*-

import pytest
from tests.unit.data.tilda_orders import (answer1, answer2, answer3, answer4,
                                          example1, example2, example3,
                                          example4)
from utils.tilda import parse_order


@pytest.mark.parametrize(
    "tilda_order,parsed_answer",
    [
        (example1, answer1),
        (example2, answer2),
        (example3, answer3),
        (example4, answer4),
    ],
)
def test_example(tilda_order, parsed_answer):
    text, text_client = parse_order(tilda_order)
    assert text == parsed_answer
