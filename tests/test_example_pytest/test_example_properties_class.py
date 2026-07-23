from strict_mock import Events, Expected, strict_mock

# cannot define deleter with class vars


def test_strict_mock_properties_class_getter_returns_expected_value():
    # example os a successfully called getter
    class ClassWithProperty:
        prop: int

    expected = 13
    expected_calls = Events([
        Expected("prop getter").returns_value(13),
    ])

    mock = strict_mock(ClassWithProperty, "ClassWithProperty", expected_calls)
    actual = mock.prop

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_strict_mock_properties_class_setter_sets_expected_value():
    # example os a successfully called setter
    class ClassWithProperty:
        prop: int

    expected_calls = Events([
        Expected("prop setter", 12),
    ])

    mock = strict_mock(ClassWithProperty, "SetterCorrect", expected_calls)
    mock.prop = 12  # type: ignore

    assert mock.assert_all_calls()  # disable for this example
