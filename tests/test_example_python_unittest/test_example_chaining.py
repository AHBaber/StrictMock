import unittest

from strict_mock import (Events, Expected, MockCreationError, TypeIgnore,
                         strict_mock)

from ..fakes import Connection, Cursor, SimpleDao


class TestExampleChaining(unittest.TestCase):
    def test_chaining_cm_returns_sub_context_manager(self):
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

        cursor_mock = strict_mock(Cursor, "CursorMock", expected_calls)
        connection = strict_mock(Connection, "ConnectionMock", expected_calls)

        with connection:
            with connection.cursor() as cursor:
                query = "SELECT * FROM eg.example"
                cursor.execute(query)
                if cursor.rowcount > 0:
                    actual = [row for row in cursor]

        self.assertEqual(expected, actual, f"\nexpected: {expected}\nactual  : {actual}")
        connection.assert_all_calls()
        cursor_mock.assert_all_calls()

    def test_chaining_cm_values_ignored_returns_sub_context_manager(self):
        expected = [3, 5, 8]
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
        cursor_mock = strict_mock(Cursor, "CursorMock", expected_calls)
        connection = strict_mock(Connection, "ConnectionMock", expected_calls)

        dao = SimpleDao(connection)
        with connection:
            actual = dao.select_with_args(5, "something")

        self.assertEqual(expected, actual, f"\nexpected: {expected}\nactual  : {actual}")
        connection.assert_all_calls()
        cursor_mock.assert_all_calls()

    def test_chaining_mock_not_specified_raises_error(self):
        expected = """All chained mocks must be named when returning self;
    index  : 1
    current: Expected("cursor").returns_mock()
    fixed  : Expected("cursor").returns_mock("ConnectionMock")"""

        expected_calls = Events([
            Expected("__enter__").returns_mock("ConnectionMock"),
            Expected("cursor").returns_mock(),
        ])

        cursor_mock = strict_mock(Cursor, "CursorMock", expected_calls)
        connection = strict_mock(Connection, "ConnectionMock", expected_calls)

        dao = SimpleDao(connection)
        with self.assertRaises(MockCreationError) as ex:
            with connection:
                dao.select_with_args(5, "something")
        actual = str(ex.exception)

        self.assertEqual(expected, actual, f"\nexpected: {expected}\nactual  : {actual}")
        cursor_mock.assert_all_calls()
        connection.assert_all_calls()
