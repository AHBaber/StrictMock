from typing import Any, Callable, List, Optional

import pytest

from strict_mock import (Events, Expected, MockCreationError, TypeData,
                         TypeIgnore, expected_iter)
from strict_mock.analysis import CheckType, get_params
from strict_mock.implementations import BaseMock

from .fake_mock import FakeMock


class CallClass:
    def __init__(self, name: str, method: Callable, *args, **kwargs) -> None:
        self.name = name
        self.method = method
        self.args = args
        self.kwargs = kwargs


def make_mock(name: str, ) -> BaseMock:
    return BaseMock(BaseMock, name, Events())


def test_events_none_returns_true():
    events = Events()

    assert events._assert_all_calls(make_mock("NoEvents"))


def test_events_extend_expected_returns_expected_value():
    expected: List[Expected] = [
        Expected("__iter__"),
        Expected("__next__").returns_value(1),
        Expected("__next__").returns_value(2),
        Expected("__next__").returns_value(3),
        Expected("__next__").stop_iteration(),
    ]

    events = Events()
    events.extend_expected(expected_iter([1, 2, 3]))
    actual = events._expected

    assert len(actual) == len(expected)
    for i in range(len(expected)):
        e = expected[i].as_str()
        a = actual[i].as_str()
        assert a == e, f"\nindex   : {i}\nexpected: {e}\nactual  : {a}"
        e = repr(expected[i]._return_value)
        a = repr(actual[i]._return_value)
        assert a == e, f"\nindex   : {i}\nexpected: {e}\nactual  : {a}"
        e = repr(expected[i]._error)
        a = repr(actual[i]._error)
        assert a == e, f"\nindex   : {i}\nexpected: {e}\nactual  : {a}"


def call0():
    pass


def call1r(a: int) -> int:
    return 0


class EventsAddActualBase:
    expected_output: Optional[str] = None
    name: str
    calls: List[CallClass] = list()

    expected_calls: List[Expected] = list()
    expected_rv: List[Any] = list()

    _actual_rv: List[Any] = list()
    _actual_ex: Optional[str] = None
    _actual_assert: bool

    @classmethod
    def setup_class(cls):
        events = Events(cls.expected_calls)
        mock = make_mock(cls.name)
        try:
            for c in cls.calls:
                td = TypeData(c.name, CheckType(), get_params(c.method))
                rv = events.add_actual(mock, c.name, td, *c.args, **c.kwargs)
                cls._actual_rv.append(rv)
        except MockCreationError as ex:
            cls._actual_ex = str(ex)
        try:
            if cls._actual_ex is None:
                events._assert_all_calls(mock)
        except MockCreationError as ex:
            cls._actual_ex = str(ex)

    def test_returned_len(self):
        e = len(self.expected_rv)
        a = len(self._actual_rv)
        assert a == e, f"\nexpected: {e}\nactual  : {a}"

    def test_returned_value(self):
        for i in range(len(self.expected_rv)):
            e = self.expected_rv[i]
            a = self._actual_rv[i]
            assert a == e, f"\nindex   : {i}\nexpected: {a}\nactual  : {a}"

    def test_exception(self):
        expected = self.expected_output
        actual = self._actual_ex
        assert actual == expected, f"\nexpected: {expected}\nactual: {actual}"


class TestEventsAddActual1Match(EventsAddActualBase):
    expected_output: Optional[str] = None
    expected_rv: List[Any] = [None]

    name: str = "Events1Match"
    expected_calls: List[Expected] = [
        Expected("call0"),
    ]
    calls: List[CallClass] = [
        CallClass("call0", call0),
    ]


class TestEventsAddActualNoExpected(EventsAddActualBase):
    expected_output = (
        'StrictMock: EventsNoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("call0")\n'
        '                      fix: Expected("call0")\n\n')
    expected_rv: List[Any] = [None]

    name: str = "EventsNoExpected"
    calls: List[CallClass] = [
        CallClass("call0", call0),
    ]


class TestEventsAddActualOnlyExpected(EventsAddActualBase):
    expected_output = (
        'StrictMock: EventNoActual Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 0\n'
        'Extra          0: Expected("call0")\n\n')
    expected_rv: List[Any] = [None]

    name: str = "EventNoActual"
    expected_calls: List[Expected] = [
        Expected("call0"),
    ]


class TestEventsAddActualMismatch(EventsAddActualBase):
    expected_output = (
        'StrictMock: EventsMismatch Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("call00")\n'
        '                      fix: Expected("call0")\n'
        'Mismatched     0: Actual("call0")\n\n')
    expected_rv: List[Any] = [None]

    name: str = "EventsMismatch"
    expected_calls: List[Expected] = [
        Expected("call00"),
    ]
    calls: List[CallClass] = [
        CallClass("call0", call0),
    ]


