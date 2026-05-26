from uuid import uuid4

import pytest

from strict_mock import Events, Expected, IValueEqual, MockError, strict_mock


class PoorlyImplemented:
    def __init__(self, a: int):
        self.a = a
        self.not_predictable = uuid4()

    def __eq__(self, other) -> bool:
        if not isinstance(other, PoorlyImplemented):
            return False
        if self.a != other.a or self.not_predictable != other.not_predictable:
            return False
        return True

    def __repr__(self):
        return f"PoorlyImplemented({self.a})"


class PIEqual(IValueEqual):
    def __init__(self, a: int):
        self.a = a

    def __eq__(self, other) -> bool:
        if not isinstance(other, PoorlyImplemented):
            return False
        if self.a != other.a:
            return False
        return True

    def __repr__(self):
        return f"{type(self).__name__}({self.a})"


def test_i_value_equal_returns_expected_value():
    def function(a: int, pi: PoorlyImplemented) -> bool:
        raise NotImplementedError()

    expected = True
    expected_calls = Events([
        Expected("__call__", 7, PIEqual(12)).returns_value(True),
    ])
    mock = strict_mock(function, events=expected_calls)
    actual = mock(7, PoorlyImplemented(12))

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_i_value_equal_raises_error():
    def function(a: int, pi: PoorlyImplemented) -> bool:
        raise NotImplementedError()

    expected = (
        'StrictMock: StrictMockfunction Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("__call__", 7, PoorlyImplemented(11)).returns_value(True)\n'
        '                      fix: Expected("__call__", a: int, pi: PoorlyImplemented).returns_value(bool)\n'
        'Mismatched     0: Actual("__call__", 7, PoorlyImplemented(12))\n\n'
    )
    # Irony, I have to use a different value to make sure the test "fails".
    # Otherwise, there is a chance for the expected and actual to randomly be the same value
    # and thus "pass".  Highly remote, but non-zero.
    expected_calls = Events([
        Expected("__call__", 7, PoorlyImplemented(11)).returns_value(True),
    ])
    mock = strict_mock(function, events=expected_calls)
    with pytest.raises(MockError) as ex:
        _ = mock(7, PoorlyImplemented(12))
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : '{actual}'"
    assert mock.assert_all_calls()
