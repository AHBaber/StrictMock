import pytest

from .implementations import assert_no_leaked_mocks, clear_mocks


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def _strict_mock_cleanup(request):
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep is None or not rep.passed:
        clear_mocks()
    else:
        assert_no_leaked_mocks()
