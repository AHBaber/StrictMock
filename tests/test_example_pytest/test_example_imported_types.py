import pytest

from strict_mock import (Events, Expected, ImportedTypes, MockCreationError,
                         TypeIgnore, strict_mock)
from tests.fakes.fake_connection import Connection, Cursor, SimpleDao

# these tests are the same as in test_example_chaining.py
# however they retain the usage of ImportedTypes to illustrate its use


def test_imported_types_returns_sub_context_manager():
    expected = [3, 5, 8]
    expected_calls = Events([
        Expected("__enter__"),
        Expected("cursor").returns_mock("CursorMock"),
        Expected("__enter__").returns_mock("CursorMock"),
        Expected("execute", "SELECT * FROM eg.example").returns_mock("CursorMock"),
        Expected("rowcount getter").returns_value(3),
        Expected("__next__").returns_value(3),
        Expected("__next__").returns_value(5),
        Expected("__next__").returns_value(8),
        Expected("__next__").stop_iteration(),
        Expected("__exit__", None, None, None),
        Expected("__exit__", None, None, None),
    ])
    it = ImportedTypes(Cursor)
    cursor_mock = strict_mock(Cursor, "CursorMock", expected_calls, imported=it)
    connection = strict_mock(Connection, "ConnectionMock", expected_calls, None, it)

    with connection:
        with connection.cursor() as cursor:
            query = "SELECT * FROM eg.example"
            cursor.execute(query)
            if cursor.rowcount > 0:
                actual = [row for row in cursor]

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert connection.assert_all_calls()
    assert cursor_mock.assert_all_calls()


def test_imported_types_values_ignored_returns_sub_context_manager():
    expected = [3, 5, 8]
    it = ImportedTypes(Cursor)
    params = dict(a=5, b="something")
    expected_calls = Events([
        Expected("__enter__").returns_mock("ConnectionMock"),
        Expected("cursor").returns_mock("CursorMock"),
        Expected("__enter__").returns_mock("CursorMock"),
        Expected("execute", "SELECT * FROM eg.example WHERE a = %(a)s AND b = %(b)s;",
                 TypeIgnore(params)).returns_mock("CursorMock"),
        Expected("rowcount getter").returns_value(3),
        Expected("__next__").returns_value(3),
        Expected("__next__").returns_value(5),
        Expected("__next__").returns_value(8),
        Expected("__next__").stop_iteration(),
        Expected("__exit__", None, None, None),
        Expected("__exit__", None, None, None),
    ])
    cursor_mock = strict_mock(Cursor, "CursorMock", expected_calls, imported=it)
    connection = strict_mock(Connection, "ConnectionMock", expected_calls, None, it)

    dao = SimpleDao(connection)
    with connection:
        actual = dao.select_with_args(5, "something")

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert connection.assert_all_calls()
    assert cursor_mock.assert_all_calls()


def test_imported_types_not_specified_raises_error():
    expected = """All chained mocks must be named when returning self;
    index  : 1
    current: Expected("cursor").returns_mock()
    fixed  : Expected("cursor").returns_mock("ConnectionMock")"""

    it = ImportedTypes(Cursor)
    expected_calls = Events([
        Expected("__enter__").returns_mock("ConnectionMock"),
        Expected("cursor").returns_mock(),
    ])

    cursor_mock = strict_mock(Cursor, "CursorMock", expected_calls, imported=it)
    connection = strict_mock(Connection, "ConnectionMock", expected_calls, None, it)

    dao = SimpleDao(connection)
    with pytest.raises(MockCreationError) as ex:
        with connection:
            dao.select_with_args(5, "something")
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert cursor_mock.assert_all_calls()
    assert connection.assert_all_calls()
