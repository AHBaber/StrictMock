import pytest

from strict_mock.analysis import Actual


@pytest.mark.parametrize("expected, value", [
    ('("m")', Actual("m")),
    ('("m", 1)', Actual("m", 1)),
    ('("m", 1, 2, 3)', Actual("m", 1, 2, 3)),
    ('("m", "a")', Actual("m", "a")),
    ('("m", "a", "b", "c")', Actual("m", "a", "b", "c")),
    ('("m", 1, 2, "a", 3)', Actual("m", 1, 2, "a", 3)),
    ('("m", a=1)', Actual("m", a=1)),
    ('("m", a=1, b=2, c=3)', Actual("m", a=1, b=2, c=3)),
    ('("m", a="a")', Actual("m", a="a")),
    ('("m", 1, 2, 3, a=1, b="b", c=3)', Actual("m", 1, 2, 3, a=1, b="b", c=3)),
])
def test_actual_as_str_returns_expected_value(expected, value):
    actual = value.as_str()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("expected, value", [
    ('Actual("r")', Actual("r")),
    ('Actual("r")', Actual("r")),
    ('Actual("r")', Actual("r")),
    ('Actual("r", 1, "b", a=2, b="c")', Actual("r", 1, "b", a=2, b="c")),
])
def test_actual_report_returns_expected_value(expected: str, value: Actual):
    actual = value.report()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("expected, value", [
    ('Actual("r")', Actual("r")),
    ('Actual("r")', Actual("r")),
    ('Actual("r")', Actual("r")),
    ('Actual("r", 1, "b", a=2, b="c")', Actual("r", 1, "b", a=2, b="c")),
])
def test_actual_repr_returns_expected_value(expected: str, value: Actual):
    actual = repr(value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
