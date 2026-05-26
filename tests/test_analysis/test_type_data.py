import inspect
from copy import deepcopy
from typing import FrozenSet, Set, Union

import pytest

from strict_mock.analysis import (CheckType, Empty, IValueEqual, Param,
                                  ParamList, TypeData, TypeIgnore, ValueIgnore,
                                  get_params)

from .func_and_methods import *  # noqa: F403

_p_or_k = inspect.Parameter.POSITIONAL_OR_KEYWORD


@pytest.mark.parametrize("pl, p", [
    (ParamList([Param("a", int)]), None),
    (None, Param("a", int)),
])
def test_type_data_constructor_returns_expected(pl, p):
    td = TypeData("ctor", CheckType(), pl, p)

    assert type(td) is TypeData


@pytest.mark.parametrize("t, rv, has_errors, expected", [
    (Empty, None, False, []),
    (Empty, 12, False, []),
    (None, None, False, []),
    (None, 12, True, [
        "ReturnType: return_type; expected: None; actual: int(12)",
        'fix: Expected("ReturnType")',
    ]),
    (Any, None, False, []),
    (Any, 27, False, []),
    (int, 5, False, []),
    (int, "a", True, [
        'ReturnType: return_type; expected: int; actual: str("a")',
        'fix: Expected("ReturnType").returns_value(int)',
    ]),
    (Empty, TypeIgnore(None), False, []),
    (Empty, TypeIgnore(12), False, []),
    (None, TypeIgnore(None), False, []),
    (None, TypeIgnore(12), False, []),
    (Any, TypeIgnore(None), False, []),
    (Any, TypeIgnore(27), False, []),
    (int, TypeIgnore(5), False, []),
    (int, TypeIgnore("5"), False, []),
])
def test_type_data_check_return_value(t, rv, has_errors, expected):
    pl = ParamList()
    pl.add_return_type(t)
    td = TypeData("ReturnType", CheckType(), pl)
    actual = td.check_return_value(rv)
    actual_errors = td.errors

    assert actual == has_errors
    assert actual_errors == expected, f"\nexpected: {expected}\nactual  : {actual_errors}"


params = [
    # e1, e2, pl, args, kwargs
    (False, 'a: Optional[int] = None', [Param("a", Optional[int], None)], [], {}),
    (False, '6', [Param("a", Optional[int], None)], [6], {}),
    (False, 'a=6', [Param("a", Optional[int], None)], [], dict(a=6)),
    (True, "a: Optional[int] = None", [Param("a", Optional[int], None)], ["b"], {}),
    (True, "a: Optional[int] = None", [Param("a", Optional[int], None)], [], dict(a="b")),
    (True, "5, extra: int(12), extra: int(23)",
     [Param("a", Optional[int], None)], [5, 12, 23], {}),
    (True, "a=5, extra: b=int(12), extra: c=int(23)",
     [Param("a", Optional[int], None)], [], dict(a=5, b=12, c=23)),
    (True, "a: int", [Param("a", int)], [], {}),
    (True, '5, c="3rd", b: bool', [Param("a", int), Param("b", bool), Param("c", str)], [5],
     dict(c="3rd")),
    (False, 'a: int = 5', [Param("a", int, 5)], [], {}),
    (True, 'a: int, b: int = 5', [Param("a", int), Param("b", int, 5)], [], {}),
    (False, 'None', [Param("a", type(None))], [None], {}),
    (True, 'a: None', [Param("a", type(None))], [1], {}),
    (False, 'None', [Param("a", Any)], [None], {}),
    (False, '"abc"', [Param("a", Any)], ["abc"], {}),
    (False, '[]', [Param("l", List[int])], [[]], {}),
    (False, '[7]', [Param("l", List[int])], [[7]], {}),
    (True, 'l: List[int]', [Param("l", List[int])], [["abc"]], {}),
    (False, "(1, 'a')", [Param("t", Tuple[int, str])], [(1, "a")], {}),
    (False, "t=(1, 'a')", [Param("t", Tuple[int, str])], [], dict(t=(1, "a"))),
    (True, "t: Tuple[int, str, bool]", [Param("t", Tuple[int, str, bool])], [(1,)], {}),
    (True, "t: Tuple[int, str, bool]", [Param("t", Tuple[int, str, bool])], [], dict(t=(1,))),
    (False, "{'dd': 4}", [Param("d", Dict[str, int])], [{"dd": 4}], {}),
    (False, "d={'dd': 4}", [Param("d", Dict[str, int])], [], dict(d={"dd": 4})),
    (True, "d: Dict[str, int]", [Param("d", Dict[str, int])], [{"dd": "ee"}], {}),
    (False, "{2}", [Param("s", Set[int])], [{2}], {}),
    (False, "s={2}", [Param("s", Set[int])], [], dict(s={2})),
    (True, "s: Set[int]", [Param("s", Set[int])], [{"a"}], {}),
    (False, "{}", [Param("f", FrozenSet[int])], [{}], {}),
    (False, "f={}", [Param("f", FrozenSet[int])], [], dict(f={})),
    (False, "{5}", [Param("f", FrozenSet[int])], [{5}], {}),
    (False, "f={6}", [Param("f", FrozenSet[int])], [], dict(f={6})),
    (True, "f: FrozenSet[int]", [Param("f", FrozenSet[int])], [{"a"}], {}),
    (True, "f: FrozenSet[int]", [Param("f", FrozenSet[int])], [], dict(f={"a"})),
    (False, "1", [Param("u", Union[str, int])], [1], {}),
    (False, "u=1", [Param("u", Union[str, int])], [], dict(u=1)),
    (False, '"abd"', [Param("u", Union[str, int])], ["abd"], {}),
    (False, 'u="cef"', [Param("u", Union[str, int])], [], dict(u="cef")),
    (False, '5, d: int = 23', [Param("a", int), Param("d", int, 23)], [5], {}),
]


