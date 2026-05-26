from sys import getsizeof
from typing import Any, Callable, Dict, List, Type

import pytest

from strict_mock import Events, Expected, MockCreationError
from strict_mock.implementations import (BaseMock, default_dunders,
                                         get_spec_dict)

from ..fake_mock import FakeMock


def _create_mock(spec: Type[Any], name: str, expected: List[Expected]):
    events = Events(expected)
    spec_mocked: Dict[str, Callable] = {}
    spec_dict = get_spec_dict(spec)
    for d, v in default_dunders.items():
        if d in spec_dict:
            spec_mocked[d] = v

    mock_type = type(f'StrictMockTesting:{name}', (BaseMock, spec), spec_mocked)
    return mock_type(spec, name, events)


class Implements:
    def __bool__(self) -> bool:
        raise NotImplementedError()

    def __int__(self) -> int:
        raise NotImplementedError()

    def __float__(self) -> float:
        raise NotImplementedError()

    def __bytes__(self) -> bytes:
        raise NotImplementedError()

    def __complex__(self) -> complex:
        raise NotImplementedError()

    def __index__(self) -> int:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()


conversion_params = [
    # dunder, lam, r_type, expected, is_obj
    # is_obj means that it is implemented in object
    ("__bool__", lambda m: bool(m), "bool", True, False),
    ("__bytes__", lambda m: bytes(m), "bytes", b"chomp", False),
    ("__complex__", lambda m: complex(m), "complex", complex(3, 2), False),
    ("__float__", lambda m: float(m), "float", 3.2, False),
    ("__hash__", lambda m: hash(m), "int", 12, True),
    ("__index__", lambda m: int(hex(m), 16), "int", 17, False),
    ("__int__", lambda m: int(m), "int", 23, False),
    # ("__repr__", lambda m: repr(m), "str", "rep", True),
    ("__sizeof__", lambda m: getsizeof(m) - 32, "int", 23, True),
    # ("__str__", lambda m: str(m), "str", "string", True),
]


@pytest.mark.parametrize("dunder, lam, expected, is_obj", [
    (dunder, lam, expected, is_obj) for dunder, lam, _, expected, is_obj in conversion_params
])
def test_dunder_type_conversion_returns_expected_value(dunder, lam, expected, is_obj):
    expected_calls: List[Expected] = [
        Expected(dunder).returns_value(expected),
    ]
    spec = FakeMock if is_obj else Implements
    mock = _create_mock(spec, "", expected_calls)
    actual = lam(mock)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock._events._assert_all_calls(mock)


@pytest.mark.parametrize("dunder, lam, r_type, is_obj", [
    (dunder, lam, r_type, is_obj) for dunder, lam, r_type, _, is_obj in conversion_params
])
def test_dunder_type_conversion_raises_error(dunder, lam, r_type, is_obj):
    expected = (
        f'StrictMock: StrictMock{r_type} Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        f'Extra          0: Actual("{dunder}")\n'
        f'                      fix: Expected("{dunder}").returns_value({r_type})\n\n'
    )
    spec = FakeMock if is_obj else Implements
    mock = _create_mock(spec, f"StrictMock{r_type}", [])
    with pytest.raises(MockCreationError) as ex:
        lam(mock)
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock._events._assert_all_calls(mock)


@pytest.mark.parametrize("lam", [
    (lambda m: str(m)),
    (lambda m: repr(m)),
    (lambda m: f"{m:*>3}"),
])
def test_dunder_format_returns_expected_value(lam):
    expected = "FormattedMock"
    expected_calls: List[Expected] = [
        #  note lack of Expected
        # this is due to the fact that __str__,
        # __repr__, and __format__ are defined to
        # simply return the name
    ]
    mock = _create_mock(FakeMock, "FormattedMock", expected_calls)
    actual = f"{mock:*>3}"
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock._events._assert_all_calls(mock)
