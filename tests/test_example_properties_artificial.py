from typing import List

import pytest

from strict_mock import Events, Expected, MockPropertyError, Prop, strict_mock


class NoProps:
    pass


def test_strict_mock_properties_artificial_getter_none_expected_raises_error():
    # when you first create the mock, if you don't have the expected_calls
    # filled out, then you will get errors
    # the lack of proper expected values will cause the mock to
    # raise an error as soon as the property is called
    # note 1: that the term "getter" is appended to the property name
    # note 2: the type is properly shown in the fix line
    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop getter")\n'
        '                      fix: Expected("prop getter").returns_value(str)\n\n'
    )
    expected_calls = Events([])
    props: List[Prop] = [
        Prop("prop", str, True),
    ]
    mock = strict_mock(NoProps, "NoExpected", expected_calls, properties=props)

    with pytest.raises(MockPropertyError) as ex:
        _ = mock.prop
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_artificial_getter_returns_expected_value():
    # example os a successfully called getter
    expected = "abc"
    expected_calls = Events([
        Expected("prop getter").returns_value("abc"),
    ])
    props: List[Prop] = [
        Prop("prop", str, True),
    ]

    mock = strict_mock(NoProps, "ArtificialProperty", expected_calls, properties=props)
    actual = mock.prop

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_artificial_getter_incorrect_type_raises_error():
    # error is raised due to the wrong type in returns_value()
    expected = (
        'StrictMock: IncorrectReturnType Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("prop getter").returns_value(15)\n'
        '                      prop getter: return_type; expected: str; actual: int(15)\n'
        '                      fix: Expected("prop getter").returns_value(str)\n'
        '               0: Actual("prop getter")\n\n'
    )
    expected_calls = Events([
        Expected("prop getter").returns_value(15),
    ])
    props: List[Prop] = [
        Prop("prop", str, True),
    ]
    mock = strict_mock(NoProps, "IncorrectReturnType", expected_calls, properties=props)

    with pytest.raises(MockPropertyError) as ex:
        _ = mock.prop
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_artificial_setter_none_expected_raises_error():
    # when you first create the mock, if you don't have the expected_calls
    # filled out, then you will get errors
    # the lack of proper expected values will cause the mock to
    # raise an error as soon as the property is called
    # note 1: that the term "setter" is appended to the property name
    # note 2: the type is properly shown in the fix line
    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop setter", "abc")\n'
        '                      fix: Expected("prop setter", setter: str)\n\n'
    )
    expected_calls = Events([])
    props: List[Prop] = [
        Prop("prop", str, False, True),
    ]

    mock = strict_mock(NoProps, "NoExpected", expected_calls, properties=props)

    with pytest.raises(MockPropertyError) as ex:
        mock.prop = "abc"  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_artificial_setter_sets_expected_value():
    # example os a successfully called setter
    expected_calls = Events([
        Expected("prop setter", "abc"),
    ])
    props: List[Prop] = [
        Prop("prop", str, False, True),
    ]

    mock = strict_mock(NoProps, "SetterCorrect", expected_calls, properties=props)
    mock.prop = "abc"  # type: ignore

    assert mock.assert_all_calls()  # disable for this example


def test_strict_mock_properties_artificial_setter_incorrect_value_raises_error():
    # we have the expected calls filled out, but the value that is set differs
    # than what we expected
    # at this point, we would need to determine which value is wrong:
    # the value in expected or the value in actual
    expected = (
        'StrictMock: SetterIncorrect Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("prop setter", "abc")\n'
        '                      fix: Expected("prop setter", setter: str)\n'
        'Mismatched     0: Actual("prop setter", "def")\n\n'
    )
    expected_calls = Events([
        Expected("prop setter", "abc"),
    ])
    props: List[Prop] = [
        Prop("prop", str, False, True),
    ]

    mock = strict_mock(NoProps, "SetterIncorrect", expected_calls, properties=props)

    with pytest.raises(MockPropertyError) as ex:
        mock.prop = "def"  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_artificial_setter_incorrect_type_raises_error():
    # error is raised due to the wrong type in returns_value()
    expected = (
        'StrictMock: IncorrectReturnType Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        '               0: Expected("prop setter", 12)\n'
        '                      positional: setter; required type: str; actual value: 12; index: 0;\n'
        '                      fix: Expected("prop setter", setter: str)\n'
        '               0: Actual("prop setter", 12)\n\n'
    )
    expected_calls = Events([Expected("prop setter", 12)])
    props: List[Prop] = [
        Prop("prop", str, False, True),
    ]
    mock = strict_mock(NoProps, "IncorrectReturnType", expected_calls, properties=props)

    with pytest.raises(MockPropertyError) as ex:
        mock.prop = 12  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_artificial_deleter_none_expected_raises_error():
    # when you first create the mock, if you don't have the expected_calls
    # filled out, then you will get errors
    # the lack of proper expected values will cause the mock to
    # raise an error as soon as the property is called
    # note: that the term "deleter" is appended to the property name
    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop deleter")\n'
        '                      fix: Expected("prop deleter")\n\n'
    )
    expected_calls = Events([])
    props: List[Prop] = [
        Prop("prop", str, False, False, True),
    ]

    mock = strict_mock(NoProps, "NoExpected", expected_calls, properties=props)

    with pytest.raises(MockPropertyError) as ex:
        del mock.prop
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_artificial_deleter_prop_is_deleted():
    # example os a successfully called deleter
    expected_calls = Events([
        Expected("prop deleter"),
    ])
    props: List[Prop] = [
        Prop("prop", str, False, False, True),
    ]

    mock = strict_mock(NoProps, "DeleterSuccessful", expected_calls, properties=props)

    del mock.prop

    assert mock.assert_all_calls()