@pytest.mark.parametrize("e1, e2, pl, args, kwargs", params)
def test_type_data_check_types(e1, e2, pl, args, kwargs):
    pl = deepcopy(pl)
    td = TypeData("ct2", CheckType(), ParamList(pl))
    a1 = td.check_types(*args, **kwargs)

    assert a1 == e1, f"\nexpected: {e1}\nactual  : {a1}"


@pytest.mark.parametrize("e1, e2, pl, args, kwargs", params)
def test_type_data_check_types_has_errors(e1, e2, pl, args, kwargs):
    pl = deepcopy(pl)
    td = TypeData("ct2", CheckType(), ParamList(pl))
    a1 = td.check_types(*args, **kwargs)

    assert a1 == td.has_errors


@pytest.mark.parametrize("e1, e2, pl, args, kwargs", params)
def test_type_data_check_types_as_param_str(e1, e2, pl, args, kwargs):
    pl = deepcopy(pl)
    td = TypeData("ct2", CheckType(), ParamList(pl))
    td.check_types(*args, **kwargs)
    actual = td.results.as_param_str("")

    assert actual == e2, f"\nexpected: {e2}\nactual  : {actual}"


@pytest.mark.parametrize("func, expected", [
    (function0, "TypeData(function0, CheckType(), ParamList())"),
    (function1, "TypeData(function1, CheckType(), ParamList(int)->None)"),
    (function2, "TypeData(function2, CheckType(), ParamList(int,str))"),
    (function3, "TypeData(function3, CheckType(), ParamList(int,str,Dict[str, List[int]]))"),
    (function1d, "TypeData(function1d, CheckType(), ParamList(Optional[int]))"),
    (function2d, "TypeData(function2d, CheckType(), ParamList(int,int))"),
    (function0r, "TypeData(function0r, CheckType(), ParamList()->Dict[str, List[Tuple[int, str]]])"),
    (function0a, "TypeData(function0a, CheckType(), ParamList()->Any)"),
    (functionArgs, "TypeData(functionArgs, CheckType(), ParamList(*Any)->None)"),
    (functionKwargs, "TypeData(functionKwargs, CheckType(), ParamList(**Any)->None)"),
    (functionArgsKwargs, "TypeData(functionArgsKwargs, CheckType(), ParamList(*Any,**Any)->None)"),
    (functionPosOnly, "TypeData(functionPosOnly, CheckType(), ParamList(bool,int)->None)"),
    (functionPosOnlyVarPos,
     "TypeData(functionPosOnlyVarPos, CheckType(), ParamList(bool,int,*str)->None)"),
    (functionKeysOnly, "TypeData(functionKeysOnly, CheckType(), ParamList(bool,int)->None)"),
    (functionKeysOnlyKwargs,
     "TypeData(functionKeysOnlyKwargs, CheckType(), ParamList(bool,int,**Any)->None)"),
    (Class.method0, "TypeData(method0, CheckType(), ParamList(self))"),
    (Class.method1, "TypeData(method1, CheckType(), ParamList(self,int)->None)"),
    (Class.method3,
     "TypeData(method3, CheckType(), ParamList(self,int,str,Dict[str, List[int]])->None)"),
    (Class.method0r,
     "TypeData(method0r, CheckType(), ParamList(self)->Dict[int, List[Dict[int, str]]])"),
    (Class.method0a, "TypeData(method0a, CheckType(), ParamList(self)->Any)"),
])
def test_type_data_repr_returns_expected_value(func, expected):
    pl = get_params(func)
    td = TypeData(func.__name__, CheckType(), pl)
    actual = repr(td)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("func, expected, args, kwargs, errors", [
    (function0, False, [], {}, []),
    (function1, False, [1], {}, []),
    (function1, False, [], {"a": 2}, []),
    (function1, True, ["1"], {}, ['positional: a; required type: int; actual value: "1"; index: 0;']),
    (function1, True, [], {}, ["param: a: required type: int; no value provided"]),
    (function1, True, [1], {"e": 12}, ["key: e: extra value: 12"]),
    (function2d, False, [3], {}, []),
    (functionArgs, False, [], {}, []),
    (functionArgs, False, [1], {}, []),
    (functionArgs, False, [1, 2, 3], {}, []),
    (functionKwargs, False, [], {}, []),
    (functionKwargs, False, [], {"a": 1, "b": False}, []),
    (functionPosOnly, False, [True, 5], {}, []),
    (functionPosOnly, True, [True], {}, ["positional: b: required type: int; no value provided; index: 1;"]),
    (functionPosOnly, True, [True, 5, 6], {}, ["extra positional value: 6; index: 2;"]),
    (functionPosOnlyd, False, [], {}, []),
    (functionKeysOnly, False, [], {"a": False, "b": 12}, []),
    (functionKeysOnly, True, [], {"a": False, "b": "12"}, ['key: b; required type: int; actual value: "12"']),
    (functionKeysOnly, True, [], {"a": True}, ["param: b: required type: int; no value provided"]),

])
def test_type_data_values_passed_to_func(func, expected, args, kwargs, errors):
    pl = get_params(func)
    td = TypeData(func.__name__, CheckType(), pl)
    actual = td.check_types(*args, **kwargs)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert td.errors == errors, f"\nexpected: {errors}\nactual  : {td.errors}"


