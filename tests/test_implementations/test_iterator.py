from typing import Any, Callable, Dict, List

import pytest

from strict_mock import Events, Expected, expected_iter
from strict_mock.implementations import BaseMock, get_spec_dict, iter_dunders


class IterMock:
    def __iter__(self):
        raise NotImplementedError()

    def __next__(self) -> Any:
        raise NotImplementedError()


def _create_mock(name: str, expected: List[Expected]):
    events = Events(expected)
    spec_dict = get_spec_dict(IterMock)
    spec_mocked: Dict[str, Callable] = {}
    for d in iter_dunders.keys():
        if d in spec_dict:
            spec_mocked[d] = iter_dunders[d]
    mock_type = type(f'StrictMockTesting:{name}', (BaseMock, IterMock), spec_mocked)
    return mock_type(IterMock, name, events)


def test_expected_iter_returns_empty_list():
    expected: List[Expected] = [
        Expected("__next__").stop_iteration(),
    ]
    actual = expected_iter([])

    assert len(actual) == len(expected)
    for i in range(len(expected)):
        a = actual[i]
        e = expected[i]
        assert a == e, f"\nindex   : {i}\nexpected: {e}\nactual  : {a}"


def test_expected_iter_returns_expected_values():
    expected: List[Expected] = [
        Expected("__next__").returns_value(1),
        Expected("__next__").returns_value(2),
        Expected("__next__").returns_value(3),
        Expected("__next__"),
    ]
    actual = expected_iter([1, 2, 3])

    assert len(actual) == len(expected)
    for i in range(len(expected)):
        a = actual[i].as_str()
        e = expected[i].as_str()
        assert a == e, f"\nindex   : {i}\nexpected: {e}\nactual  : {a}"


def test_iterator_comprehension_no_values_returns_expected_value():
    expected: List[int] = []

    expected_calls: List[Expected] = [
        Expected("__next__").stop_iteration(),
    ]
    mock = _create_mock("IteratorPass", expected_calls)
    actual = [n for n in mock]

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_comprehension_returns_expected_value():
    expected = [1, 2, 3]

    expected_calls: List[Expected] = expected_iter([1, 2, 3])
    mock = _create_mock("IteratorPass", expected_calls)
    actual = [n for n in mock]

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_for_no_values_returns_expected_value():
    expected: List[int] = []

    expected_calls: List[Expected] = [
        Expected("__next__").stop_iteration(),
    ]
    mock = _create_mock("IteratorPass", expected_calls)
    actual: List[int] = []
    for n in mock:
        actual.append(n)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_for_loop_returns_expected_value():
    expected = [1, 2, 3]

    expected_calls: List[Expected] = [
        Expected("__next__").returns_value(1),
        Expected("__next__").returns_value(2),
        Expected("__next__").returns_value(3),
        Expected("__next__").stop_iteration(),
    ]
    mock = _create_mock("IteratorPass", expected_calls)
    actual = []
    for n in mock:
        actual.append(n)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_next_no_values_returns_expected_value():
    expected_calls: List[Expected] = [
        Expected("__next__").stop_iteration(),
    ]
    mock = _create_mock("IteratorPass", expected_calls)
    with pytest.raises(StopIteration):
        next(mock)

    assert mock.assert_all_calls()


def test_iterator_next_one_values_returns_expected_value():
    expected = 1

    expected_calls: List[Expected] = [
        Expected("__next__").returns_value(1),
    ]
    mock = _create_mock("IteratorPass", expected_calls)
    actual = next(mock)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_next_three_values_returns_expected_value():
    expected = [1, 2, 3]

    expected_calls: List[Expected] = [
        Expected("__next__").returns_value(1),
        Expected("__next__").returns_value(2),
        Expected("__next__").returns_value(3),
    ]
    mock = _create_mock("IteratorPass", expected_calls)
    actual = []
    actual.append(next(mock))
    actual.append(next(mock))
    actual.append(next(mock))

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_iter_no_values_returns_expected_value():
    expected_calls: List[Expected] = []
    mock = _create_mock("IteratorPass", expected_calls)
    _ = iter(mock)

    assert mock.assert_all_calls()


def test_iterator_iter_1_values_returns_expected_value():
    expected = 5
    expected_calls: List[Expected] = [
        Expected("__next__").returns_value(5),
    ]
    mock = _create_mock("IteratorPass", expected_calls)
    i = iter(mock)
    actual = next(i)

    assert mock.assert_all_calls()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
