from typing import Any, Optional, Union

import pytest

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


@pytest.mark.parametrize("expected, expected_calls", [
    (None, [Expected("method_no_return_specified")]),
    (None, [Expected("method_no_return_specified").returns_value(None)]),
    (123, [Expected("method_no_return_specified").returns_value(123)]),
    ("123", [Expected("method_no_return_specified").returns_value("123")]),
])
def test_no_return_specified_returns_any(expected, expected_calls):
    mock = strict_mock(SampleClass, events=Events(expected_calls))
    actual = mock.method_no_return_specified()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


@pytest.mark.parametrize("expected_calls", [
    ([Expected("method_explicit_none")]),
    ([Expected("method_explicit_none").returns_value(None)]),
])
def test_explicit_none_returns_none(expected_calls):
    mock = strict_mock(SampleClass, events=Events(expected_calls))
    actual = mock.method_explicit_none()
    assert actual is None
    assert mock.assert_all_calls()


def test_explicit_none_raises_error():
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
    with pytest.raises(MockError) as ex:
        mock.method_explicit_none()
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_method_explicit_type_returns_type():
    expected = 37
    expected_calls = Events([
        Expected("method_explicit_type").returns_value(37),
    ])
    mock = strict_mock(SampleClass, events=expected_calls)
    actual = mock.method_explicit_type()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


@pytest.mark.parametrize("rv, tv, expected_calls", [
    ("", "NoneType(None)", [Expected("method_explicit_type")]),
    (".returns_value(None)", "NoneType(None)", [Expected("method_explicit_type").returns_value(None)]),
    ('.returns_value([1, 2, 3])', 'list([1, 2, 3])', [Expected("method_explicit_type").returns_value([1, 2, 3])]),
])
def test_method_optional_type_raises_error(rv, tv, expected_calls):
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
    with pytest.raises(MockError) as ex:
        _ = mock.method_explicit_type()
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


@pytest.mark.parametrize("expected, expected_calls", [
    (None, [Expected("method_optional_type")]),
    (None, [Expected("method_optional_type").returns_value(None)]),
    (83, [Expected("method_optional_type").returns_value(83)]),
])
def test_method_optional_type_returns_type(expected, expected_calls):
    mock = strict_mock(SampleClass, events=Events(expected_calls))
    actual = mock.method_optional_type()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


@pytest.mark.parametrize("rv, tv, expected_calls", [
    ("", "NoneType(None)", [Expected("method_union_type")]),
    (".returns_value(None)", "NoneType(None)", [Expected("method_union_type").returns_value(None)]),
    # ('.returns_value("123")', 'str("123")', [Expected("method_explicit_type").returns_value("123")]),
])
def test_method_union_type_raises_error(rv, tv, expected_calls):
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
    with pytest.raises(MockError) as ex:
        _ = mock.method_union_type()
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


@pytest.mark.parametrize("expected, expected_calls", [
    (83, [Expected("method_union_type").returns_value(83)]),
    ("abc", [Expected("method_union_type").returns_value("abc")]),
])
def test_method_union_type_returns_type(expected, expected_calls):
    mock = strict_mock(SampleClass, events=Events(expected_calls))
    actual = mock.method_union_type()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


@pytest.mark.parametrize("expected, expected_calls", [
    (None, [Expected("method_returns_any")]),
    (None, [Expected("method_returns_any").returns_value(None)]),
    (123, [Expected("method_returns_any").returns_value(123)]),
    ("123", [Expected("method_returns_any").returns_value("123")]),
])
def test_method_returns_any(expected, expected_calls):
    mock = strict_mock(SampleClass, events=Events(expected_calls))
    actual = mock.method_returns_any()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()
