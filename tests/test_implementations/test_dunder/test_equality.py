from typing import Any, Callable, Dict, List, Type

import pytest

from strict_mock import Events, Expected, MockCreationError
from strict_mock.analysis.utility import stringify
from strict_mock.implementations import (BaseMock, default_dunders,
                                         get_spec_dict)

from ..fake_mock import FakeMock


def _create_mock(spec: Type[Any], name: str, expected: List[Expected]):
    events = Events(expected)
    spec_dict = get_spec_dict(spec)
    spec_mocked: Dict[str, Callable] = {}
    for d, v in default_dunders.items():
        if d in spec_dict:
            spec_mocked[d] = v
    mock_type = type(f'StrictMockTesting:{name}', (BaseMock, spec), spec_mocked)
    return mock_type(spec, name, events)


comparison_params = [
    # dunder, lam, arg, expected
    ("__eq__", lambda m: m == "abc", "abc", False),
    ("__eq__", lambda m: m == 5, 5, True),
    ("__ne__", lambda m: m != "abc", "abc", False),
    ("__ne__", lambda m: m != 6, 6, True),
    ("__lt__", lambda m: m < "abc", "abc", True),
    ("__lt__", lambda m: m < 7, 7, False),
    ("__gt__", lambda m: m > "abc", "abc", False),
    ("__gt__", lambda m: m > 9, 9, True),
    ("__le__", lambda m: m <= "abc", "abc", False),
    ("__le__", lambda m: m <= 10, 10, True),
    ("__ge__", lambda m: m >= "abc", "abc", True),
    ("__ge__", lambda m: m >= 11, 11, False),
]


@pytest.mark.parametrize("dunder, lam, arg, expected", comparison_params)
def test_dunder_compare_returns_expected_value(dunder, lam, arg, expected):
    expected_calls: List[Expected] = [
        Expected(dunder, arg).returns_value(expected),
    ]
    mock = _create_mock(FakeMock, "", expected_calls)
    actual = lam(mock)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock._events._assert_all_calls(mock)


@pytest.mark.parametrize("dunder, lam, arg", [
    (dunder, lam, arg) for dunder, lam, arg, _ in comparison_params
])
def test_dunder_compare_raises_error(dunder, lam, arg):
    expected = (
        f'StrictMock: {dunder} Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        f'Extra          0: Actual("{dunder}", {stringify(arg)})\n'
        f'                      fix: Expected("{dunder}", ValueIgnore).returns_value(bool)\n\n'
    )
    mock = _create_mock(FakeMock, dunder, [])
    with pytest.raises(MockCreationError) as ex:
        lam(mock)
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock._events._assert_all_calls(mock)