@pytest.mark.parametrize("expected, pl, args", [
    (False, [Param("a", int)], [1]),
    (False, [Param("a", "int")], [1]),
    (False, [Param("a", str)], ["abc"]),
    (False, [Param("a", "str")], ["def"]),
    (True, [Param("a", int)], [1.3]),
    (True, [Param("a", "int")], [1.3]),
])
def test_type_data_check_types_has_str_name_returns_expected_value(expected, pl, args):
    td = TypeData("str_type", CheckType(), ParamList(pl))
    actual = td.check_types(*args)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


class AnyValue(IValueEqual):
    def __eq__(self, other: Any) -> bool:
        return True  # accepts anything


@pytest.mark.parametrize("expected, pl, e_args, e_kwargs, args, kwargs", [
    (False, [Param("a", int)], [5], {}, [5], {}),
    (False, [Param("a", int)], [ValueIgnore], {}, [5], {}),
    (False, [Param("a", int)], [], {"a": ValueIgnore}, [], {"a": 5}),
    (False, [Param("a", int), Param("b", int)], [5, ValueIgnore], {}, [5, "notint"], {}),
    (False, [Param("a", int), Param("b", int)], [ValueIgnore, 6], {}, ["notint", 5], {}),
    (False, [Param("a", int), Param("b", int)], [], {"a": ValueIgnore, "b": 12}, [], {"a": None, "b": 12}),
    (False, [Param("a", int), Param("b", int)], [], {"a": 5, "b": ValueIgnore}, [], {"a": 5, "b": "notint"}),
    (False, [Param("a", int)], [TypeIgnore(7)], {}, [7], {}),
    (False, [Param("a", str)], [TypeIgnore(7)], {}, [7], {}),
    (False, [Param("a", str)], [], {"a": TypeIgnore(7)}, [], {"a": 7}),
    (False, [Param("a", int)], [AnyValue()], {}, ["not an int"], {}),
    (False, [Param("a", int)], [], {"a": AnyValue()}, [], {"a": "not an int"}),
    # incorrect positions and keys do not cause an error

    (False, [Param("a", int)], [], {"z": TypeIgnore(7)}, [1], {}),
    (False, [Param("a", int)], [], {"z": AnyValue()}, [1], {}),
])
def test_type_data_adjust_params_returns_expected_value(expected, pl, e_args, e_kwargs, args, kwargs):
    td = TypeData("adjusted", CheckType(), ParamList(pl))
    td.adjust_params(*e_args, **e_kwargs)
    actual = td.check_types(*args, **kwargs)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_type_data_as_fix_method_returns_expected_string():
    expected = 'fix: Expected("no_fix", a: int)'
    td = TypeData("no_fix", CheckType(), ParamList([Param("a", int)]))
    actual = td.as_fix_method()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_type_data_no_fix_returns_empty_string():
    expected = ""
    td = TypeData("no_fix", CheckType(), ParamList([Param("a", int)])).no_fix()
    actual = td.as_fix_method()
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
