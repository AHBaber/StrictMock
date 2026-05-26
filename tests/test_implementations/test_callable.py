from typing import Any, Callable, List, Type, Union

import pytest

from strict_mock import Events, Expected, MockCallableError
from strict_mock.implementations import BaseMock, get_call_dunder


class CallMock:
    def __init__(self):
        self._callable: Any = None

    def __call__(self, *args, **kwargs):
        return self._callable.call(*args, **kwargs)


def _create_mock(spec: Union[Type[Any], Callable], name: str, expected: List[Expected]):
    events = Events(expected)
    spec_mocked, spec = get_call_dunder({}, spec)  # type: ignore
    bases: List[Type] = [BaseMock]
    if spec:
        bases.append(spec)  # type: ignore
    mock_type = type(f'StrictMockTesting:{name}', tuple(bases), spec_mocked)
    return mock_type(spec, name, events)


def test_callable_not_callable_raises_error():
    class NotCallable:
        pass

    expected = "'StrictMockTesting:NotCallable' object is not callable"
    mock = _create_mock(NotCallable, "NotCallable", [])

    with pytest.raises(TypeError) as ex:
        mock()
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_callable_simple_function_returns_expected_values():
    def simple():
        pass

    expected_calls: List[Expected] = [
        Expected("__call__"),
    ]
    mock = _create_mock(simple, "Simple", expected_calls)

    mock()

    assert mock.assert_all_calls()


def test_callable_function_with_args():
    def func(a: int, b: int) -> int:
        raise NotImplementedError

    expected = 23
    expected_calls: List[Expected] = [
        Expected("__call__", 5, 7).returns_value(23),
    ]
    mock = _create_mock(func, "Func", expected_calls)

    actual = mock(5, 7)

    assert mock.assert_all_calls()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_callable_function_wrong_types_raises_error():
    def func(a: int, b: int) -> int:
        raise NotImplementedError

    expected = (
        'StrictMock: Func Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("__call__", 5, 7).returns_value(23)\n'
        '                      positional: b; required type: int; actual value: "7"; index: 1;\n'
        '                      fix: Expected("__call__", a: int, b: int).returns_value(int)\n'
        'Mismatched     0: Actual("__call__", 5, "7")\n\n'
    )
    expected_calls: List[Expected] = [
        Expected("__call__", 5, 7).returns_value(23),
    ]
    mock = _create_mock(func, "Func", expected_calls)

    with pytest.raises(MockCallableError) as ex:
        _ = mock(5, "7")
    actual = str(ex.value)
    assert mock.assert_all_calls()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_callable_function_wrong_values_raises_error():
    def func(a: int, b: int) -> int:
        raise NotImplementedError

    expected = (
        'StrictMock: Func Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("__call__", 5, 7).returns_value(23)\n'
        '                      fix: Expected("__call__", a: int, b: int).returns_value(int)\n'
        'Mismatched     0: Actual("__call__", 5, 8)\n\n'
    )
    expected_calls: List[Expected] = [
        Expected("__call__", 5, 7).returns_value(23),
    ]
    mock = _create_mock(func, "Func", expected_calls)

    with pytest.raises(MockCallableError) as ex:
        _ = mock(5, 8)
    actual = str(ex.value)

    assert mock.assert_all_calls()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_callable_function_wrong_return_value_raises_error():
    def func(a: int, b: int) -> int:
        raise NotImplementedError

    expected = (
        'StrictMock: Func Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("__call__", 5, 7).returns_value("23")\n'
        '                      __call__: return_type; expected: int; actual: str("23")\n'
        '                      fix: Expected("__call__", a: int, b: int).returns_value(int)\n'
        '               0: Actual("__call__", 5, 7)\n\n'
    )
    expected_calls: List[Expected] = [
        Expected("__call__", 5, 7).returns_value("23"),
    ]
    mock = _create_mock(func, "Func", expected_calls)

    with pytest.raises(MockCallableError) as ex:
        _ = mock(5, 7)
    actual = str(ex.value)

    assert mock.assert_all_calls()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_callable_functor_returns_expected_values():
    class Func:
        def __call__(self):
            pass

    expected_calls: List[Expected] = [
        Expected("__call__"),
    ]
    mock = _create_mock(Func, "Func", expected_calls)

    mock()

    assert mock.assert_all_calls()


def test_callable_functor_with_args_returns_expected_values():
    class Func:
        def __call__(self, a: int, b: int) -> int:
            raise NotImplementedError

    expected = 23
    expected_calls: List[Expected] = [
        Expected("__call__", 5, 7).returns_value(23),
    ]
    mock = _create_mock(Func, "WithArgs", expected_calls)

    actual = mock(5, 7)

    assert mock.assert_all_calls()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_callable_functor_wrong_types_raises_error():
    class Func:
        def __call__(self, a: int, b: int) -> int:
            raise NotImplementedError

    expected = (
        'StrictMock: FuncWrongType Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("__call__", 5, 7).returns_value(23)\n'
        '                      positional: b; required type: int; actual value: "7"; index: 2;\n'
        '                      fix: Expected("__call__", a: int, b: int).returns_value(int)\n'
        'Mismatched     0: Actual("__call__", 5, "7")\n\n'
    )
    expected_calls: List[Expected] = [
        Expected("__call__", 5, 7).returns_value(23),
    ]
    mock = _create_mock(Func, "FuncWrongType", expected_calls)

    with pytest.raises(MockCallableError) as ex:
        _ = mock(5, "7")
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_callable_functor_wrong_value_raises_error():
    class Func:
        def __call__(self, a: int, b: int) -> int:
            raise NotImplementedError

    expected = (
        'StrictMock: FuncWrongType Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("__call__", 5, 7).returns_value(23)\n'
        '                      fix: Expected("__call__", a: int, b: int).returns_value(int)\n'
        'Mismatched     0: Actual("__call__", 5, 8)\n\n'
    )
    expected_calls: List[Expected] = [
        Expected("__call__", 5, 7).returns_value(23),
    ]
    mock = _create_mock(Func, "FuncWrongType", expected_calls)

    with pytest.raises(MockCallableError) as ex:
        _ = mock(5, 8)
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_callable_functor_wrong_return_type_raises_error():
    class Func:
        def __call__(self, a: int, b: int) -> int:
            raise NotImplementedError

    expected = (
        'StrictMock: FuncWrongType Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("__call__", 5, 7).returns_value("23")\n'
        '                      __call__: return_type; expected: int; actual: str("23")\n'
        '                      fix: Expected("__call__", a: int, b: int).returns_value(int)\n'
        '               0: Actual("__call__", 5, 7)\n\n'
    )
    expected_calls: List[Expected] = [
        Expected("__call__", 5, 7).returns_value("23"),
    ]
    mock = _create_mock(Func, "FuncWrongType", expected_calls)

    with pytest.raises(MockCallableError) as ex:
        _ = mock(5, 7)
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
