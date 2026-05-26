import pytest

from strict_mock import Events, Expected, MockPropertyError, strict_mock


def test_strict_mock_properties_getter_none_expected_raises_error():
    # when you first create the mock, if you don't have the expected_calls
    # filled out, then you will get errors
    # the lack of proper expected values will cause the mock to
    # raise an error as soon as the property is called
    # note 1: that the term "getter" is appended to the property name
    # note 2: the type is not currently gathered, thus the type in
    # returns_value() is "Any"
    class NoExpected:
        @property
        def prop(self) -> int:
            raise NotImplementedError

    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop getter")\n'
        '                      fix: Expected("prop getter").returns_value(Any)\n\n'
    )
    expected_calls = Events([])

    mock = strict_mock(NoExpected, "NoExpected", expected_calls)

    with pytest.raises(MockPropertyError) as ex:
        _ = mock.prop
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_getter_returns_expected_value():
    # example os a successfully called getter
    class ClassWithProperty:
        @property
        def prop(self) -> int:
            raise NotImplementedError

    expected = 13
    expected_calls = Events([
        Expected("prop getter").returns_value(13),
    ])

    mock = strict_mock(ClassWithProperty, "ClassWithProperty", expected_calls)
    actual = mock.prop

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_setter_none_expected_raises_error():
    # when you first create the mock, if you don't have the expected_calls
    # filled out, then you will get errors
    # the lack of proper expected values will cause the mock to
    # raise an error as soon as the property is called
    # note 1: that the term "setter" is appended to the property name
    # note 2: the type is not currently gathered, thus the type in
    # the fix line is "Any"
    class NoExpected:
        @property
        def prop(self) -> int:
            raise NotImplementedError

        @prop.setter
        def prop(self, value: int):
            raise NotImplementedError

    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop setter", 12)\n'
        '                      fix: Expected("prop setter", setter: Any)\n\n'
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
        @property
        def prop(self) -> int:
            raise NotImplementedError

        @prop.setter
        def prop(self, value: int):
            raise NotImplementedError

    expected = (
        'StrictMock: SetterIncorrect Discrepancies\n'
        'Data Length\n'
        '    expected: 1\n'
        '    actual  : 1\n'
        'Mismatched     0: Expected("prop setter", 15)\n'
        '                      fix: Expected("prop setter", setter: Any)\n'
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


def test_strict_mock_properties_setter_sets_expected_value():
    # example os a successfully called setter
    class ClassWithProperty:
        @property
        def prop(self) -> int:
            raise NotImplementedError

        @prop.setter
        def prop(self, value: int):
            raise NotImplementedError

    expected_calls = Events([
        Expected("prop setter", 12),
    ])

    mock = strict_mock(ClassWithProperty, "SetterCorrect", expected_calls)
    mock.prop = 12  # type: ignore

    assert mock.assert_all_calls()  # disable for this example


def test_strict_mock_properties_deleter_none_expected_raises_error():
    # when you first create the mock, if you don't have the expected_calls
    # filled out, then you will get errors
    # the lack of proper expected values will cause the mock to
    # raise an error as soon as the property is called
    # note: that the term "deleter" is appended to the property name
    class NoExpected:
        @property
        def prop(self) -> int:
            raise NotImplementedError

        @prop.setter
        def prop(self, value: int):
            raise NotImplementedError

        @prop.deleter
        def prop(self):
            raise NotImplementedError

    expected = (
        'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("prop deleter")\n'
        '                      fix: Expected("prop deleter")\n\n'
    )
    expected_calls = Events([])

    mock = strict_mock(NoExpected, "NoExpected", expected_calls)

    with pytest.raises(MockPropertyError) as ex:
        del mock.prop
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_deleter_prop_is_deleted():
    # example os a successfully called deleter
    class ClassWithProperty:
        @property
        def prop(self) -> int:
            raise NotImplementedError

        @prop.setter
        def prop(self, value: int):
            raise NotImplementedError

        @prop.deleter
        def prop(self):
            raise NotImplementedError

    expected_calls = Events([
        Expected("prop deleter"),
    ])

    mock = strict_mock(ClassWithProperty, "DeleterSuccessful", expected_calls)

    del mock.prop

    assert mock.assert_all_calls()  # disable for this example
