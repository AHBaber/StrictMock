from typing import List

from strict_mock import Events, Expected, Prop, strict_mock


class NoProps:
    pass


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
