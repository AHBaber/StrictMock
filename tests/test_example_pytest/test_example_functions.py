from typing import Any, List

import pytest

from strict_mock import Events, Expected, MockCallableError, strict_mock


def test_strict_mock_functions_none_expected_raises_error():
    # when you first create the mock, if you don't have the expected_calls
    # filled out, then you will get errors
    # the lack of proper expected values will cause the mock to
    # raise an error as soon as the method is called
    def function_called():
        raise NotImplementedError

    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("__call__")\n'
        '                      fix: Expected("__call__")\n\n'
    )
    expected_calls = Events([])

    mock = strict_mock(function_called, "NoExpected", expected_calls)
    with pytest.raises(MockCallableError) as ex:
        mock()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_functions_with_args_none_expected_raises_error():
    # if the method takes args, then it will tell you the types that
    # need to passed to create expected value properly
    def method_called(a: int, b: str):
        raise NotImplementedError()

    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("__call__")\n'
        '                      fix: Expected("__call__", a: int, b: str)\n\n'
    )
    expected_calls = Events([])

    mock = strict_mock(method_called, "NoExpected", expected_calls)
    with pytest.raises(MockCallableError) as ex:
        mock()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_functions_successful_call():
    # once the expected_calls is set, then the tests will pass
    def function1():
        pass

    def function2(a: int, b: str):
        pass

    expected_calls1 = Events([
        Expected("__call__"),
    ])
    expected_calls2 = Events([
        Expected("__call__", 5, "abc"),
    ])

    mock1 = strict_mock(function1, "Successful", expected_calls1)
    mock2 = strict_mock(function2, "Successful", expected_calls2)
    mock1()
    mock2(5, "abc")

    assert mock1.assert_all_calls()
    assert mock2.assert_all_calls()


def test_strict_mock_functions_return_value_not_set_raises_error():
    # if a method returns a value, the returned value must be set
    # or an error will be returned
    # a MockMethodError will be raised as soon as method is called
    # without a return value
    def NoReturnValue() -> int:
        raise NotImplementedError()

    expected = (
        'StrictMock: NoReturnValue Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("__call__")\n'
        '                      __call__: return_type; expected: int; actual: NoneType(None)\n'
        '                      fix: Expected("__call__").returns_value(int)\n'
        '               0: Actual("__call__")\n\n'
    )
    expected_calls = Events([
        Expected("__call__"),
    ])

    mock = strict_mock(NoReturnValue, "NoReturnValue", expected_calls)
    with pytest.raises(MockCallableError) as ex:
        mock()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_functions_wrong_return_value_raises_error():
    # even if a return value is added to the expected calls, its
    # type must match
    def returns_wrong(self) -> int:
        raise NotImplementedError()

    expected = (
        'StrictMock: ReturnsWrong Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("__call__").returns_value("abc")\n'
        '                      __call__: return_type; expected: int; actual: str("abc")\n'
        '                      fix: Expected("__call__").returns_value(int)\n'
        '               0: Actual("__call__")\n\n'
    )
    expected_calls = Events([
        Expected("__call__").returns_value("abc"),
    ])

    mock = strict_mock(returns_wrong, "ReturnsWrong", expected_calls)
    with pytest.raises(MockCallableError) as ex:
        mock()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_functions_method_raises_error():
    # you can choose to have a method raise an error instead.
    def method_raises(self):
        pass

    expected = "boom"
    expected_calls = Events([
        Expected("__call__").raises_error(ValueError("boom")),
    ])

    mock = strict_mock(method_raises, "MethodRaises", expected_calls)
    with pytest.raises(ValueError) as ex:
        mock()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_functions_values_must_match_to_raise_error():
    # the actual values must match the expected values before the
    # error is raised, a MockMethodError is raised until it is fixed
    def method_wrong_args(self, a: int, b: List[int]):
        pass

    expected = (
        'StrictMock: MethodWrongArgs Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("__call__", 5, [12]).raises_error(ValueError("bang!"))\n'
        '                      fix: Expected("__call__", a: int, b: List[int])\n'
        'Mismatched     0: Actual("__call__", 5, [13])\n\n'
    )
    expected_calls = Events([
        Expected("__call__", 5, [12]).raises_error(ValueError("bang!")),
    ])

    mock = strict_mock(method_wrong_args, "MethodWrongArgs", expected_calls)
    with pytest.raises(MockCallableError) as ex:
        mock(5, [13])
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_functions_with_defaults_successful_call():
    # if defaults are used in the called methods, then they do not appear in the
    # Expected list either
    # if the value appears in the called method, it needs to be in the Expected
    # list as well, even if the value is same as the default

    def method1(a: int = 5):
        pass

    def method2(a: int, b: str = "abc"):
        pass

    expected_calls1 = Events([
        Expected("__call__"),
        Expected("__call__", 8),
        Expected("__call__", 5),
    ])

    expected_calls2 = Events([
        Expected("__call__", 5),
        Expected("__call__", 6, "abc"),
        Expected("__call__", 7, "def"),
    ])

    mock1 = strict_mock(method1, "Successful1", expected_calls1)
    mock1()
    mock1(8)
    mock1(5)

    mock2 = strict_mock(method2, "Successful2", expected_calls2)
    mock2(5)
    mock2(6, "abc")
    mock2(7, "def")

    assert mock1.assert_all_calls()
    assert mock2.assert_all_calls()


def test_strict_mock_functions_with_pos_and_kwargs():
    def function_pk(a: int, *args: Any, b: int, **kwargs: Any):
        pass

    expected_calls = Events([
        Expected("__call__", 1, 2, 3, 4, b=5, c=6, d=7),
    ])
    mock = strict_mock(function_pk, "Mock_function_pk", expected_calls)

    mock(1, 2, 3, 4, b=5, c=6, d=7)

    assert mock.assert_all_calls()
