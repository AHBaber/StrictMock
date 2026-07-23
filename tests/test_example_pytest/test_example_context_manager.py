import pytest

from strict_mock import (Events, Expected, MockContextManagerError, TypeIgnore,
                         ValueIgnore, strict_mock)
from tests.fakes.fake_connection import Connection, Cursor, SimpleDao


def test_context_manager_no_expected_raises_error():
    # when you first create the mock, if you don't have the expected_calls
    # filled out, then you will get errors
    # the lack of proper expected values will cause the mock to
    # raise an error as soon as the context manager is called
    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("__enter__")\n'
        '                      fix: Expected("__enter__")\n\n'
    )

    expected_calls = Events([])
    mock = strict_mock(Connection, "NoExpected", expected_calls)
    with pytest.raises(MockContextManagerError) as ex:
        with mock:
            pass
    actual = ex.value.args[0]
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_context_manager_returns_expected_values():
    # a context manager that runs with no errors will have a matching
    # __enter__ and __exit__
    expected_calls = Events([
        Expected("__enter__"),
        Expected("__exit__", None, None, None),
    ])
    mock = strict_mock(Connection, "NoExpected", expected_calls)
    with mock:
        pass

    assert mock.assert_all_calls()


def test_context_manager_raised_error_escapes_context():
    # if an error is supposed to occur within a context, then
    # You need to have the __exit__ call have three values:
    # the error type, the value of the error.
    # for the third parameter, we use ValueIgnore since
    # it will have a dynamic value in it.
    expected = "invaluable"
    expected_calls = Events([
        Expected("__enter__"),
        Expected("__exit__", ValueError, "invaluable", ValueIgnore).returns_value(False),
    ])
    mock = strict_mock(Connection, "NoExpected", expected_calls)
    with pytest.raises(ValueError) as ex:
        with mock:
            raise ValueError("invaluable")
    actual = ex.value.args[0]
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_context_manager_raised_error_swallowed():
    # if an error is supposed to be swallowed by the context
    # set the returns_value(True), and it will be swallowed by
    # the mock as well
    expected_calls = Events([
        Expected("__enter__").returns_mock(),
        Expected("__exit__", ValueError, "invaluable", ValueIgnore).returns_value(True),
    ])
    mock = strict_mock(Connection, "NoExpected", expected_calls)
    with mock:
        raise ValueError("invaluable")

    # IDE flags this as unreachable
    # but that is incorrect since True is returned from __exit__
    # which means the error is swallowed
    assert mock.assert_all_calls()


def test_cm_returns_sub_context_manager():
    expected = [3, 5, 8]
    expected_calls_cursor = Events([
        Expected("__enter__").returns_mock(),
        Expected("execute", "SELECT * FROM eg.example").returns_mock(),
        Expected("rowcount getter").returns_value(3),
        Expected("__next__").returns_value(3),
        Expected("__next__").returns_value(5),
        Expected("__next__").returns_value(8),
        Expected("__next__").stop_iteration(),
        Expected("__exit__", None, None, None),
    ])
    cursorMock = strict_mock(Cursor, "CursorMock", expected_calls_cursor)
    expected_calls_conn = Events([
        Expected("__enter__"),
        Expected("cursor").returns_value(cursorMock),
        Expected("__exit__", None, None, None),
    ])
    connection = strict_mock(Connection, "ConnectionMock", expected_calls_conn)

    dao = SimpleDao(connection)
    with connection:
        actual = dao.select_example()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert connection.assert_all_calls()
    assert cursorMock.assert_all_calls()


def test_cm_values_ignored_returns_sub_context_manager():
    expected = [5, 8, 13]
    params = dict(a=5, b="something")
    expected_calls_cursor = Events([
        Expected("__enter__").returns_mock(),
        Expected("execute", "SELECT * FROM eg.example WHERE a = %(a)s AND b = %(b)s;",
                 TypeIgnore(params)).returns_mock(),
        Expected("rowcount getter").returns_value(3),
        Expected("__next__").returns_value(5),
        Expected("__next__").returns_value(8),
        Expected("__next__").returns_value(13),
        Expected("__next__").stop_iteration(),
        Expected("__exit__", None, None, None),
    ])
    cursorMock = strict_mock(Cursor, "CursorMock", expected_calls_cursor)
    expected_calls_conn = Events([
        Expected("__enter__"),
        Expected("cursor").returns_value(cursorMock),
        Expected("__exit__", None, None, None),
    ])
    connection = strict_mock(Connection, "ConnectionMock", expected_calls_conn)

    dao = SimpleDao(connection)
    with connection:
        actual = dao.select_with_args(5, "something")

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert connection.assert_all_calls()
    assert cursorMock.assert_all_calls()
