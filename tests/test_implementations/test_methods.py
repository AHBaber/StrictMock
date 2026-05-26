from typing import Any, Set

import pytest

from strict_mock import Events, Expected, MockMethodError
from strict_mock.analysis import CheckType
from strict_mock.implementations import Methods

from .fake_mock import FakeMock


def create_mock(spec: Any, name: str, events: Events, e_set: Set[str]):
    methods = Methods(spec, e_set)
    spec_mocked = methods.add_methods({}, CheckType())
    mock_type = type(name, (FakeMock,), spec_mocked)  # type: ignore
    return mock_type(name, events)


def test_methods_method_no_return():
    class Class:
        def method_called(self):
            raise NotImplementedError

    expected_calls = Events([
        Expected("method_called"),
    ])
    mock = create_mock(Class, "MethodCalledMock", expected_calls, {"method_called"})

    mock.method_called()  # type: ignore

    assert expected_calls._assert_all_calls(mock)


def test_methods_method_with_return_value():
    class Class:
        def method_called(self) -> int:
            raise NotImplementedError

    expected = 12
    expected_calls = Events([
        Expected("method_called").returns_value(12),
    ])
    mock = create_mock(Class, "MethodCalledMock", expected_calls, {"method_called"})

    actual = mock.method_called()  # type: ignore

    assert expected_calls._assert_all_calls(mock)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_methods_return_value_not_set_raises_error():
    class Class:
        def method_called(self) -> int:
            raise NotImplementedError()

    expected = (
        'StrictMock: MockMissingReturn Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("method_called")\n'
        '                      method_called: return_type; expected: int; actual: NoneType(None)\n'
        '                      fix: Expected("method_called").returns_value(int)\n'
        '               0: Actual("method_called")\n\n')

    expected_calls = Events([
        Expected("method_called"),
    ])
    mock = create_mock(Class, "MockMissingReturn", expected_calls, {"method_called"})

    with pytest.raises(MockMethodError) as ex:
        mock.method_called()  # type: ignore
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_methods_has_default_value_returns_expected():
    class Class:
        def method_called(self, a: int = 5):
            raise NotImplementedError()

    expected_calls = Events([
        Expected("method_called"),
    ])
    mock = create_mock(Class, "MockHasDefault", expected_calls, {"method_called"})

    mock.method_called()  # type: ignore
    assert expected_calls._assert_all_calls(mock)


def test_methods_function_param_added_changed_raises_error():
    # catches extra param even though both expected and actual are the same
    class Class:
        def method1(self, a: int):
            pass

    expected = (
        'StrictMock: ExtraParam Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("method1", 12, 23)\n'
        '                      extra positional value: 23; index: 1;\n'
        '                      fix: Expected("method1", a: int)\n'
        '               0: Actual("method1", 12, 23)\n\n')
    expected_calls = Events([
        Expected("method1", 12, 23),
    ])
    mock = create_mock(Class, "ExtraParam", expected_calls, {"method1"})

    with pytest.raises(MockMethodError) as ex:
        mock.method1(12, 23)  # type: ignore
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_methods_function_param_removed_changed_raises_error():
    # catches missing param even though both expected and actual are the same
    class Class:
        def method1(self, a: int, b: int):
            pass

    expected = (
        'StrictMock: MissingParam Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("method1", 12)\n'
        '                      param: b: required type: int; no value provided\n'
        '                      fix: Expected("method1", a: int, b: int)\n'
        '               0: Actual("method1", 12)\n\n')
    expected_calls = Events([
        Expected("method1", 12),
    ])
    mock = create_mock(Class, "MissingParam", expected_calls, {"method1"})

    with pytest.raises(MockMethodError) as ex:
        mock.method1(12)  # type: ignore
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_methods_function_raises_error():
    class Class:
        def method(self) -> int:
            raise NotImplementedError

    expected = "don't do that"
    expected_calls = Events([
        Expected("method").raises_error(ValueError("don't do that")),
    ])
    mock = create_mock(Class, "RaisesError", expected_calls, {"method"})

    with pytest.raises(ValueError) as ex:
        mock.method()  # type: ignore
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_methods_function_invalid_raises_error():
    # though the expected line raises an error,
    # the values in actual must match those in expected
    class Class:
        def method(self, a: int) -> int:
            raise NotImplementedError

    expected = (
        'StrictMock: ArgError Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("method", 5).raises_error(ValueError("don\'t do that"))\n'
        '                      positional: a; required type: int; actual value: "b"; index: 1;\n'
        '                      fix: Expected("method", a: int).returns_value(int)\n'
        'Mismatched     0: Actual("method", "b")\n\n'
    )
    expected_calls = Events([
        Expected("method", 5).raises_error(ValueError("don't do that")),
    ])
    mock = create_mock(Class, "ArgError", expected_calls, {"method"})

    with pytest.raises(MockMethodError) as ex:
        mock.method("b")  # type: ignore
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_methods_none_return():
    class Class:
        def method(self) -> None:
            pass

    expected = None
    expected_calls = Events([
        Expected("method").returns_value(None),
    ])
    mock = create_mock(Class, "ReturnsNone", expected_calls, {"method"})

    actual = mock.method()  # type: ignore
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert expected_calls._assert_all_calls(mock)
