from copy import copy

import pytest

from strict_mock import Events, MockCreationError, strict_mock


def test_mock_that_does_nothing():
    # useful if you need to make sure some object does nothing
    # during a test
    class Spec:
        pass

    mock = strict_mock(Spec, "DoesNothing", Events([]))

    assert mock.assert_all_calls()


def test_strict_mock_is_instance():
    class Spec:
        pass

    mock = strict_mock(Spec, "DoesNothing", Events([]))
    assert mock.assert_all_calls()
    assert isinstance(mock, Spec)


def test_no_spec_raises_error():
    expected = "class, function, or module required to define spec"
    with pytest.raises(MockCreationError) as ex:
        _ = strict_mock(None)  # type: ignore
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_instance_spec_raises_error():
    class SomeClass:
        pass

    expected = "class, function, or module required to define spec"
    with pytest.raises(MockCreationError) as ex:
        _ = strict_mock(SomeClass(), "NoSpec", [])  # type: ignore
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"


def test_no_methods_raises_error():
    class NoMethods:
        pass

    expected = "StrictMock: 'StrictMockNoMethods'(spec: NoMethods) does not implement 'method_dne'"
    mock = strict_mock(NoMethods, events=Events())
    with pytest.raises(MockCreationError) as ex:
        mock.method_dne()
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_no_properties_raises_error():
    class NoProperties:
        pass

    expected = "StrictMock: 'NoProperties'(spec: NoProperties) does not implement 'prop_dne'"
    mock = strict_mock(NoProperties, "NoProperties", Events([]))
    with pytest.raises(MockCreationError) as ex:
        mock.prop_dne
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_no_iter_raises_error():
    class NotIter:
        pass

    expected = "'StrictMockNotIter' object is not an iterator"
    mock = strict_mock(NotIter)
    with pytest.raises(TypeError) as ex:
        next(mock)
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_no_iter_for_raises_error():
    class NotIter:
        pass

    expected = "'StrictMockNotIter' object is not iterable"
    mock = strict_mock(NotIter)
    with pytest.raises(TypeError) as ex:
        for m in mock:  # type: ignore
            pass
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_no_cm_raises_error():
    class NotCM:
        pass

    expected = "'StrictMockNotCM' object does not support the context manager protocol"
    mock = strict_mock(NotCM)
    with pytest.raises(TypeError) as ex:
        with mock:
            pass
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()


def test_unsupported_raises_error():
    class Unsupported:
        def __copy__(self):
            raise NotImplementedError()

    expected = "StrictMock does not support __copy__"
    mock = strict_mock(Unsupported)
    with pytest.raises(MockCreationError) as ex:
        _ = copy(mock)
    actual = str(ex.value)
    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert mock.assert_all_calls()
