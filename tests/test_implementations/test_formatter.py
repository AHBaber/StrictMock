from typing import List, Optional

import pytest

from strict_mock.analysis import (Actual, CheckType, ErrorExpected, Expected,
                                  Param, ParamList, TypeData)
from strict_mock.implementations import DefaultFormatter, IReportFormatter


class Dummy(IReportFormatter):
    def report(self, name: str,
               expected: List[Expected],
               actual: List[Actual],
               type_data: List[Optional[TypeData]]) -> str:
        return super().report(name, expected, actual, type_data)  # type: ignore


def test_i_report_formatter_report_raises_error():
    expected = "IReportFormatter.report() was not implemented"

    d = Dummy()
    with pytest.raises(NotImplementedError) as ex:
        d.report("", [], [], [])
    actual = str(ex.value)

    assert expected in actual, f"\nexpected: '{expected}'\nactual  : '{actual}'"


def test_default_formatter_report_no_data_returns_expected():
    expected = (
        'StrictMock: Empty Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 0\n\n'
    )
    e: List[Expected] = []
    a: List[Actual] = []
    formatter = DefaultFormatter()
    actual = formatter.report("Empty", e, a, [])
    assert actual == expected, f"\nexpected: '{expected}'\nactual  : '{actual}'"


def test_default_formatter_report_expected_only_returns_expected():
    expected = (
        'StrictMock: ExpectedOnly Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 0\n'
        'Extra          0: Expected("method1")\n\n'
    )
    e: List[Expected] = [
        Expected("method1"),
    ]
    a: List[Actual] = []
    formatter = DefaultFormatter()
    actual = formatter.report("ExpectedOnly", e, a, [])
    assert actual == expected, f"\nexpected: '{expected}'\nactual  : '{actual}'"


def test_default_formatter_report_actual_only_returns_expected():
    expected = (
        'StrictMock: ActualOnly Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("method1")\n'
        '                      positional: j; required type: int; actual value: "7"; index: 2;\n'
        '                      fix: Expected("method1", i: int, j: int)\n\n'
    )
    e: List[Expected] = []
    a: List[Actual] = [
        Actual("method1"),
    ]
    pl = ParamList([Param("self"), Param("i", int), Param("j", int)])
    td = TypeData("method1", CheckType(), pl)
    if td.check_types(5, "7"):
        td.as_fix_method()
    formatter = DefaultFormatter()
    actual = formatter.report("ActualOnly", e, a, [td])
    assert actual == expected, f"\nexpected: '{expected}'\nactual  : '{actual}'"


def test_default_formatter_report_1_row_returns_expected():
    expected = (
        'StrictMock: 1Row Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("method1")\n'
        '               0: Actual("method1")\n\n'
    )
    e: List[Expected] = [
        Expected("method1"),
    ]
    a: List[Actual] = [
        Actual("method1"),
    ]
    formatter = DefaultFormatter()
    actual = formatter.report("1Row", e, a, [None])
    assert actual == expected, f"\nexpected: '{expected}'\nactual  : '{actual}'"


def test_default_formatter_report_1_row_mismatch_returns_expected():
    expected = (
        'StrictMock: 1Row Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("method1", 5, 12)\n'
        '                      positional: j; required type: int; actual value: "7"; index: 2;\n'
        '                      fix: Expected("method2", i: int, j: int)\n'
        'Mismatched     0: Actual("method2", 5, "7")\n\n'
    )
    e: List[Expected] = [
        Expected("method1", 5, 12),
    ]
    a: List[Actual] = [
        Actual("method2", 5, "7"),
    ]
    pl = ParamList([Param("self"), Param("i", int), Param("j", int)])
    td = TypeData("method2", CheckType(), pl)
    if td.check_types(5, "7"):
        td.as_fix_method()
    formatter = DefaultFormatter()
    actual = formatter.report("1Row", e, a, [td])
    assert actual == expected, f"\nexpected: '{expected}'\nactual  : '{actual}'"


def test_default_formatter_report_error_expected_returns_expected():
    expected = (
        'StrictMock: ErrorExpectedReport Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Error          0: Error in Expected: Something went wrong\n'
        '                      fix: hopefully something useful\n'
        'Error          0: Actual("method1")\n\n'
    )
    e: List[Expected] = [
        ErrorExpected("Something went wrong", "hopefully something useful"),
    ]
    a: List[Actual] = [
        Actual("method1"),
    ]
    pl = ParamList([Param("self"), Param("i", int), Param("j", int)])
    td = TypeData("method1", CheckType(), pl)
    if td.check_types(5, 7):
        td.as_fix_method()
    formatter = DefaultFormatter()
    actual = formatter.report("ErrorExpectedReport", e, a, [td])
    assert actual == expected, f"\nexpected: '{expected}'\nactual  : '{actual}'"
