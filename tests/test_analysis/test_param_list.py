import inspect
from typing import Any, Dict, List, Optional, Tuple, Type

import pytest

from strict_mock.analysis import Param, ParamList, get_params
from strict_mock.analysis.check_type import Empty

from .func_and_methods import (Class, function0, function0a, function0r,
                               function1, function1d, function2, function2d,
                               function3, functionArgs, functionArgsKwargs,
                               functionKeysOnly, functionKeysOnlyKwargs,
                               functionKwargs, functionPosOnly,
                               functionPosOnlyVarPos)

_ip = inspect.Parameter
_vp = inspect.Parameter.VAR_POSITIONAL
_vk = inspect.Parameter.VAR_KEYWORD
_po = inspect.Parameter.POSITIONAL_ONLY
_ko = inspect.Parameter.KEYWORD_ONLY


@pytest.mark.parametrize("func, expected", [
    (function0, []),
    (function0a, []),
    (function1, [Param("a", int)]),
    (function2, [Param("a", int), Param("b", str)]),
    (function3, [
        Param("a", int),
        Param("b", str),
        Param("c", Dict[str, List[int]]),
    ]),
    (function1d, [Param("a", Optional[int], None)]),
    (function2d, [Param("x", int), Param("y", int, 0)]),
    (function0r, []),
    (function0a, []),
    (functionArgs, [Param("args", Any, kind=_vp)]),
    (functionKwargs, [Param("kwargs", Any, kind=_vk)]),
    (functionArgsKwargs, [
        Param("args", Any, kind=_vp),
        Param("kwargs", Any, kind=_vk),
    ]),
    (functionPosOnly, [
        Param("a", bool, kind=_po),
        Param("b", int, kind=_po),
    ]),
    (functionPosOnlyVarPos, [
        Param("a", bool, kind=_po),
        Param("b", int, kind=_po),
        Param("dimensions", str, kind=_vp),
    ],),
    (functionKeysOnly, [
        Param("a", bool, kind=_ko),
        Param("b", int, kind=_ko),
    ]),
    (functionKeysOnlyKwargs, [
        Param("a", bool, kind=_ko),
        Param("b", int, kind=_ko),
        Param("k_dimensions", Any, kind=_vk),
    ]),

    (Class.method0, []),
    (Class.method0a, []),
    (Class.method1, [Param("a", int)]),
    (Class.method2, [Param("a", int), Param("b", str)]),
    (Class.method3, [
        Param("a", int),
        Param("b", str),
        Param("c", Dict[str, List[int]]),
    ]),
    (Class.method1d, [Param("a", Optional[int], None)]),
    (Class.method2d, [Param("x", int), Param("y", int, 0)]),
    (Class.method0r, []),
    (Class.method0a, []),
    (Class.methodArgs, [Param("args", Any, kind=_vp)]),
    (Class.methodKwargs, [Param("kwargs", Any, kind=_vk)]),
    (Class.methodArgsKwargs, [
        Param("args", Any, kind=_vp),
        Param("kwargs", Any, kind=_vk),
    ]),
    (Class.methodPosOnly, [
        Param("a", bool, kind=_po),
        Param("b", int, kind=_po),
    ]),
    (Class.methodPosOnlyVarPos, [
        Param("a", bool, kind=_po),
        Param("b", int, kind=_po),
        Param("dimensions", str, kind=_vp),
    ],),
    (Class.methodKeysOnly, [
        Param("a", bool, kind=_ko),
        Param("b", int, kind=_ko),
    ]),
    (Class.methodKeysOnlyKwargs, [
        Param("a", bool, kind=_ko),
        Param("b", int, kind=_ko),
        Param("k_dimensions", Any, kind=_vk),
    ]),

])
def test_get_params_functions_returns_expected(func, expected):
    for i, e in enumerate(expected):  # sets index of params automatically
        e.index = i
    pl = get_params(func)
    actual = pl.params()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_param_list_params_self_skipped():
    expected: List[Param] = []
    pl = ParamList([Param("self")])
    actual = pl.params()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_param_list_method_self_not_returned():
    expected: List[Param] = [
        Param("a", int, index=1),
        Param("b", str, index=2),
        Param("c", Dict[str, List[int]], index=3),
    ]
    pl = get_params(Class.method3)
    actual = pl.params()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_param_list_self_set_to_checked():
    p = Param("self")
    assert p.checked is False

    pl = ParamList()
    pl.append(p)
    assert p.checked is True


