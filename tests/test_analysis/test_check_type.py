from typing import (Any, Dict, FrozenSet, List, Optional, Set, Tuple, Type,
                    Union)

import pytest

from strict_mock.analysis import CheckType, Empty, ImportedTypes, MockTypeError

from .func_and_methods import Class, SubClass


def test_check_type_repr_returns_expected_value():
    expected = "CheckType()"
    ct = CheckType()
    actual = repr(ct)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("t, value, expected", [
    (bool, False, True),
    (bool, "NotBool", False),
    (bytearray, bytearray([]), True),
    (bytes, b"", True),
    (complex, complex(2, 1), True),
    (dict, {}, True),
    (dict, {"a": 1}, True),
    (enumerate, enumerate([1, 2]), True),
    (float, 2.3, True),
    (float, "NotFloat", False),
    (frozenset, frozenset([1, 2, 3]), True),
    (int, 1, True),
    (int, "NotInt", False),
    (list, [], True),
    (list, [1, 2, 3], True),
    (list, [1, "a", False], True),
    (list, "NotList", False),
    (object, Class(), True),
    (range, range(5), True),
    (range, "NotRange", False),
    (set, set(), True),
    (set, "NotSet", False),
    (set, {1, 2}, True),
    (set, {1, "a", False}, True),
    (str, "", True),
    (str, "abc", True),
    (str, 123, False),
    (tuple, (), True),
    (tuple, (1, 2, 3), True),
    (tuple, "NotTuple", False),
    (type, type(int), True),
    (type, "NotType", False),

    (type(None), None, True),
    (type(None), 1, False),
    (None, None, True),
    (None, 1, False),

    (Any, 1, True),
    (Any, "a", True),
    (Dict[str, int], {}, True),
    (Dict[str, int], {"a": 1}, True),
    (Dict[str, int], {1: "a"}, False),
    (Dict[str, int], "NotDict", False),
    (Empty, None, True),
    (Empty, 1, True),
    (FrozenSet[int], frozenset([1, 2]), True),
    (List[int], [], True),
    (List[int], [1], True),
    (Optional[int], None, True),
    (Optional[int], 1, True),
    (Optional[int], "NotIntOrNone", False),
    (Optional, "", False),  # Union with no params does not have __origin__
    (Set[int], {}, True),
    (Set[int], {1}, True),
    (Set[int], {"a"}, False),
    (Tuple, (), True),
    (Tuple, (1,), True),
    (Tuple, (1, "a"), True),
    (Tuple[int, str], (1, "a"), True),
    (Tuple, "NotTuple", False),
    (Tuple[int, str], "NotTuple", False),
    (Union, 1, False),  # Union with no params does not have __origin__
    (Union[int, str], 1, True),
    (Union[int, str], "a", True),
    (Union[int, str], Class(), False),
    (Type[Class], Class, True),
    (Type[Class], SubClass, True),
    (Type[int], 1, False),

    (Tuple[Union[int, str], int, str], (1, 2, "a"), True),
    (Tuple[Union[int, str], int, str], ("1", 2, "a"), True),

])
def test_check_type_return_expected(t, value, expected):
    ct = CheckType()
    actual = ct(t, value)
    assert actual == expected, f"\ntype : {t}\nvalue: {value}"


