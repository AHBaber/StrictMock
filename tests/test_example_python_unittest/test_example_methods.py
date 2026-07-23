import unittest
from typing import List

from strict_mock import Events, Expected, MockMethodError, strict_mock


class TestExampleMethods(unittest.TestCase):
    def test_strict_mock_methods_none_expected_raises_error(self):
        # when you first create the mock, if you don't have the expected_calls
        # filled out, then you will get errors
        # the lack of proper expected values will cause the mock to
        # raise an error as soon as the method is called
        class NoExpected:
            def method_called(self):
                raise NotImplementedError

        expected = (
            'StrictMock: NoExpected Discrepancies\n'
            'Data Length\n'
            '    expected: 0\n'
            '    actual  : 1\n'
            'Extra          0: Actual("method_called")\n'
            '                      fix: Expected("method_called")\n\n'
        )
        expected_calls = Events([])

        mock = strict_mock(NoExpected, "NoExpected", expected_calls)
        with self.assertRaises(MockMethodError) as ex:
            mock.method_called()
        actual = str(ex.exception)
        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_strict_mock_methods_with_args_none_expected_raises_error(self):
        # if the method takes args, then it will tell you the types that
        # need to passed to create expected value properly
        class NoExpected:
            def method_called(self, a: int, b: str):
                raise NotImplementedError

        expected = (
            'StrictMock: NoExpected Discrepancies\n'
            'Data Length\n'
            '    expected: 0\n'
            '    actual  : 1\n'
            'Extra          0: Actual("method_called")\n'
            '                      fix: Expected("method_called", a: int, b: str)\n\n'
        )
        expected_calls = Events([])

        mock = strict_mock(NoExpected, "NoExpected", expected_calls)
        with self.assertRaises(MockMethodError) as ex:
            mock.method_called()
        actual = str(ex.exception)

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_strict_mock_methods_successful_call(self):
        # once the expected_calls is set, then the tests will pass
        class Successful:
            def method1(self):
                pass

            def method2(self, a: int, b: str):
                pass

        expected_calls = Events([
            Expected("method1"),
            Expected("method2", 5, "abc"),
        ])

        mock = strict_mock(Successful, "Successful", expected_calls)
        mock.method1()
        mock.method2(5, "abc")

        mock.assert_all_calls()

    def test_strict_mock_methods_return_value_not_set_raises_error(self):
        # if a method returns a value, the returned value must be set
        # or an error will be returned
        # a MockMethodError will be raised as soon as method is called
        # without a return value
        class NoReturnValue:
            def method_returns(self) -> int:
                raise NotImplementedError

        expected = (
            'StrictMock: NoReturnValue Discrepancies\n'
            'Data Length\n'
            '    expected: 1\n'
            '    actual  : 1\n'
            '               0: Expected("method_returns")\n'
            '                      method_returns: return_type; expected: int; actual: NoneType(None)\n'
            '                      fix: Expected("method_returns").returns_value(int)\n'
            '               0: Actual("method_returns")\n\n'
        )
        expected_calls = Events([
            Expected("method_returns"),
        ])

        mock = strict_mock(NoReturnValue, "NoReturnValue", expected_calls)
        with self.assertRaises(MockMethodError) as ex:
            mock.method_returns()
        actual = str(ex.exception)

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_strict_mock_methods_wrong_return_value_raises_error(self):
        # even if a return value is added to the expected calls, its
        # type must match
        class NoReturnValue:
            def method_returns(self) -> int:
                raise NotImplementedError

        expected = (
            'StrictMock: NoReturnValue Discrepancies\n'
            'Data Length\n'
            '    expected: 1\n'
            '    actual  : 1\n'
            '               0: Expected("method_returns").returns_value("abc")\n'
            '                      method_returns: return_type; expected: int; actual: str("abc")\n'
            '                      fix: Expected("method_returns").returns_value(int)\n'
            '               0: Actual("method_returns")\n\n'
        )
        expected_calls = Events([
            Expected("method_returns").returns_value("abc"),
        ])

        mock = strict_mock(NoReturnValue, "NoReturnValue", expected_calls)
        with self.assertRaises(MockMethodError) as ex:
            mock.method_returns()
        actual = str(ex.exception)

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_strict_mock_methods_method_raises_error(self):
        # you can choose to have a method raise an error instead.
        class MethodRaises:
            def method_raises(self):
                pass

        expected = "boom"
        expected_calls = Events([
            Expected("method_raises").raises_error(ValueError("boom")),
        ])

        mock = strict_mock(MethodRaises, "MethodRaises", expected_calls)
        with self.assertRaises(ValueError) as ex:
            mock.method_raises()
        actual = str(ex.exception)

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_strict_mock_methods_method_with_return_raises_error(self):
        # you can choose to have a method raise an error instead.
        class MethodRaises:
            def method_returns_raises(self):
                pass

        expected = "boom"
        expected_calls = Events([
            Expected("method_returns_raises").raises_error(ValueError("boom")),
        ])

        mock = strict_mock(MethodRaises, "MethodRaises", expected_calls)
        with self.assertRaises(ValueError) as ex:
            mock.method_returns_raises()
        actual = str(ex.exception)

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_strict_mock_methods_values_must_match_to_raise_error(self):
        # the actual values must match the expected values before the
        # error is raised, a MockMethodError is raised until it is fixed
        class MethodValuesRaises:
            def method(self, a: int, b: List[int]):
                pass

        expected = (
            'StrictMock: MethodValuesRaises Discrepancies\n'
            'Data Length\n'
            '    expected: 1\n'
            '    actual  : 1\n'
            'Mismatched     0: Expected("method", 5, [12]).raises_error(ValueError("bang!"))\n'
            '                      fix: Expected("method", a: int, b: List[int])\n'
            'Mismatched     0: Actual("method", 5, [13])\n\n'
        )
        expected_calls = Events([
            Expected("method", 5, [12]).raises_error(ValueError("bang!")),
        ])

        mock = strict_mock(MethodValuesRaises, "MethodValuesRaises", expected_calls)
        with self.assertRaises(MockMethodError) as ex:
            mock.method(5, [13])
        actual = str(ex.exception)

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_strict_mock_methods_with_defaults_successful_call(self):
        # if defaults are used in the called methods, then they do not appear in the
        # Expected list either
        # if the value appears in the called method, it needs to be in the Expected
        # list as well, even if the value is same as the default

        class Successful:
            def method1(self, a: int = 5):
                pass

            def method2(self, a: int, b: str = "abc"):
                pass

        expected_calls = Events([
            Expected("method1"),
            Expected("method1", 8),
            Expected("method1", 5),
            Expected("method2", 5),
            Expected("method2", 6, "abc"),
            Expected("method2", 7, "def"),
        ])

        mock = strict_mock(Successful, "Successful", expected_calls)
        mock.method1()
        mock.method1(8)
        mock.method1(5)
        mock.method2(5)
        mock.method2(6, "abc")
        mock.method2(7, "def")

        mock.assert_all_calls()
