from typing import Iterable

import pytest

from strict_mock import (Events, Expected, MockIteratorError, expected_iter,
                         strict_mock)


class Iterator(Iterable):
    def __init__(self, start: int, stop: int):
        raise Exception("Iterator.__init__() should have been overridden by the mock")

    def __iter__(self):
        raise Exception("Iterator.__iter__() should have been overridden by the mock")

    def __next__(self):
        raise Exception("Iterator.__next__() should have been overridden by the mock")


def test_iterator_no_expected_raises_error():
    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("__next__")\n'
        '                      fix: Expected("__next__")\n\n'
    )
    expected_calls = Events([])
    mock = strict_mock(Iterator, "NoExpected", expected_calls)
    with pytest.raises(MockIteratorError) as ex:
        for n in mock:
            pass
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_for_loop_returns_expected_values():
    # when setting up to be used in a for loop, the first
    # expected will be an iter followed by nexts
    # each next will return a single value.
    # a next without a return value will end the loop
    expected = [1, 2, 3]
    expected_calls = Events([
        Expected("__next__").returns_value(1),
        Expected("__next__").returns_value(2),
        Expected("__next__").returns_value(3),
        Expected("__next__").stop_iteration(),
    ])
    mock = strict_mock(Iterator, "ForLoop", expected_calls)
    actual = []
    for n in mock:
        actual.append(n)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_for_loop_with_helper_returns_expected_values():
    # you can set up the expected values by using the convenience
    # function expected_iter
    expected = [1, 2, 3]
    expected_calls = Events(expected_iter([1, 2, 3]))
    mock = strict_mock(Iterator, "ForLoop", expected_calls)
    actual = []
    for n in mock:
        actual.append(n)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_comprehension_returns_expected_values():
    # comprehensions are similar to for loops
    # however, for some odd reason it requires
    # an additional __iter__ at the beginning
    expected = [1, 2, 3]
    expected_calls = Events([
        Expected("__next__").returns_value(1),
        Expected("__next__").returns_value(2),
        Expected("__next__").returns_value(3),
        Expected("__next__").stop_iteration(),
    ])
    mock = strict_mock(Iterator, "Passes", expected_calls)
    actual = [n for n in mock]

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_next_returns_expected_values():
    # using only next() means that we need a value
    # to break the loop
    expected = [1, 2, 3]
    expected_calls = Events([
        Expected("__next__").returns_value(1),
        Expected("__next__").returns_value(2),
        Expected("__next__").returns_value(3),
        Expected("__next__").returns_value(4),
    ])
    mock = strict_mock(Iterator, "Passes", expected_calls)
    actual = []
    while n := next(mock):
        if n > 3:
            break
        actual.append(n)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_next_using_expected_iter_returns_expected_values():
    # using only next() means that we need a value
    # to break the loop
    expected = [2, 3]
    expected_calls = Events(expected_iter([1, 2, 3, 4])[1:4])
    mock = strict_mock(Iterator, "Passes", expected_calls)
    actual = []
    while n := next(mock):
        if n > 3:
            break
        actual.append(n)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_next_false_returns_expected_values():
    # an alternative is to return false to break a loop
    expected = [1, 2, 3]
    expected_calls = Events([
        Expected("__next__").returns_value(1),
        Expected("__next__").returns_value(2),
        Expected("__next__").returns_value(3),
        Expected("__next__").returns_value(False),
    ])
    mock = strict_mock(Iterator, "Passes", expected_calls)
    actual = []
    while n := next(mock):
        actual.append(n)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_iterator_iter():
    expected = [1, 2, 3]
    expected_calls = Events([
        Expected("__next__").returns_value(1),
        Expected("__next__").returns_value(2),
        Expected("__next__").returns_value(3),
        Expected("__next__").returns_value(False),
    ])
    mock = strict_mock(Iterator, "Passes", expected_calls)
    actual = []

    i = iter(mock)
    while n := next(i):
        actual.append(n)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()
