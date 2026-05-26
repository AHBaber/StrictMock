import pytest

from strict_mock.implementations import (MockData, assert_no_leaked_mocks,
                                         clear_mocks, get_unasserted_mocks,
                                         register_mock)
from strict_mock.implementations.registry import deregister_mock


def test_registry_register_and_deregister_mock_returns_no_values():
    # this test may report false fails if another test fails
    # this issue only exists in these tests since we are explicitly calling assert_no_leaked_mocks()
    # which is called implicitly during normal operations
    mock_id = register_mock(MockData("filename", "test_name", "MockName", 9))
    deregister_mock(mock_id)
    assert_no_leaked_mocks()


def test_registry_assert_no_leaked_mocks_returns_expected_values():
    # this test may report false fails if another test fails
    # this issue only exists in these tests since we are explicitly calling assert_no_leaked_mocks()
    # which is called implicitly during normal operations
    _ = register_mock(MockData("filename", "test_name", "MockName1", 15))
    _ = register_mock(MockData("filename", "test_name", "MockName2", 16))

    expected = """Mocks created but assert_all_calls() was never called (count: 2):
    mock: 'MockName1'  test: 'test_name'  file: filename:15
    mock: 'MockName2'  test: 'test_name'  file: filename:16"""

    with pytest.raises(AssertionError) as ex:
        assert_no_leaked_mocks()
    actual = str(ex.value)

    assert actual == expected, f"\nexpected: {expected}\nactual  : {actual}"
    assert get_unasserted_mocks() == [], "registry should be cleared after reporting"


def test_registry_clear_mocks_clears_registry():
    _ = register_mock(MockData("filename", "test_name", "MockName", 30))
    clear_mocks()
    assert get_unasserted_mocks() == []


def test_registry_assert_no_leaked_mocks_clears_registry_after_reporting():
    _ = register_mock(MockData("filename", "test_name", "MockName", 30))

    with pytest.raises(AssertionError):
        assert_no_leaked_mocks()

    # registry is cleared — a second call should not raise
    assert_no_leaked_mocks()
