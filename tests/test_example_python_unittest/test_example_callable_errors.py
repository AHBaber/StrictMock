import unittest
from typing import Tuple

from strict_mock import Events, MockCallableError, strict_mock


class TestExampleCallableErrors(unittest.TestCase):
    def test_callable_function_no_expected_raises_error(self):
        def function():
            pass

        expected = (
            'StrictMock: StrictMockfunction Discrepancies\n'
            'Data Length\n'
            '    expected: 0\n'
            '    actual  : 1\n'
            'Extra          0: Actual("__call__")\n'
            '                      fix: Expected("__call__")\n\n'
        )

        mock = strict_mock(function)
        with self.assertRaises(MockCallableError) as ex:
            mock()
        actual = str(ex.exception)
        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_callable_function_no_expected_with_args_and_return_raises_error(self):
        def function(a: int, b: str, c: bool) -> Tuple[int, str]:
            raise NotImplementedError()

        expected = (
            'StrictMock: NoExpected Discrepancies\n'
            'Data Length\n'
            '    expected: 0\n'
            '    actual  : 1\n'
            'Extra          0: Actual("__call__", 12, "ghi", False)\n'
            '                      fix: Expected("__call__", a: int, b: str, c: bool).returns_value(Tuple[int, str])\n\n'  # noqa E501
        )

        expected_calls = Events([])
        mock = strict_mock(function, "NoExpected", expected_calls)
        with self.assertRaises(MockCallableError) as ex:
            _ = mock(12, "ghi", False)
        actual = str(ex.exception)
        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_callable_object_no_expected_raises_error(self):
        class CallClass:
            def __call__(self, a: int, b: str) -> int:
                raise NotImplementedError

        expected = (
            'StrictMock: CallClass Discrepancies\n'
            'Data Length\n'
            '    expected: 0\n'
            '    actual  : 1\n'
            'Extra          0: Actual("__call__", a=12, b="key")\n'
            '                      fix: Expected("__call__", a: int, b: str).returns_value(int)\n\n'
        )
        expected_calls = Events([])
        mock = strict_mock(CallClass, "CallClass", expected_calls)
        with self.assertRaises(MockCallableError) as ex:
            _ = mock(a=12, b="key")
        actual = str(ex.exception)
        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()
