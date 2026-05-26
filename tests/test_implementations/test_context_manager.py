from typing import Any, Callable, Dict, List, Type

import pytest

from strict_mock import Events, Expected, MockError, ValueIgnore
from strict_mock.implementations import BaseMock, cm_dunders, get_spec_dict

from .fake_mock import FakeMock


class CMMock:
    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()


class CTXMock(CMMock):
    # this works since only __entr__ and __exit__ are being mocked in this test file
    def get_value(self) -> int:
        return 23


def _create_mock(spec: Type[Any], name: str, expected: List[Expected]):
    events = Events(expected)
    spec_dict = get_spec_dict(spec)
    spec_mocked: Dict[str, Callable] = {}
    for d in cm_dunders.keys():
        if d in spec_dict:
            spec_mocked[d] = cm_dunders[d]
    mock_type = type(f'StrictMockTesting:{name}', (BaseMock, spec), spec_mocked)
    return mock_type(spec, name, events)


def test_context_manager_spec_not_callable_raises_error():
    expected = "'StrictMockTesting:NotCM' object does not support the context manager protocol"

    mock = _create_mock(FakeMock, "NotCM", [])

    with pytest.raises(TypeError) as ex:
        with mock:
            pass
    actual = str(ex.value)
    assert expected in actual, f"\nexpected: {expected}\nactual  : {actual}"


def test_context_manager_returns_expected_value():
    expected_calls: List[Expected] = [
        Expected("__enter__"),
        Expected("__exit__", None, None, None),
    ]
    mock = _create_mock(CMMock, "IteratorPasses", expected_calls)
    with mock:
        pass

    assert mock.assert_all_calls()


def test_context_manager_returns_ctx():
    expected = 23

    expected_calls: List[Expected] = [
        Expected("__enter__").returns_mock(),
        Expected("__exit__", None, None, None),
    ]
    mock = _create_mock(CTXMock, "IteratorPasses", expected_calls)
    with mock as ctx:
        actual = ctx.get_value()

    assert mock.assert_all_calls()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_context_manager_error_in_context_error_suppressed():
    expected_calls: List[Expected] = [
        Expected("__enter__"),
        Expected("__exit__", TypeError, "whoops", ValueIgnore).returns_value(True),
    ]
    mock = _create_mock(CMMock, "IteratorPasses", expected_calls)
    try:
        with mock:
            raise TypeError("whoops")
    except Exception as e:
        # since True is returned in __exit__, the error will
        # not be raised out of the context manager
        assert str(e) == "this will never be reached"

    assert mock.assert_all_calls()


def test_context_manager_error_in_context_error_raised():
    expected = "error escaped context"
    expected_calls: List[Expected] = [
        Expected("__enter__"),
        Expected("__exit__", TypeError, "error escaped context", ValueIgnore),
    ]
    mock = _create_mock(CMMock, "CMErrorEscapes", expected_calls)
    actual = ""
    try:
        with mock:
            raise TypeError("error escaped context")
    except Exception as ex:
        actual = str(ex)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_context_manager_multi_cm_with_error():
    expected = (
        'error escaped context'
        ''
    )
    expected_calls1: List[Expected] = [
        Expected("__enter__").returns_mock(),
        # __exit__ not called since MockError was raised
    ]
    expected_calls2: List[Expected] = [
        Expected("__enter__").returns_mock(),
        # __exit__ not called since MockError was raised
    ]
    mock1 = _create_mock(CMMock, "CMMock1", expected_calls1)
    mock2 = _create_mock(CMMock, "CMMock2", expected_calls2)

    with pytest.raises(Exception) as ex:
        with mock1:
            with mock2:
                raise MockError("error escaped context")
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock1.assert_all_calls()
    assert mock2.assert_all_calls()
