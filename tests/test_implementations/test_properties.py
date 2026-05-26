from typing import Any, Dict, List, Type

import pytest

from strict_mock import Events, Expected, MockPropertyError, Prop
from strict_mock.implementations import Properties

from .fake_mock import FakeMock


def test_properties_none_return_none():
    class ClassNoProp:
        pass

    expected: Dict[str, Prop] = {}
    props = Properties(ClassNoProp)
    actual = props.get_properties_with_setters()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_properties_returns_getter():
    class WithGetter:
        pass

        @property
        def prop1(self) -> int:
            raise Exception("ClassWithProperties.prop1 getter should have been overridden by the mock")

    expected = {
        "prop1": Prop("prop1", Any, True),
    }
    props = Properties(WithGetter)
    actual = props.get_properties_with_setters()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_properties_returns_setter():
    class WithSetter:
        pass

        @property
        def prop2(self) -> str:
            raise Exception("ClassWithProperties.prop2 getter should have been overridden by the mock")

        @prop2.setter
        def prop2(self, value: str):
            raise Exception("ClassWithProperties.prop2 setter should have been overridden by the mock")

    expected = {
        "prop2": Prop("prop2", Any, True, True),
    }
    props = Properties(WithSetter)
    actual = props.get_properties_with_setters()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_properties_returns_deleter():
    class WithDeleter:
        pass

        @property
        def prop3(self) -> int:
            raise Exception("ClassWithProperties.prop3 getter should have been overridden by the mock")

        @prop3.setter
        def prop3(self, value: int):
            raise Exception("ClassWithProperties.prop3 setter should have been overridden by the mock")

        @prop3.deleter
        def prop3(self) -> None:
            raise Exception("ClassWithProperties.prop3 deleter should have been overridden by the mock")

    expected = {
        "prop3": Prop("prop3", Any, True, True, True),
    }

    props = Properties(WithDeleter)
    actual = props.get_properties_with_setters()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def _create_mock(name: str, events: Events, props: List[Prop]):
    properties = Properties(FakeMock)
    props_mocked = properties.add_properties({}, props)
    mock_type = type(name, (FakeMock,), props_mocked)
    return mock_type(name, events)


prop_values = [
    (17, 17, int),
    ("a", "a", str),
    ([], [], List[int]),
    ([23], [23], List[int]),
    ([1, 2, 3], [1, 2, 3], List[int]),
    ({"a": "b"}, {"a": "b"}, Dict[str, str]),
]


@pytest.mark.parametrize("expected, input, t", prop_values)
def test_properties_prop_getter_returns_expected_value(expected, input, t):
    prop = Prop("prop", t, True)
    expected_calls = Events([
        Expected("prop getter").returns_value(input),
    ])
    mock = _create_mock("Getter", expected_calls, [prop])

    actual = mock.prop  # type: ignore

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_properties_prop_getter_not_expected_raises_error():
    expected = (
        'StrictMock: Getter Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop getter")\n'
        '                      fix: Expected("prop getter").returns_value(int)\n\n'
    )
    prop = Prop("prop", int, True)
    expected_calls = Events([])
    mock = _create_mock("Getter", expected_calls, [prop])

    with pytest.raises(MockPropertyError) as ex:
        _ = mock.prop  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_properties_prop_getter_wrong_type_raises_error():
    expected = (
        'StrictMock: Getter Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("prop getter").returns_value("abc")\n'
        '                      prop getter: return_type; expected: int; actual: str("abc")\n'
        '                      fix: Expected("prop getter").returns_value(int)\n'
        '               0: Actual("prop getter")\n\n'
    )
    prop = Prop("prop", int, True)
    expected_calls = Events([
        Expected("prop getter").returns_value("abc"),
    ])
    mock = _create_mock("Getter", expected_calls, [prop])

    with pytest.raises(MockPropertyError) as ex:
        _ = mock.prop  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


@pytest.mark.parametrize("expected, input, t", prop_values)
def test_properties_prop_setter(expected, input, t):
    prop = Prop("prop", t, False, True)
    expected_calls = Events([
        Expected("prop setter", expected),
    ])
    mock = _create_mock("Setter", expected_calls, [prop])

    mock.prop = input  # type: ignore

    assert expected_calls._assert_all_calls(mock)


