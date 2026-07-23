import pytest

from .implementations import (assert_no_leaked_mocks, clear_mocks,
                              set_externally_managed)

# This plugin performs richer per-test leak checking below, so take ownership and
# disable the core's atexit safety net (the fallback for non-pytest runs). pytest
# loads this module at startup, before any mock is created and arms that net.
set_externally_managed()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Pytest hook: stash each phase's report on the test item.

    Records ``rep_setup``/``rep_call``/``rep_teardown`` so the autouse cleanup
    fixture can tell whether the test passed and decide whether to assert that no
    mocks were left unverified.
    """
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
