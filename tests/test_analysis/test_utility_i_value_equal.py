from typing import Any

import pytest

from strict_mock.analysis.utility import IValueEqual, stringify


def test_i_value_equal_equal_raises_error():
    expected = "Did not implement ValueEqual.__eq__(...)"
    with pytest.raises(NotImplementedError) as ex:
        _ = IValueEqual() == "place holder"
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_i_value_equal_repr_returns_expected_value():
    expected = "IValueEqual(...)"
    actual = repr(IValueEqual())
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


class NotSupported:
    def __init__(self, i: int, b: bool, s: str) -> None:
        self.i = i
        self.b = b
        self.s = s


class VESimple(IValueEqual):
    def __init__(self, i: int, b: bool, s: str) -> None:
        self.i = i
        self.b = b
        self.s = s

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NotSupported):
            return False
        if self.i != other.i:
            return False
        if self.b != other.b:
            return False
        if self.s != other.s:
            return False
        return True

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.i}, {self.b}, {stringify(self.s)})'


def test_i_value_equal_equal_returns_true():
    expected = True
    actual = VESimple(1, False, "s") == NotSupported(1, False, "s")
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_i_value_equal_not_equal_returns_true():
    expected = True
    actual = VESimple(1, False, "s") != NotSupported(1, True, "s")
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_i_value_equal_str_returns_expected_value():
    expected = 'VESimple(1, False, "s")'
    actual = repr(VESimple(1, False, "s"))
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
