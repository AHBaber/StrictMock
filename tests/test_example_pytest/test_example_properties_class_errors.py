import pytest

from strict_mock import Events, Expected, MockPropertyError, strict_mock

# cannot define deleter with class vars


def test_strict_mock_properties_class_getter_none_expected_raises_error():
    # when you first create the mock, if you don't have the expected_calls
    # filled out, then you will get errors
    # the lack of proper expected values will cause the mock to
    # raise an error as soon as the property is called
    # note 1: that the term "getter" is appended to the property name
    # note 2: the type is properly shown in the fix line
    class NoExpected:
        prop: int

    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop getter")\n'
        '                      fix: Expected("prop getter").returns_value(int)\n\n'
    )
    expected_calls = Events([])

    mock = strict_mock(NoExpected, "NoExpected", expected_calls)

    with pytest.raises(MockPropertyError) as ex:
        _ = mock.prop
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_class_getter_incorrect_type_raises_error():
    # error is raised due to the wrong type in returns_value()
    class ClassWithProperty:
        prop: str

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
    mock = strict_mock(ClassWithProperty, "IncorrectReturnType", expected_calls)

    with pytest.raises(MockPropertyError) as ex:
        _ = mock.prop
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_class_setter_none_expected_raises_error():
    # when you first create the mock, if you don't have the expected_calls
    # filled out, then you will get errors
    # the lack of proper expected values will cause the mock to
    # raise an error as soon as the property is called
    # note 1: that the term "setter" is appended to the property name
    # note 2: the type is properly shown in the fix line
    class NoExpected:
        prop: int

    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop setter", 12)\n'
        '                      fix: Expected("prop setter", setter: int)\n\n'
    )
    expected_calls = Events([])

    mock = strict_mock(NoExpected, "NoExpected", expected_calls)

    with pytest.raises(MockPropertyError) as ex:
        mock.prop = 12  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_setter_incorrect_value_raises_error():
    # we have the expected calls filled out, but the value that is set differs
    # than what we expected
    # at this point, we would need to determine which value is wrong:
    # the value in expected or the value in actual
    class ClassWithProperty:
        prop: int

    expected = (
        'StrictMock: SetterIncorrect Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("prop setter", 15)\n'
        '                      fix: Expected("prop setter", setter: int)\n'
        'Mismatched     0: Actual("prop setter", 12)\n\n'
    )
    expected_calls = Events([
        Expected("prop setter", 15),
    ])

    mock = strict_mock(ClassWithProperty, "SetterIncorrect", expected_calls)

    with pytest.raises(MockPropertyError) as ex:
        mock.prop = 12  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_class_setter_incorrect_type_raises_error():
    # error is raised due to the wrong type in returns_value()
    class ClassWithProperty:
        prop: str

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
    expected_calls = Events([
        Expected("prop setter", 12),
    ])
    mock = strict_mock(ClassWithProperty, "IncorrectReturnType", expected_calls)

    with pytest.raises(MockPropertyError) as ex:
        mock.prop = 12  # type: ignore
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()
