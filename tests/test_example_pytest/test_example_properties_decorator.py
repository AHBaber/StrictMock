from strict_mock import Events, Expected, strict_mock


def test_strict_mock_properties_getter_returns_expected_value():
    # example of a successfully called getter
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