def test_param_list_remaining_are_unchecked():
    expected: List[Param] = [
        Param("a", int, index=1),
        Param("b", str, index=2),
        Param("c", Dict[str, List[int]], index=3),
    ]
    pl = get_params(Class.method3)
    actual = pl.remaining()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_param_list_get_returns_expected():
    expected1 = Param("b", str, Empty, checked=True, index=1)
    expected2 = False
    pl = get_params(function3)
    actual1 = None
    if "b" in pl:
        actual1 = pl.get("b")
    actual2 = "b" in pl  # no longer available

    assert actual1 == expected1, f"\nexpected: {expected1}\nactual  : {actual1}"
    assert actual2 == expected2, f"\nexpected: {expected2}\nactual  : {actual2}"


def test_param_list_by_init_get_returns_expected():
    expected1 = Param("b", str, Empty, checked=True, index=1)
    expected2 = False
    pl = ParamList([Param("b", str)])
    actual1 = None
    if "b" in pl:
        actual1 = pl.get("b")
    actual2 = "b" in pl  # no longer available

    assert actual1 == expected1, f"\nexpected: {expected1}\nactual  : {actual1}"
    assert actual2 == expected2, f"\nexpected: {expected2}\nactual  : {actual2}"


@pytest.mark.parametrize("expected, f", [
    (Param("return_type"), function0),
    (Param("return_type", None), function1),
    (Param("return_type", Dict[str, List[Tuple[int, str]]]), function0r),
    (Param("return_type", Any), function0a),
    (Param("return_type"), Class.method0),
    (Param("return_type", None), Class.method1),
    (Param("return_type", Dict[int, List[Dict[int, str]]]), Class.method0r),
    (Param("return_type", Any), Class.method0a),
])
def test_param_list_return_value(expected: Param, f):
    pl = get_params(f)
    actual = pl.return_type
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


params = [
    (function0, [], ""),
    (function1, [Param("a", int)], "a: int"),
    (function2, [
        Param("a", int),
        Param("b", str, index=1),
    ], "a: int, b: str"),
    (function3, [
        Param("a", int),
        Param("b", str, Empty, index=1),
        Param("c", Dict[str, List[int]], Empty, index=2),
    ], "a: int, b: str, c: Dict[str, List[int]]"),
    (function1d,
     [Param("a", Optional[int], None)],
     "a: Optional[int] = None"),
    (function2d,
     [Param("x", int), Param("y", int, 0, index=1)],
     "x: int, y: int = 0"),
    (Class.method0, [], ""),
    (Class.method1,
     [Param("a", int, index=1)],
     "a: int"),
]


@pytest.mark.parametrize("f, expected, _", params)
def test_get_params_functions_params(f, expected, _):
    pl = get_params(f)
    actual = pl.params()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("f, _, expected", params)
