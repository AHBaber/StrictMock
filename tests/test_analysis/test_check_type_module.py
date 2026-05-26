import dummy_module_v1  # type: ignore
import dummy_module_v2  # type: ignore
import pytest
from dummy_module_v1 import Dummy as Dummy1
from dummy_module_v2 import Dummy as Dummy2

from strict_mock.analysis import ImportedTypes


@pytest.mark.parametrize("t, value, expected", [
    (Dummy1, Dummy1(1), True),
    (dummy_module_v1.Dummy, Dummy1(1), True),
    (Dummy2, Dummy2(5), True),
    (dummy_module_v2.Dummy, Dummy2(1), True),
])
def test_check_type_aliased_types_returns_expected(t, value, expected):
    it = ImportedTypes()
    ct = it.check_type
    actual = ct(t, value)
    assert actual == expected, f"\ntype : {t}\nvalue: {value}"


@pytest.mark.parametrize("t, value, expected", [
    ("Dummy | None", None, True),
    ("dummy_module_v1.Dummy", dummy_module_v1.Dummy(1), True),
    ("dummy_module_v1.Dummy | None", "nope", False),
    ("Dummy | None", Dummy2(3), True),
    ("Dummy", Dummy2(4), True),
    ("dummy_module_v2.Dummy", Dummy2(4), True),
])
def test_check_type_str_concat_eval_using_module_returns_expected(t, value, expected):
    it = ImportedTypes(dummy_module_v1.Dummy, dummy_module_v2.Dummy)
    ct = it.check_type
    actual = ct(t, value)
    assert actual == expected, f"\ntype : {t}\nvalue: {value}"


@pytest.mark.parametrize("t, value, expected", [
    ("Dummy | None", Dummy1(5), False),  # this fails due to the fact that Dummy2 overwrites the entry for Dummy1
    ("Dummy | None", Dummy2(5), True),
])
def test_check_type_str_eval_fails_using_module_returns_expected(t, value, expected):
    it = ImportedTypes(Dummy1, Dummy2)
    ct = it.check_type
    actual = ct(t, value)
    assert actual == expected, f"\ntype : {t}\nvalue: {value}"
