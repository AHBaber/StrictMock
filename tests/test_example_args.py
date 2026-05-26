from typing import Optional, Sequence

import pytest

from strict_mock import Events, Expected, TypeIgnore, strict_mock


@pytest.mark.parametrize("args, kwargs", [
    ([1, "2", 3, True], {}),  # positional
    ([1, "2", 3], {}),  # positional / default
    ([], dict(a=1, b="2", c=3, d=True)),  # keywords
    ([], dict(a=1, b="2", c=3)),  # keywords /default
    ([1, "2"], dict(d=True, c=3)),  # positional / keyword
    ([], dict(a=1, d=True, c=3, b="2")),  # keywords mixed order
])
def test_args(args, kwargs):
    def function(a: int, b: str, c: int = 0, d: bool = False):
        raise NotImplementedError()

    expected_calls = Events([
        Expected("__call__", *args, **kwargs),
    ])
    mock = strict_mock(function, events=expected_calls)

    mock(*args, **kwargs)

    assert mock.assert_all_calls()


def test_defaults():
    def function(a: int, b: str, c: int = 0, d: bool = False):
        raise NotImplementedError()

    expected_calls = Events([
        Expected("__call__", 1, "2"),
    ])
    mock = strict_mock(function, events=expected_calls)

    mock(1, "2")

    assert mock.assert_all_calls()


def test_defaults_overridden():
    def function(a: int, b: str, c: int = 0, d: bool = False):
        raise NotImplementedError()

    expected_calls = Events([
        Expected("__call__", 1, "2", 3, False),
    ])
    mock = strict_mock(function, events=expected_calls)

    mock(1, "2", 3, False)

    assert mock.assert_all_calls()


@pytest.mark.parametrize("ti, params", [
    (False, None),
    (False, [1, 2, 3]),
    (True, dict(a=1, b="2", c=3, d=False)),
])
def test_type_ignore(ti, params):
    class Cursor:
        def execute(self, query: str, params: Optional[Sequence]):
            raise NotImplementedError()

    e_params = TypeIgnore(params) if ti else params
    expected_calls = Events([
        Expected("execute", "query", e_params),
    ])
    mock = strict_mock(Cursor, events=expected_calls)
    mock.execute("query", params)
    assert mock.assert_all_calls()