def test_get_params_functions_param_str(f, _, expected):
    pl = get_params(f)
    actual = pl.as_param_str()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("expected, rv, p", [
    ('fix: Expected("method")', Empty, []),
    ('fix: Expected("method")', None, []),
    ('fix: Expected("method").returns_value(Any)', Any, []),
    ('fix: Expected("method").returns_value(int)', int, []),
    ('fix: Expected("method", a: int)', None, [Param("a", int)]),
    ('fix: Expected("method", a: int).returns_value(int)', int, [Param("a", int)]),
    ('fix: Expected("method", index: int, lang: str = "enUS").returns_value(str)', str,
     [Param("self"), Param("index", int), Param("lang", str, "enUS")]),
    ('fix: Expected("method", setter: int)', None, [Param("self"), Param("setter", int)]),
])
def test_param_list_as_fix_method_returns_expected_value(expected: str, rv: Optional[Type], p: List[Param]):
    pl = ParamList(p)
    pl.add_return_type(rv)
    actual = pl.as_fix_method("method")
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("func, expected", [
    (function0, "ParamList()"),
    (function1, "ParamList(int)->None"),
    (function2, "ParamList(int,str)"),
    (function3, "ParamList(int,str,Dict[str, List[int]])"),
    (function1d, "ParamList(Optional[int])"),
    (function2d, "ParamList(int,int)"),
    (function0r, "ParamList()->Dict[str, List[Tuple[int, str]]]"),
    (function0a, "ParamList()->Any"),
    (Class.method0, "ParamList(self)"),
    (Class.method1, "ParamList(self,int)->None"),
    (Class.method3, "ParamList(self,int,str,Dict[str, List[int]])->None"),
    (Class.method0r, "ParamList(self)->Dict[int, List[Dict[int, str]]]"),
    (Class.method0a, "ParamList(self)->Any"),
])
def test_param_list_repr_returns_expected_value(func, expected):
    pl = get_params(func)
    actual = repr(pl)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_param_list_param_keys_returns_expected_value():
    expected: Dict[str, Param] = {
        "x": Param("x", int),
        "y": Param("y", int, 0, index=1),
    }
    pl = get_params(function2d)
    actual = pl.param_keys()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("f, expected, offset", [
    (function0a, None, 0),  # empty args
    (function1, Param("a", int), 0),  # first arg
    (function1, None, 1),  # no second arg, checks index was moved forward
    (function0a, None, 0),  # empty args
    (functionKwargs, None, 0),  # no positional, only kwargs
    (functionPosOnlyVarPos, Param("a", bool), 0),
    (functionPosOnlyVarPos, Param("b", int), 1),
    (functionPosOnlyVarPos, Param("dimensions", str), 2),  # variadic
    (functionPosOnlyVarPos, Param("dimensions", str), 3),  # variadic
    (Class.method1, Param("a", int), 0),  # gets first past self
    (Class.static_method, Param("a", bool), 0),
    (Class.class_method0, None, 0),
    (Class.class_method1, Param("c", str), 0),
    (Class.static_pos_only, Param("a", str), 0),
    (Class.static_pos_only, None, 1),
    (Class.class_pos_only, Param("c", str), 0),
    (Class.class_pos_only, None, 1),
])
def test_param_list_get_next_positional_returns_none(f, expected, offset):
    pl = get_params(f)
    actual: Optional[Param] = None
    for i in range(offset + 1):
        actual = pl.get_next_positional()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("f, expected, offset, used", [
    (function0a, None, 0, 0),  # empty args
    (functionKwargs, None, 0, 0),  # no positional, only kwargs
    (functionPosOnlyVarPos, Param("a", bool), 0, 0),
    (functionPosOnlyVarPos, Param("b", int), 1, 0),
    (functionPosOnlyVarPos, None, 2, 0),  # variadic is skipped
    (functionPosOnlyVarPos, Param("b", int), 0, 1),  # first used, second remaining
    (Class.method1, None, 0, 0),  # may be used as kwarg
    (Class.static_method, None, 0, 0),  # may be used as kwarg
    (Class.class_method0, None, 0, 0),  # may be used as kwarg
    (Class.class_method1, None, 0, 0),  # may be used as kwarg
    (Class.static_pos_only, Param("a", str), 0, 0),
    (Class.static_pos_only, None, 0, 1),
    (Class.class_pos_only, Param("c", str), 0, 0),
    (Class.class_pos_only, None, 0, 1),
])
def test_param_list_get_only_positional_returns_expected(f, expected, offset, used):
    pl = get_params(f)
    actual: Optional[Param] = None
    for i in range(used):
        _ = pl.get_next_positional()
    for i in range(offset + 1):
        actual = pl.get_remaining_positional()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
