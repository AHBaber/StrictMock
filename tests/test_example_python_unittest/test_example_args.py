import unittest
from typing import Any, Dict, List, Optional, Sequence, Tuple

from strict_mock import Events, Expected, TypeIgnore, strict_mock


class TestExampleArgs(unittest.TestCase):
    def test_args(self):
        def function(a: int, b: str, c: int = 0, d: bool = False):
            raise NotImplementedError()

        cases: List[Tuple[List[Any], Dict[str, Any]]] = [
            ([1, "2", 3, True], {}),  # positional
            ([1, "2", 3], {}),  # positional / default
            ([], dict(a=1, b="2", c=3, d=True)),  # keywords
            ([], dict(a=1, b="2", c=3)),  # keywords /default
            ([1, "2"], dict(d=True, c=3)),  # positional / keyword
            ([], dict(a=1, d=True, c=3, b="2")),  # keywords mixed order
        ]
        for args, kwargs in cases:
            with self.subTest(args=args, kwargs=kwargs):
                expected_calls = Events([
                    Expected("__call__", *args, **kwargs),
                ])
                mock = strict_mock(function, events=expected_calls)
                mock(*args, **kwargs)

                mock.assert_all_calls()

    def test_defaults(self):
        def function(a: int, b: str, c: int = 0, d: bool = False):
            raise NotImplementedError()

        expected_calls = Events([
            Expected("__call__", 1, "2"),
        ])
        mock = strict_mock(function, events=expected_calls)
        mock(1, "2")
        mock.assert_all_calls()

    def test_defaults_overridden(self):
        def function(a: int, b: str, c: int = 0, d: bool = False):
            raise NotImplementedError()

        expected_calls = Events([
            Expected("__call__", 1, "2", 3, False),
        ])
        mock = strict_mock(function, events=expected_calls)
        mock(1, "2", 3, False)
        mock.assert_all_calls()

    def test_type_ignore(self):
        class Cursor:
            def execute(self, query: str, params: Optional[Sequence]):
                raise NotImplementedError()

        cases = [
            (False, None),
            (False, [1, 2, 3]),
            (True, dict(a=1, b="2", c=3, d=False)),
        ]
        for ti, params in cases:
            e_params = TypeIgnore(params) if ti else params
            expected_calls = Events([
                Expected("execute", "query", e_params),
            ])
            mock = strict_mock(Cursor, events=expected_calls)
            mock.execute("query", params)
            mock.assert_all_calls()
