import unittest

from strict_mock import Events, Expected, ValueIgnore, strict_mock

from ..fakes import FakeMock


class TestExampleEquality(unittest.TestCase):
    def test_method_equal_returns_expected_value(self):
        expected = False
        expected_calls = Events([
            Expected("__eq__", ValueIgnore).returns_value(False),
        ])
        mock1 = strict_mock(FakeMock, "Equal1", expected_calls)
        mock2 = strict_mock(FakeMock, "Equal2", Events([]))

        actual = mock1 == mock2

        mock1.assert_all_calls()
        mock2.assert_all_calls()
        self.assertEqual(expected, actual, f"\nexpected: {expected}\nactual  : {actual}")

    def test_method_not_equal_returns_expected_value(self):
        expected = True
        expected_calls = Events([
            Expected("__ne__", ValueIgnore).returns_value(True),
        ])
        mock1 = strict_mock(FakeMock, "Equal1", expected_calls)
        mock2 = strict_mock(FakeMock, "Equal2", Events([]))

        actual = mock1 != mock2

        mock1.assert_all_calls()
        mock2.assert_all_calls()
        self.assertEqual(expected, actual, f"\nexpected: {expected}\nactual  : {actual}")

    def test_method_less_than_returns_expected_value(self):
        expected = True
        expected_calls = Events([
            Expected("__lt__", ValueIgnore).returns_value(True),
        ])
        mock1 = strict_mock(FakeMock, "Equal1", expected_calls)
        mock2 = strict_mock(FakeMock, "Equal2", Events([]))

        actual = mock1 < mock2  # type: ignore

        mock1.assert_all_calls()
        mock2.assert_all_calls()
        self.assertEqual(expected, actual, f"\nexpected: {expected}\nactual  : {actual}")

    def test_method_greater_than_returns_expected_value(self):
        expected = True
        expected_calls = Events([
            Expected("__gt__", ValueIgnore).returns_value(True),
        ])
        mock1 = strict_mock(FakeMock, "Equal1", expected_calls)
        mock2 = strict_mock(FakeMock, "Equal2", Events([]))

        actual = mock1 > mock2  # type: ignore

        mock1.assert_all_calls()
        mock2.assert_all_calls()
        self.assertEqual(expected, actual, f"\nexpected: {expected}\nactual  : {actual}")

    def test_method_less_than_equal_returns_expected_value(self):
        expected = True
        expected_calls = Events([
            Expected("__le__", ValueIgnore).returns_value(True),
        ])
        mock1 = strict_mock(FakeMock, "Equal1", expected_calls)
        mock2 = strict_mock(FakeMock, "Equal2", Events([]))

        actual = mock1 <= mock2  # type: ignore

        mock1.assert_all_calls()
        mock2.assert_all_calls()
        self.assertEqual(expected, actual, f"\nexpected: {expected}\nactual  : {actual}")

    def test_method_greater_than_equal_returns_expected_value(self):
        expected = True
        expected_calls = Events([
            Expected("__ge__", ValueIgnore).returns_value(True),
        ])
        mock1 = strict_mock(FakeMock, "Equal1", expected_calls)
        mock2 = strict_mock(FakeMock, "Equal2", Events([]))

        actual = mock1 >= mock2  # type: ignore

        mock1.assert_all_calls()
        mock2.assert_all_calls()
        self.assertEqual(expected, actual, f"\nexpected: {expected}\nactual  : {actual}")
