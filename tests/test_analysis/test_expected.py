from typing import Optional

import pytest

from strict_mock.analysis import Actual, Expected, TypeIgnore, ValueIgnore


@pytest.mark.parametrize("expected, value", [
    ('("m")', Expected("m")),
    ('("m", 1)', Expected("m", 1)),
    ('("m", 1, 2, 3)', Expected("m", 1, 2, 3)),
    ('("m", "a")', Expected("m", "a")),
    ('("m", "a", "b", "c")', Expected("m", "a", "b", "c")),
    ('("m", 1, 2, "a", 3)', Expected("m", 1, 2, "a", 3)),
    ('("m", a=1)', Expected("m", a=1)),
    ('("m", a=1, b=2, c=3)', Expected("m", a=1, b=2, c=3)),
    ('("m", a="a")', Expected("m", a="a")),
    ('("m", 1, 2, 3, a=1, b="b", c=3)', Expected("m", 1, 2, 3, a=1, b="b", c=3)),
    ('("m")', Expected("m").returns_value(5)),
    ('("m")', Expected("m").raises_error(Exception("this should not print"))),
])
def test_expected_as_str_returns_expected_value(expected, value):
    actual = value.as_str()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_expected_get_return_value_returns_none():
    actual = Expected("m")._get_return_value()
    assert actual is None


def test_expected_get_return_value_returns_expected_value():
    expected = 25
    actual = Expected("m").returns_value(25)._get_return_value()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_expected_get_return_value_raises_error():
    expected = "whoops"
    e = Expected("m").returns_value(25).raises_error(Exception("whoops"))
    with pytest.raises(Exception) as ex:
        e._get_return_value()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_expected_get_return_value_stop_iteration_raises_error():
    expected = ""
    e = Expected("m").stop_iteration()
    with pytest.raises(StopIteration) as ex:
        e._get_return_value()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("expected, value", [
    ('Expected("r")', Expected("r")),
    ('Expected("r", 1, "b", a=2, b="c")', Expected("r", 1, "b", a=2, b="c")),
    ('Expected("r").returns_value(5)', Expected("r").returns_value(5)),
    ('Expected("r").returns_value("a")', Expected("r").returns_value("a")),
    ('Expected("r").raises_error(Exception("hold my drink"))',
     Expected("r").raises_error(Exception("hold my drink"))),
    ('Expected("r").returns_value(None)', Expected("r").returns_value(None)),
    ('Expected("m").returns_mock()', Expected("m").returns_mock()),
    ('Expected("m").returns_mock(ignore_type=True)', Expected("m").returns_mock(ignore_type=True)),
    ('Expected("rm").returns_mock("amock")', Expected("rm").returns_mock("amock")),
    ('Expected("rm").returns_mock("amock", True)', Expected("rm").returns_mock("amock", True)),
])
def test_expected_report_returns_expected_value(expected: str, value: Expected):
    actual = value.report()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("expected, e, a", [
    (False, Expected("called"), Actual("called")),
    (False, Expected("called", 1), Actual("called", 1)),
    (False, Expected("called", a=1), Actual("called", a=1)),
    (True, Expected("called1"), Actual("called2")),
    (True, Expected("called", 1), Actual("called")),
    (True, Expected("called", a=1), Actual("called")),
    (True, Expected("called", 1), Actual("called", 2)),
    (True, Expected("called", a=1), Actual("called", a=2)),
    (True, Expected("called", a=1), Actual("called", b=1)),
    (True, Expected("called", ValueIgnore), Actual("called")),
    (False, Expected("called", ValueIgnore), Actual("called", None)),
    (False, Expected("called", ValueIgnore), Actual("called", 5)),
    (False, Expected("called", ValueIgnore, 6), Actual("called", 5, 6)),
    (False, Expected("called", 5, ValueIgnore), Actual("called", 5, 6)),
    (True, Expected("called", i=ValueIgnore), Actual("called")),
    (True, Expected("called", i=ValueIgnore), Actual("called", j=5)),
    (False, Expected("called", i=ValueIgnore), Actual("called", i=5)),
    (False, Expected("called", TypeIgnore(5)), Actual("called", 5)),
    (True, Expected("called", TypeIgnore("5")), Actual("called", 5)),
    (False, Expected("called", t=TypeIgnore(5)), Actual("called", t=5)),
    (True, Expected("called", t=TypeIgnore("5")), Actual("called", t=5)),
])
def test_expected_compare_actual(expected: bool, e: Expected, a: Actual):
    actual = e.compare_actual(a)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_expected_return_self():
    expected = 5
    e = Expected("m").returns_mock()
    e._check_for_self(5)
    actual = e._get_return_value()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_expected_return_self_type_ignore():
    expected = 5
    e = Expected("m").returns_mock(ignore_type=True)
    e._check_for_self(5)
    actual = e._get_return_value().value

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("expected, e", [
    (None, Expected("none")),
    (None, Expected("value").returns_value(5)),
    (None, Expected("self").returns_mock()),
    (None, Expected("self").returns_mock(ignore_type=True)),
    ("mock1", Expected("mock").returns_mock("mock1")),
    ("mock2", Expected("mock").returns_mock("mock2", True)),
])
def test_expected_get_mock_name_returns_expected_value(expected: Optional[str], e: Expected):
    actual = e._get_mock_name()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("expected, e, mock_name", [
    ('Expected("none")', Expected("none"), "unused"),
    ('Expected("value")', Expected("value").returns_value(12), "unused"),
    ('Expected("self").returns_mock("Mock")', Expected("self").returns_mock(), "Mock"),
    ('Expected("ignored").returns_mock("MockIgnore", True)', Expected("ignored").returns_mock(ignore_type=True),
     "MockIgnore"),
])
def test_expected_report_mock_fix_returns_expected_value(expected: Optional[str], e: Expected, mock_name: str):
    actual = e._report_mock_fix(mock_name)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
