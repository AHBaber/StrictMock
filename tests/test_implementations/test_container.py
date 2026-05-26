from operator import length_hint
from typing import Any, Callable, Dict, List, Type

import pytest

from strict_mock import Events, Expected
from strict_mock.implementations import (BaseMock, container_dunders,
                                         get_spec_dict)


def _create_mock(spec: Type[Any], name: str, expected: List[Expected]):
    events = Events(expected)
    spec_dict = get_spec_dict(spec)
    spec_mocked: Dict[str, Callable] = {}
    for d in container_dunders.keys():
        if d in spec_dict:
            spec_mocked[d] = container_dunders[d]
    mock_type = type(f'StrictMockTesting:{name}', (BaseMock, spec), spec_mocked)
    return mock_type(spec, name, events)


class ContainerMock:
    def __contains__(self, key: Any) -> bool:
        raise NotImplementedError()

    def __delitem__(self, key: Any) -> None:
        raise NotImplementedError()

    def __getitem__(self, key: Any) -> Any:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __reversed__(self) -> Any:
        raise NotImplementedError()

    def __setitem__(self, key: Any, value: Any) -> None:
        raise NotImplementedError()

    def delitem(self, key: Any) -> None:
        del self[key]


class ContainerHint:
    def __length_hint__(self) -> int:
        raise NotImplementedError()


params_keyed = [
    # dunder, type, arg, lam, expected, r_type
    ("__contains__", ContainerMock, "a", lambda m: "a" in m, True, bool),
    ("__getitem__", ContainerMock, "a", lambda m: m["a"], 23, int),
]


@pytest.mark.parametrize("dunder, type, arg, lam, expected", [
    (dunder, type, arg, lam, expected) for dunder, type, arg, lam, expected, _ in params_keyed
])
def test_container_keyed_passes(dunder, type, arg, lam, expected):
    expected_calls: List[Expected] = [
        Expected(dunder, arg).returns_value(expected),
    ]
    mock = _create_mock(type, f"Passes{dunder}", expected_calls)
    actual = lam(mock)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


params_no_keys = [
    # dunder, type, lam, expected
    ("__len__", ContainerMock, lambda m: len(m), 12),
    ("__length_hint__", ContainerHint, lambda m: length_hint(m), 23),
    ("__reversed__", ContainerMock, lambda m: reversed(m), [23, 12, 5]),
]


@pytest.mark.parametrize("dunder, type, lam, expected", params_no_keys)
def test_container_non_keyed_passes(dunder, type, lam, expected):
    expected_calls: List[Expected] = [
        Expected(dunder).returns_value(expected),
    ]
    mock = _create_mock(type, f"Passes{dunder}", expected_calls)
    actual = lam(mock)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_container_delete_item_passes():
    class DelClass:
        def __delitem__(self, key: Any) -> None:
            raise NotImplementedError()

    expected_calls: List[Expected] = [
        Expected("__delitem__", "a"),
    ]
    mock = _create_mock(DelClass, "Passes__delitem__", expected_calls)
    del mock["a"]
    assert mock.assert_all_calls()


def test_container_setitem_passes():
    expected_calls: List[Expected] = [
        Expected("__setitem__", "a", 5),
    ]
    mock = _create_mock(ContainerMock, "Passes__setitem__", expected_calls)
    mock["a"] = 5
    assert mock.assert_all_calls()
