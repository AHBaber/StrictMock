from typing import Optional

import pytest

from strict_mock import MockCreationError
from strict_mock.analysis import (Actual, ErrorExpected, Expected, TypeIgnore,
                                  ValueIgnore)


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


@pytest.mark.parametrize("expected, left, right", [
    (True, Expected("pass"), Expected("pass")),
    (True, Expected("pass", 1, a=2), Expected("pass", 1, a=2)),
    (True, Expected("pass", ValueIgnore, a=2), Expected("pass", 1, a=2)),
    (True, Expected("pass", 1, a=2), Expected("pass", ValueIgnore, a=2)),
    (True, Expected("pass", a=ValueIgnore), Expected("pass", a=1)),
    (True, Expected("pass", a=1), Expected("pass", a=ValueIgnore)),
    (True, Expected("returns_pass").returns_value(5), Expected("returns_pass").returns_value(5)),
    (True, Expected("raises_pass").raises_error(Exception("oops")),
     Expected("raises_pass").raises_error(Exception("oops"))),
    (False, Expected("not correct type"), object()),
    (False, Expected("one name"), Expected("another name")),
    (False, Expected("diff len args", 1, 2), Expected("diff len args", 1)),
    (False, Expected("!= args", 1, 2), Expected("!= args", 1, 3)),
    (False, Expected("diff len kwargs", a=1, b=2), Expected("diff len kwargs", a=1)),
    (False, Expected("diff kwargs", a=1, b=2), Expected("diff kwargs", a=1, c=2)),
    (False, Expected("!= kwargs", a=1), Expected("!= kwargs", a=2)),
    (False, Expected("returns_ne").returns_value(5), Expected("returns_ne").returns_value(6)),
    (False, Expected("returns_diff").returns_mock(), Expected("returns_diff").returns_value(6)),
    (False, Expected("raises_fails").raises_error(Exception("oops")), Expected("raises_fails")),
    (False, Expected("raises_fails"), Expected("raises_fails").raises_error(Exception("oops"))),
    (False, Expected("raises_fails").raises_error(TypeError("oops")),
     Expected("raises_fails").raises_error(ValueError("oops"))),
    (False, Expected("raises_fails").raises_error(TypeError("oops")),
     Expected("raises_fails").raises_error(TypeError("typo"))),
])
def test_expected_eq_returns_expected_value(expected, left, right):
    actual = left == right
    assert actual == expected, f"\nleft : {left}\nright: {right}"


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
    e = Expected("__next__").stop_iteration()
    with pytest.raises(StopIteration) as ex:
        e._get_return_value()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_expected_get_return_value_stop_iteration_incorrect_method_raises_error():
    expected = '.stop_iteration() may only be used with "__next__", not "oops"'
    with pytest.raises(MockCreationError) as ex:
        Expected("oops").stop_iteration()
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


def test_error_expected_compare_actual_returns_true():
    expected = True
    actual = ErrorExpected("matching", "").compare_actual(Actual("matching"))
    assert actual == expected, f"\nexpected: {expected}\nactual: {actual}"


def test_error_expected_report_returns_basic_text():
    expected = "Error in Expected: Something Went wrong\n    fix: useful instructions"
    actual = ErrorExpected("Something Went wrong", "useful instructions").report()
    assert actual == expected, f"\nexpected: {expected}\nactual: {actual}"


def test_error_expected_report_expected_returns_expected_value():
    expected = (
        'Error in Expected: E when async was needed\n'
        '    incorrect: Expected("method", a=5, b=12)\n'
        '    fix: AsyncGroup(Expected(...))'
    )
    e = Expected("method", a=5, b=12)
    actual = ErrorExpected("E when async was needed", "AsyncGroup(Expected(...))", e).report()
    assert actual == expected, f"\nexpected: {expected}\nactual: {actual}"
