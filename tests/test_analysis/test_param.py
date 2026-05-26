import inspect
from typing import (Any, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple,
                    Type, Union)

import pytest

from strict_mock.analysis import (Param, ParamDefault, ParamExtra, ParamIgnore,
                                  ParamValue)

_ip = inspect.Parameter


class SomeClass:
    pass


@pytest.mark.parametrize("expected, p", [
    ('Param("self")', Param("self")),
    ('Param("i", int)', Param("i", int)),
    ('Param("s", str, "abc")', Param("s", str, "abc")),
    ('Param("f", float, 3.14, POSITIONAL_ONLY)',
     Param("f", float, 3.14, _ip.POSITIONAL_ONLY)),
    ('Param("b", bool, True, POSITIONAL_OR_KEYWORD, True)',
     Param("b", bool, True, checked=True)),
    ('Param("b", bool, True, POSITIONAL_OR_KEYWORD, True, 3)',
     Param("b", bool, True, checked=True, index=3)),
    ('Param("a", int, _empty, POSITIONAL_OR_KEYWORD, False, 5)', Param("a", int, index=5)),
    ('ValueIgnore', ParamIgnore("pi")),
    ('Param("*args", Any, _empty, VAR_POSITIONAL)', Param("*args", Any, kind=_ip.VAR_POSITIONAL)),
    ('Param("*dims", Any, _empty, VAR_POSITIONAL)', Param("*dims", Any, kind=_ip.VAR_POSITIONAL)),
    ('Param("**kwargs", Any, _empty, VAR_KEYWORD)', Param("**kwargs", Any, kind=_ip.VAR_KEYWORD)),
    ('Param("**does", Any, _empty, VAR_KEYWORD)', Param("**does", Any, kind=_ip.VAR_KEYWORD)),
    ('Param("*args", Any, _empty, VAR_POSITIONAL)', Param("args", Any, kind=_ip.VAR_POSITIONAL)),
    ('Param("*dims", Any, _empty, VAR_POSITIONAL)', Param("dims", Any, kind=_ip.VAR_POSITIONAL)),
    ('Param("**kwargs", Any, _empty, VAR_KEYWORD)', Param("kwargs", Any, kind=_ip.VAR_KEYWORD)),
    ('Param("**does", Any, _empty, VAR_KEYWORD)', Param("does", Any, kind=_ip.VAR_KEYWORD)),
    ('Param("c", complex)', Param("c", complex)),
    ('Param("b", bytes)', Param("b", bytes)),
    ('Param("ba", bytearray)', Param("ba", bytearray)),
    ('Param("l", List[int])', Param("l", List[int])),
    ('Param("t", Tuple[int, str])', Param("t", Tuple[int, str])),
    ('Param("d", Dict[str, int])', Param("d", Dict[str, int])),
    ('Param("s", Set[str])', Param("s", Set[str])),
    ('Param("fs", FrozenSet[int])', Param("fs", FrozenSet[int])),
    ('Param("tp", Type[SomeClass])', Param("tp", Type[SomeClass])),
    ('Param("o", Optional[bool])', Param("o", Optional[bool])),
    ('Param("seq", Sequence[int])', Param("seq", Sequence[int])),
    ('Param("u", Union[int, str, bool])', Param("u", Union[int, str, bool])),
])
def test_param_repr_returns_expected_value(expected: str, p: Param):
    actual = repr(p)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("expected, p", [
    ('self', Param("self")),
    ('self', Param("self", int)),  # type is ignored for self
    ('i: int', Param("i", int)),
    ('i: int = 5', Param("i", int, 5)),
    ('345', ParamValue(value=345)),
    ('c=3', ParamValue(name="c", value=3)),
    ('extra: str("abc")', ParamExtra(extra="abc")),
    ('extra: ex=str("abc")', ParamExtra("ex", extra="abc")),
    ('a: bool = False', ParamDefault("a", bool, False)),
    ("ValueIgnore", ParamIgnore("pi")),
    ('f: float', Param("f", float)),
    ('f: float = 3.14', Param("f", float, 3.14)),
    ('c: complex', Param("c", complex)),
    ('s: str', Param("s", str)),
    ('s: str = "hello"', Param("s", str, "hello")),
    ('b: bytes', Param("b", bytes)),
    ('ba: bytearray', Param("ba", bytearray)),
    ('l: List', Param("l", List)),
    ('t: Tuple', Param("t", Tuple)),
    ('d: Dict', Param("d", Dict)),
    ('s: Set', Param("s", Set)),
    ('fs: FrozenSet', Param("fs", FrozenSet)),
    ('tp: Type', Param("tp", Type)),
    ('a: Any', Param("a", Any)),
    ('o: Optional', Param("o", Optional)),
    ('seq: Sequence', Param("seq", Sequence)),
    ('u: Union', Param("u", Union)),
])
def test_param_as_param_returns_expected_value(expected: str, p: Param):
    actual = p.as_param()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("p, is_positional, is_keyword, is_variadic", [
    (Param("a", int), True, True, False),
    (Param("a", bool, kind=_ip.POSITIONAL_ONLY), True, False, False),
    (Param("a", bool, kind=_ip.KEYWORD_ONLY), False, True, False),
    (Param("a", bool, kind=_ip.VAR_POSITIONAL), True, False, True),
    (Param("a", bool, kind=_ip.VAR_KEYWORD), False, True, True),
])
def test_param_kinds(p, is_positional, is_keyword, is_variadic):
    assert p.is_positional == is_positional
    assert p.is_keyword == is_keyword
    assert p.is_variadic == is_variadic


@pytest.mark.parametrize("expected, p1, p2", [
    (True, Param("a", int), Param("a", int)),
    (False, Param("a", int), Param("b", int)),
    (False, Param("a", int), Param("a", str)),
    (False, Param("a", int, 5), Param("a", int, 6)),
    (True, Param("a", int, 5, True), Param("a", int, 5, False)),
    (True, Param("a", int, 5, checked=True, index=1), Param("a", int, 5, checked=True, index=2)),
    (True, Param("a", Any), ParamIgnore("a")),
    (True, Param("b", str), ParamIgnore("a")),
    (False, Param("a", int), "not a Param"),
    (True, ParamIgnore("a"), Param("a", int)),
    (False, ParamIgnore("a"), "not a param"),
])
def test_param_eq_returns_expected_value(expected, p1, p2):
    actual = p1 == p2
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"

# @pytest.mark.parametrize("expected, p1, p2", [
#     (True, ParamIgnore("a"), Param("a", int)),
#     (False, ParamIgnore("a"), "not a param"),
# ])
# def test_param_ignore_eq_returns_expected_value(expected, p1, p2):
#     actual = p1 == p2
#     assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
