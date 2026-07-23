from strict_mock import Events, Expected, strict_mock


def test_callable_function_returns_expected_value():
    def function():
        pass

    expected = None
    expected_calls = Events([
        Expected("__call__"),
    ])
    mock = strict_mock(function, "Passes", expected_calls)
    actual = mock()

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_callable_function_returns_value():
    def random_number() -> int:
        raise NotImplementedError

    expected = [83, 25, 42]
    expected_calls = Events([
        Expected("__call__").returns_value(83),
        Expected("__call__").returns_value(25),
        Expected("__call__").returns_value(42),
    ])
    mock = strict_mock(random_number, "RandomNumber", expected_calls)
    actual = [mock(), mock(), mock()]
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_callable_object_returns_expected_value():
    class CallClass:
        def __call__(self, a: int, b: str) -> int:
            raise NotImplementedError

    expected = 83
    expected_calls = Events([
        Expected("__call__", a=12, b="key").returns_value(83),
    ])
    mock = strict_mock(CallClass, "CallClass", expected_calls)
    actual = mock(a=12, b="key")

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()