@pytest.mark.parametrize("t, value, error_type, expected", [
    (Dict, {}, MockTypeError, "Dict requires 2 parameters; actual 0"),
    (List, [], MockTypeError, "List requires 1 parameters; actual 0"),
    (FrozenSet, frozenset([1, 2]), MockTypeError, "FrozenSet requires 1 parameters; actual 0"),
    (Set, {}, MockTypeError, "Set requires 1 parameters; actual 0"),
    (Type, Class, MockTypeError, "Type requires 1 parameters; actual 0"),
])
def test_check_type_raises_error(t, value, error_type, expected):
    with pytest.raises(error_type) as ex:
        ct = CheckType()
        ct(t, value)
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("t, value, expected", [
    ("bool", False, True),
    ("bool", "NotBool", False),
    ("bytearray", bytearray([]), True),
    ("bytes", b"", True),
    ("complex", complex(2, 1), True),
    ("dict", {}, True),
    ("dict", {"a": 1}, True),
    ("enumerate", enumerate([1, 2]), True),
    ("float", 2.3, True),
    ("float", "NotFloat", False),
    ("frozenset", frozenset([1, 2, 3]), True),
    ("int", 1, True),
    ("int", "NotInt", False),
    ("list", [], True),
    ("list", [1, 2, 3], True),
    ("list", [1, "a", False], True),
    ("list", "NotList", False),
    ("object", Class(), True),
    ("range", range(5), True),
    ("range", "NotRange", False),
    ("set", set(), True),
    ("set", "NotSet", False),
    ("set", {1, 2}, True),
    ("set", {1, "a", False}, True),
    ("str", "", True),
    ("str", "abc", True),
    ("str", 123, False),
    ("tuple", (), True),
    ("tuple", (1, 2, 3), True),
    ("tuple", "NotTuple", False),
    ("type", type(int), True),
    ("type", "NotType", False),

    ("None", None, True),
    ("None", 1, False),

    ("Any", 1, True),
    ("Any", "a", True),
    ("Dict[str, int]", {}, True),
    ("Dict[str, int]", {"a": 1}, True),
    ("Dict[str, int]", {1: "a"}, False),
    ("Dict[str, int]", "NotDict", False),
    ("FrozenSet[int]", frozenset([1, 2]), True),
    ("List[int]", [], True),
    ("List[int]", [1], True),
    ("Optional[int]", None, True),
    ("Optional[int]", 1, True),
    ("Optional[int]", "NotIntOrNone", False),
    ("Set[int]", {}, True),
    ("Set[int]", {1}, True),
    ("Set[int]", {"a"}, False),
    ("Tuple", (), True),
    ("Tuple", (1,), True),
    ("Tuple", (1, "a"), True),
    ("Tuple[int, str]", (1, "a"), True),
    ("Tuple", "NotTuple", False),
    ("Tuple[int, str]", "NotTuple", False),
    ("Union", 1, False),  # Union with no params does not have __origin__
    ("Union[int, str]", 1, True),
    ("Union[int, str]", "a", True),
    ("Union[int, str]", Class(), False),
    ("Type[int]", 1, False),

    ("Tuple[Union[int, str], int, str]", (1, 2, "a"), True),
    ("Tuple[Union[int, str], int, str]", ("1", 2, "a"), True),
])
def test_check_type_str_return_expected(t, value, expected):
    it = ImportedTypes()
    ct = it.check_type
    actual = ct(t, value)
    assert actual == expected, f"\ntype : {t}\nvalue: {value}"


@pytest.mark.parametrize("t, value, im, expected", [
    ("Class", Class(), Class, True),
    ("Type[Class]", Class, Class, True),
    ("Type[Class]", SubClass, Class, True),
])
def test_check_type_str_imported_return_expected(t, value, im, expected):
    it = ImportedTypes(im)
    ct = it.check_type
    actual = ct(t, value)
    assert actual == expected, f"\ntype : {t}\nvalue: {value}"


@pytest.mark.parametrize("t, value, expected", [
    ("str | int", "abc", True),
    ("str | int", 123, True),
    ("str | int", 12.3, False),
    ("Sequence | None", None, True),
])
def test_check_type_str_concat_returns_expected(t, value, expected):
    it = ImportedTypes()
    ct = it.check_type
    actual = ct(t, value)
    assert actual == expected, f"\ntype : {t}\nvalue: {value}"


def test_check_type_unknown_type_raises_error():
    expected = ("Missing types: UnknownType\n"
                "fix: it = ImportedTypes(UnknownType)\n"
                "     mock=strict_mock(..., imported=it)")
    it = ImportedTypes()
    ct = it.check_type
    with pytest.raises(MockTypeError) as ex:
        ct("UnknownType", 1)
    actual = str(ex.value)
    assert expected == actual, f"\nexpected: {expected}\nactual  : {actual}"


def test_check_type_duplicate_type_raises_error():
    expected = "Duplicate type imported : 'str'"
    with pytest.raises(MockTypeError) as ex:
        it = ImportedTypes(str)
        _ = it.check_type
    actual = str(ex.value)
    assert expected == actual, f"\nexpected: {expected}\nactual  : {actual}"


def test_check_type_unsafe_type_string_raises_error():
    expected = "Unsafe type string rejected: 'int()'"
    ct = CheckType()
    with pytest.raises(MockTypeError) as ex:
        ct("int()", 1)
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


class RaisingMeta(type):
    def __instancecheck__(cls, instance):
        raise RuntimeError("instancecheck exploded")


class RaisingType(metaclass=RaisingMeta):
    pass


def test_check_type_exception_in_check_returns_false():
    expected = False
    ct = CheckType()
    actual = ct(RaisingType, 42)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_check_type_import_type_no_name_does_not_modify_imported():
    nameless = object()
    ct = CheckType()
    keys_before = set(ct._imported.keys())
    ct.import_type(nameless)
    keys_after = set(ct._imported.keys())
    assert keys_before == keys_after
