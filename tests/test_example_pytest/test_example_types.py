from typing import Any

import pytest

from strict_mock import (Events, Expected, ImportedTypes, IValueEqual,
                         MockCallableError, strict_mock)
from tests.test_analysis import dummy_module_v1, dummy_module_v2


def test_imported_returns_expected():
    it = ImportedTypes(dummy_module_v1.Dummy)
    expected_calls = Events([
        Expected("__call__", dummy_module_v1.Dummy(5)).returns_value(None),
    ])
    mock = strict_mock(dummy_module_v1.new_dummy, events=expected_calls, imported=it)

    _ = mock(dummy_module_v1.Dummy(5))

    assert mock.assert_all_calls()


def test_imported_mismatched_types_raises_error():
    # here we see that v2.Dummy was used as a parameter, but the error message only shows "Dummy" as the types.
    # importing both types into does not help resolve the issue since both classes have the same name
    expected = (
        'StrictMock: StrictMocknew_dummy Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("__call__", Dummy(5)).returns_value(None)\n'
        '                      positional: d; required type: Dummy; actual value: Dummy(5); index: 0;\n'
        '                      fix: Expected("__call__", d: Dummy).returns_value("Dummy | None")\n'
        'Mismatched     0: Actual("__call__", Dummy(5))\n\n'
    )
    it = ImportedTypes(dummy_module_v1.Dummy, dummy_module_v2.Dummy)
    expected_calls = Events([
        Expected("__call__", dummy_module_v1.Dummy(5)).returns_value(None),
    ])
    mock = strict_mock(dummy_module_v1.new_dummy, events=expected_calls, imported=it)

    with pytest.raises(MockCallableError) as ex:
        _ = mock(dummy_module_v2.Dummy(5))
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


class DummyEqual(IValueEqual):
    def __init__(self, v, ):
        self.v = v

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, dummy_module_v1.Dummy):
            return self.v == other.a
        # code smell: why are we having to check for different types from different modules?
        if isinstance(other, dummy_module_v2.Dummy):
            return self.v == other.b
        return False


def test_imported_mismatched_types_value_equal_override_returns_expected():
    # if for some reason, we really do need to allow either type of Dummy to be passed
    # we can use IValueEqual to override standard typing behavior.
    # in this case, it becomes imperative that the IValueEqual implementation checks for types
    # in its __eq_() method to check typing

    # using IValueEqual in this manner should be considered to be a major code smell, and instead steps
    # should be taken to either refactor the tests, or improve the code base that is causing the issue

    it = ImportedTypes(dummy_module_v1.Dummy)
    expected_calls = Events([
        Expected("__call__", DummyEqual(5)).returns_value(None),
    ])
    mock = strict_mock(dummy_module_v1.new_dummy, events=expected_calls, imported=it)

    _ = mock(dummy_module_v2.Dummy(5))

    assert mock.assert_all_calls()
