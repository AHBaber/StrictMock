from copy import copy, deepcopy
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

import pytest

from strict_mock.analysis.utility import (TypeIgnore, ValueIgnore, stringify,
                                          type_name)


def test_value_ignore_copy_returns_self():
    actual = copy(ValueIgnore)
    assert actual is ValueIgnore


def test_value_ignore_deepcopy_returns_self():
    actual = deepcopy(ValueIgnore)
    assert actual is ValueIgnore


@pytest.mark.parametrize("input, expected", [
    (42, "42"),
    ("abc", '"abc"'),
    (ValueIgnore, "ValueIgnore"),
    (TypeIgnore(5), "TypeIgnore(5)"),
    (TypeIgnore("abc"), 'TypeIgnore("abc")'),
    (None, "None"),
])
def test_stringify(input, expected):
    actual = stringify(input)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("input, expected", [
    (type(None), "None"),
    (None, "None"),
    (bool, "bool"),
    (bytes, "bytes"),
    (float, "float"),
    (int, "int"),
    (str, "str"),
    (Callable, "Callable"),
    (Callable[[], None], "Callable[[], None]"),
    (Callable[[], int], "Callable[[], int]"),
    (Callable[[int], int], "Callable[[int], int]"),
    (Callable[[int, str], int], "Callable[[int, str], int]"),
    (Dict[str, int], "Dict[str, int]"),
    (Iterable, "Iterable"),
    (Iterable[int], "Iterable[int]"),
    (List[int], "List[int]"),
    (Optional[bool], "Optional[bool]"),
    (Tuple[int, Dict[str, int]], "Tuple[int, Dict[str, int]]"),
    (Union[int, str, List[int]], "Union[int, str, List[int]]"),
    (Union[None, int], "Optional[int]"),
    (Union[int, None], "Optional[int]"),
    ("str", '"str"'),
])
def test_type_name(input, expected):
    actual = type_name(input)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
