import unittest
from typing import Any, Optional, Union

from strict_mock import Events, Expected, MockError, strict_mock


class SampleClass:
    def method_no_return_specified(self):
        raise NotImplementedError()

    def method_explicit_none(self) -> None:
        raise NotImplementedError()

    def method_explicit_type(self) -> int:
        raise NotImplementedError()

    def method_optional_type(self) -> Optional[int]:
        raise NotImplementedError()

    def method_union_type(self) -> Union[int, str]:
        raise NotImplementedError()

    def method_returns_any(self) -> Any:
        raise NotImplementedError()


class TestExampleReturnValues(unittest.TestCase):
    def test_no_return_specified_returns_any(self):
        cases = [
            (None, [Expected("method_no_return_specified")]),
            (None, [Expected("method_no_return_specified").returns_value(None)]),
            (123, [Expected("method_no_return_specified").returns_value(123)]),
            ("123", [Expected("method_no_return_specified").returns_value("123")]),
        ]
        for expected, expected_calls in cases:
            with self.subTest(expected=expected, expected_calls=expected_calls):
                mock = strict_mock(SampleClass, events=Events(expected_calls))
                actual = mock.method_no_return_specified()

                self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
                mock.assert_all_calls()

    def test_explicit_none_returns_none(self):
        cases = [
            [Expected("method_explicit_none")],
            [Expected("method_explicit_none").returns_value(None)]
        ]
        for expected_calls in cases:
            with self.subTest(expected_calls=expected_calls):
                mock = strict_mock(SampleClass, events=Events(expected_calls))
                actual = mock.method_explicit_none()
                self.assertIsNone(actual)
                mock.assert_all_calls()

    def test_explicit_none_raises_error(self):
        expected = (
            'StrictMock: StrictMockSampleClass Discrepancies\n'
            'Data Length\n'
            '    expected: 1\n'
            '    actual  : 1\n'
            '               0: Expected("method_explicit_none").returns_value(123)\n'
            '                      method_explicit_none: return_type; expected: None; actual: int(123)\n'
            '                      fix: Expected("method_explicit_none")\n'
            '               0: Actual("method_explicit_none")\n\n'
        )
        expected_calls = [
            Expected("method_explicit_none").returns_value(123),
        ]
        mock = strict_mock(SampleClass, events=Events(expected_calls))
        with self.assertRaises(MockError) as ex:
            mock.method_explicit_none()
        actual = str(ex.exception)
        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_method_explicit_type_returns_type(self):
        expected = 37
        expected_calls = Events([
            Expected("method_explicit_type").returns_value(37),
        ])
        mock = strict_mock(SampleClass, events=expected_calls)
        actual = mock.method_explicit_type()

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual:  {actual}")
        mock.assert_all_calls()

    def test_method_optional_type_raises_error(self):
        cases = [
            ("", "NoneType(None)", [Expected("method_explicit_type")]),
            (".returns_value(None)", "NoneType(None)", [Expected("method_explicit_type").returns_value(None)]),
            ('.returns_value([1, 2, 3])', 'list([1, 2, 3])',
             [Expected("method_explicit_type").returns_value([1, 2, 3])]),
        ]
        for rv, tv, expected_calls in cases:
            with self.subTest(rv=rv, tv=tv, expected_calls=expected_calls):
                expected = (
                    'StrictMock: StrictMockExplicitTypeErrors Discrepancies\n'
                    'Data Length\n'
                    '    expected: 1\n'
                    '    actual  : 1\n'
                    f'               0: Expected("method_explicit_type"){rv}\n'
                    f'                      method_explicit_type: return_type; expected: int; actual: {tv}\n'
                    '                      fix: Expected("method_explicit_type").returns_value(int)\n'
                    '               0: Actual("method_explicit_type")\n\n'
                )
                mock = strict_mock(SampleClass, "StrictMockExplicitTypeErrors", Events(expected_calls))
                with self.assertRaises(MockError) as ex:
                    _ = mock.method_explicit_type()
                actual = str(ex.exception)
                self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual:  {actual}")
                mock.assert_all_calls()

    def test_method_optional_type_returns_type(self):
        cases = [
            (None, [Expected("method_optional_type")]),
            (None, [Expected("method_optional_type").returns_value(None)]),
            (83, [Expected("method_optional_type").returns_value(83)]),
        ]
        for expected, expected_calls in cases:
            with self.subTest(expected=expected, expected_calls=expected_calls):
                mock = strict_mock(SampleClass, events=Events(expected_calls))
                actual = mock.method_optional_type()
                self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual:  {actual}")
                mock.assert_all_calls()

    def test_method_union_type_raises_error(self):
        cases = [
            ("", "NoneType(None)", [Expected("method_union_type")]),
            (".returns_value(None)", "NoneType(None)", [Expected("method_union_type").returns_value(None)]),
        ]
        for rv, tv, expected_calls in cases:
            with self.subTest(rv=rv, tv=tv, expected_calls=expected_calls):
                expected = (
                    'StrictMock: StrictMockExplicitTypeErrors Discrepancies\n'
                    'Data Length\n'
                    '    expected: 1\n'
                    '    actual  : 1\n'
                    f'               0: Expected("method_union_type"){rv}\n'
                    f'                      method_union_type: return_type; expected: Union[int, str]; actual: {tv}\n'
                    '                      fix: Expected("method_union_type").returns_value(Union[int, str])\n'
                    '               0: Actual("method_union_type")\n\n'
                )
                mock = strict_mock(SampleClass, "StrictMockExplicitTypeErrors", Events(expected_calls))
                with self.assertRaises(MockError) as ex:
                    _ = mock.method_union_type()
                actual = str(ex.exception)
                self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual:  {actual}")
                mock.assert_all_calls()

    def test_method_union_type_returns_type(self):
        cases = [
            (83, [Expected("method_union_type").returns_value(83)]),
            ("abc", [Expected("method_union_type").returns_value("abc")]),
        ]
        for expected, expected_calls in cases:
            with self.subTest(expected=expected, expected_calls=expected_calls):
                mock = strict_mock(SampleClass, events=Events(expected_calls))
                actual = mock.method_union_type()
                self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual:  {actual}")
                mock.assert_all_calls()

    def test_method_returns_any(self):
        cases = [
            (None, [Expected("method_returns_any")]),
            (None, [Expected("method_returns_any").returns_value(None)]),
            (123, [Expected("method_returns_any").returns_value(123)]),
            ("123", [Expected("method_returns_any").returns_value("123")]),
        ]
        for expected, expected_calls in cases:
            with self.subTest(expected=expected, expected_calls=expected_calls):
                mock = strict_mock(SampleClass, events=Events(expected_calls))
                actual = mock.method_returns_any()
                self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual:  {actual}")
                mock.assert_all_calls()
