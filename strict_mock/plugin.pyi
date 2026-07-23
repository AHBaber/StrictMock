from .implementations import assert_no_leaked_mocks as assert_no_leaked_mocks, clear_mocks as clear_mocks, set_externally_managed as set_externally_managed
from _typeshed import Incomplete
from collections.abc import Generator

def pytest_runtest_makereport(item, call) -> Generator[None, Incomplete]: ...
