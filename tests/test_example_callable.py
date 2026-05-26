from typing import Tuple

import pytest

from strict_mock import Events, Expected, MockCallableError, strict_mock


def test_callable_function_no_expected_raises_error():
    def function():
        pass

    expected = (
        'StrictMock: StrictMockfunction Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("__call__")\n'
        '                      fix: Expected("__call__")\n\n'
    )

    mock = strict_mock(function)
    with pytest.raises(MockCallableError) as ex:
        mock()
    actual = ex.value.args[0]
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_callable_function_returns_expected_value():
    def function():
        pass

    expected = None
    expected_calls = Events([
        Expected("__call__"),
    ])
    mock = strict_mock(function, "Passes", expected_calls)
    actual = mock()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_callable_function_no_expected_with_args_and_return_raises_error():
    def function(a: int, b: str, c: bool) -> Tuple[int, str]:
        raise NotImplementedError()

    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("__call__", 12, "ghi", False)\n'
        '                      fix: Expected("__call__", a: int, b: str, c: bool).returns_value(Tuple[int, str])\n\n'
    )

    expected_calls = Events([])
    mock = strict_mock(function, "NoExpected", expected_calls)
    with pytest.raises(MockCallableError) as ex:
        _ = mock(12, "ghi", False)
    actual = ex.value.args[0]
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_callable_function_returns_value():
    def random_number() -> int:
        raise NotImplementedError

    expected = [83, 25, 42]
    expected_calls = Events([
        Expected("__call__").returns_value(83),
        Expected("__call__").returns_value(25),
        Expected("__call__").returns_value(42),
    ])
    mock = strict_mock(random_number, "RandomNumber", expected_calls)
    actual = [mock(), mock(), mock()]
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_callable_object_no_expected_raises_error():
    class CallClass:
        def __call__(self, a: int, b: str) -> int:
            raise NotImplementedError

    expected = (
        'StrictMock: CallClass Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("__call__", a=12, b="key")\n'
        '                      fix: Expected("__call__", a: int, b: str).returns_value(int)\n\n'
    )
    expected_calls = Events([])
    mock = strict_mock(CallClass, "CallClass", expected_calls)
    with pytest.raises(MockCallableError) as ex:
        _ = mock(a=12, b="key")
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_callable_object_returns_expected_value():
    class CallClass:
        def __call__(self, a: int, b: str) -> int:
            raise NotImplementedError

    expected = 83
    expected_calls = Events([
        Expected("__call__", a=12, b="key").returns_value(83),
    ])
    mock = strict_mock(CallClass, "CallClass", expected_calls)
    actual = mock(a=12, b="key")

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()