class TestEventsAddActualIncorrectReturnType(EventsAddActualBase):
    expected_output = (
        'StrictMock: EventsIncorrectReturnType Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("call1r", 5).returns_value("abc")\n'
        '                      call1r: return_type; expected: int; actual: str("abc")\n'
        '                      fix: Expected("call1r", a: int).returns_value(int)\n'
        '               0: Actual("call1r", 5)\n\n')
    expected_rv: List[Any] = [None]

    name: str = "EventsIncorrectReturnType"
    expected_calls: List[Expected] = [
        Expected("call1r", 5).returns_value("abc"),
    ]
    calls: List[CallClass] = [
        CallClass("call1r", call1r, 5),
    ]


def test_events_raises_error():
    expected = """hold my drink"""
    expected_calls = [
        Expected("called1", 1).raises_error(Exception("hold my drink")),
    ]

    events = Events(expected_calls)
    mock = make_mock("RaisesError")
    td = TypeData("called1", CheckType(), get_params(call0))
    with pytest.raises(Exception) as ex:
        events.add_actual(mock, "called1", td, 1)
    actual = str(ex.value)

    assert expected in actual, f"\nexpected: {expected}\nactual  : {actual}"
    assert events._assert_all_calls(mock)


def test_events_has_value_raises_error():
    expected = """hold my drink"""
    expected_calls = [
        Expected("called1", 1).returns_value(5).raises_error(Exception("hold my drink")),
    ]

    events = Events(expected_calls)
    mock = make_mock("HasValueRaisesError")
    td = TypeData("called1", CheckType(), get_params(call0))
    with pytest.raises(Exception) as ex:
        events.add_actual(mock, "called1", td, 1)
    actual = str(ex.value)

    assert expected in actual, f"\nexpected: {expected}\nactual  : {actual}"
    assert events._assert_all_calls(mock)


def function():
    pass


def function_none() -> None:
    pass


def function_any() -> Any:
    return None


@pytest.mark.parametrize("f, expected_calls, expected", [
    (function, [Expected("function")], None),
    (function, [Expected("function").returns_value(None)], None),
    (function, [Expected("function").returns_value(5)], 5),
    (function_none, [Expected("function_none")], None),
    (function_none, [Expected("function_none").returns_value(None)], None),
    (function_any, [Expected("function_any")], None),
    (function_any, [Expected("function_any").returns_value(None)], None),
    (function_any, [Expected("function_any").returns_value(7)], 7),
    (function, [Expected("function").returns_value(TypeIgnore("5"))], "5"),
])
def test_events_return_values(f, expected_calls, expected):
    events = Events(expected_calls)
    mock = make_mock("ReturnTypes")
    td = TypeData(f.__name__, CheckType(), get_params(f))
    actual = events.add_actual(mock, f.__name__, td)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert events._assert_all_calls(mock)


def test_events_add_mock_multiple_with_same_name_raises_error():
    expected = "All mocks must be unique names in a given test, 'Amock' has been declared twice"
    events = Events()
    mock = FakeMock()
    events._add_mock("Amock", mock)

    with pytest.raises(MockCreationError) as ex:
        events._add_mock("Amock", mock)
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_events_check_for_mock_none_returned_passes():
    expected = None
    expected_calls: List[Expected] = [
        Expected("call"),
    ]
    events = Events(expected_calls)
    actual = events._check_for_mock(FakeMock(), expected_calls[0], 0)._get_return_value()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_events_check_for_mock_value_returned_passes():
    expected = 5
    expected_calls: List[Expected] = [
        Expected("call").returns_value(5),
    ]
    events = Events(expected_calls)
    actual = events._check_for_mock(FakeMock(), expected_calls[0], 0)._get_return_value()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_events_check_for_mock_self_returned_passes():
    expected = FakeMock("Self")
    expected_calls: List[Expected] = [
        Expected("call").returns_mock(),
    ]
    events = Events(expected_calls)
    actual = events._check_for_mock(expected, expected_calls[0], 0)._get_return_value()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_events_check_for_mock_declared_returned_passes():
    expected = FakeMock("Mock1")
    expected_calls: List[Expected] = [
        Expected("call").returns_mock("Mock1"),
    ]
    events = Events(expected_calls)
    events._add_mock("Mock1", expected)
    events._add_mock("Mock2", FakeMock("Mock2"))
    actual = events._check_for_mock(expected, expected_calls[0], 0)._get_return_value()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_events_check_for_mock_none_declared_raises_error():
    expected = "No mock named 'Mock1' was created"
    expected_calls: List[Expected] = [
        Expected("call").returns_mock("Mock1"),
    ]
    events = Events(expected_calls)

    with pytest.raises(MockCreationError) as ex:
        events._check_for_mock(FakeMock(), expected_calls[0], 0)._get_return_value()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_events_check_for_mock_missing_raises_error():
    expected = "No mock named 'Mock2' was created"
    expected_calls: List[Expected] = [
        Expected("call").returns_mock("Mock2"),
    ]
    events = Events(expected_calls)
    events._add_mock("Mock1", FakeMock())
    events._add_mock("Mock3", FakeMock())

    with pytest.raises(MockCreationError) as ex:
        events._check_for_mock(FakeMock(), expected_calls[0], 0)._get_return_value()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