def test_properties_prop_setter_not_expected_raises_error():
    expected = (
        'StrictMock: Setter Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop setter", 12)\n'
        '                      fix: Expected("prop setter", setter: int)\n\n'
    )
    prop = Prop("prop", int, False, True)
    expected_calls = Events([])
    mock = _create_mock("Setter", expected_calls, [prop])

    with pytest.raises(MockPropertyError) as ex:
        mock.prop = 12  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_properties_prop_deleter():
    prop = Prop("prop", int, False, False, True)
    expected_calls = Events([
        Expected("prop deleter"),
    ])
    mock = _create_mock("Deleter", expected_calls, [prop])

    del mock.prop  # type: ignore

    assert expected_calls._assert_all_calls(mock)


def test_properties_prop_deleter_not_expected_raises_error():
    expected = (
        'StrictMock: Deleter Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop deleter")\n'
        '                      fix: Expected("prop deleter")\n\n'
    )
    prop = Prop("prop", int, False, False, True)
    expected_calls = Events([])
    mock = _create_mock("Deleter", expected_calls, [prop])

    with pytest.raises(MockPropertyError) as ex:
        del mock.prop  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_properties_prop_no_getter_after_deleter_raises_error():
    expected = (
        'StrictMock: Del Getter Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 2\n'
        '               0: Expected("prop deleter")\n'
        '               0: Actual("prop deleter")\n'
        'Extra          1: Actual("prop getter inactive")\n\n')

    prop = Prop("prop", int, True, False, True)
    expected_calls = Events([
        Expected("prop deleter"),
    ])
    mock = _create_mock("Del Getter", expected_calls, [prop])

    del mock.prop  # type: ignore
    with pytest.raises(MockPropertyError) as ex:
        _ = mock.prop  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_properties_prop_no_setter_after_deleter_raises_error():
    expected = (
        'StrictMock: Del Setter Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 2\n'
        '               0: Expected("prop deleter")\n'
        '               0: Actual("prop deleter")\n'
        'Extra          1: Actual("prop setter inactive", 12)\n\n')

    prop = Prop("prop", int, False, True, True)
    expected_calls = Events([
        Expected("prop deleter"),
    ])
    mock = _create_mock("Del Setter", expected_calls, [prop])

    del mock.prop  # type: ignore
    with pytest.raises(MockPropertyError) as ex:
        mock.prop = 12  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_properties_prop_no_deleter_after_deleter_raises_error():
    expected = (
        'StrictMock: Del Deleter Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 2\n'
        '               0: Expected("prop deleter")\n'
        '               0: Actual("prop deleter")\n'
        'Extra          1: Actual("prop deleter inactive")\n\n')

    prop = Prop("prop", int, False, False, True)
    expected_calls = Events([
        Expected("prop deleter"),
    ])
    mock = _create_mock("Del Deleter", expected_calls, [prop])

    del mock.prop  # type: ignore
    with pytest.raises(MockPropertyError) as ex:
        del mock.prop  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_properties_prop_inqctive_getter_after_deleter():
    prop = Prop("prop", int, True, False, True)
    expected_calls = Events([
        Expected("prop deleter"),
        Expected("prop getter inactive"),
    ])
    mock = _create_mock("Del Getter", expected_calls, [prop])

    del mock.prop  # type: ignore
    _ = mock.prop  # type: ignore

    assert expected_calls._assert_all_calls(mock)


def _create_mock_from_class(name: str, spec: Type[Any], events: Events):
    properties = Properties(spec)
    props_mocked = properties.add_properties({})
    mock_type = type(name, (FakeMock,), props_mocked)
    return mock_type(name, events)


def test_properties_class_getter_returns_expected_value():
    class GetterClass:
        a: int

    expected = 17
    expected_calls: List[Expected] = [
        Expected("a getter").returns_value(17),
    ]

    events = Events(expected_calls)
    mock = _create_mock_from_class("GetterClass", GetterClass, events)

    actual = mock.a  # type: ignore
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert events._assert_all_calls(mock)


def test_properties_class_setter_returns_expected_value():
    class GetterClass:
        a: int

    expected_calls: List[Expected] = [
        Expected("a setter", 17),
    ]

    events = Events(expected_calls)
    mock = _create_mock_from_class("GetterClass", GetterClass, events)

    mock.a = 17  # type: ignore
    assert events._assert_all_calls(mock)
