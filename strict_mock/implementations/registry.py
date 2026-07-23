import atexit
import os
import sys
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class MockData:
    filename: str
    test_name: str
    mock_name: str
    line_number: int


_counter: int = 0
_registry: Dict[int, MockData] = {}
_atexit_armed: bool = False
_externally_managed: bool = False


def register_mock(mock_data: MockData) -> int:
    """Record a newly created mock and return its unique id.

    Used to detect mocks that are never verified with ``assert_all_calls()``.
    Arms the atexit safety net on first use so leaks are caught at process exit
    even when no test framework drives the run.

    Returns:
        A unique id that later identifies this mock in the registry.
    """
    global _counter
    _counter += 1
    mock_id = _counter
    _registry[mock_id] = mock_data
    _arm_atexit_leak_check()
    return mock_id


def deregister_mock(mock_id: int) -> None:
    """Remove a mock from the leak registry, e.g. once it has been asserted."""
    _registry.pop(mock_id, None)


def get_unasserted_mocks() -> List[MockData]:
    """Return the records of all mocks still registered as unasserted."""
    return list(_registry.values())


def clear_mocks() -> None:
    """Empty the leak registry, discarding all tracked mocks."""
    _registry.clear()


def _leak_report() -> str:
    """Render the list of unasserted mocks as a human-readable report."""
    lines = [f"Mocks created but assert_all_calls() was never called (count: {len(_registry)}):"]
    for md in _registry.values():
        lines.append(f"    mock: {md.mock_name!r}  test: {md.test_name!r}  file: {md.filename}:{md.line_number}")
    return "\n".join(lines)


def assert_no_leaked_mocks() -> None:
    """Fail if any created mock was never verified with ``assert_all_calls()``.

    Clears the registry as a side effect.

    Raises:
        AssertionError: If one or more mocks remain unasserted, listing each with
            its test and source location.
    """
    if _registry:
        report = _leak_report()
        _registry.clear()
        raise AssertionError(report)


def set_externally_managed() -> None:
    """Hand leak-checking to an external driver and disable the atexit net.

    Called by the pytest plugin, which performs richer per-test leak checking and
    reports failures cleanly through fixture teardown. Once set, the atexit safety
    net is never armed (and is unregistered if it already was), so the two paths do
    not both fire.
    """
    global _externally_managed
    _externally_managed = True
    _disarm_atexit_leak_check()


def _arm_atexit_leak_check() -> None:
    """Register the process-exit leak check once, unless a driver owns checking."""
    global _atexit_armed
    if _externally_managed or _atexit_armed:
        return
    atexit.register(_atexit_leak_check)
    _atexit_armed = True


def _disarm_atexit_leak_check() -> None:
    global _atexit_armed
    if _atexit_armed:
        atexit.unregister(_atexit_leak_check)
        _atexit_armed = False


def _atexit_leak_check() -> None:  # pragma: no cover
    """Report leaked mocks at interpreter shutdown and force a non-zero exit.

    An exception raised from an atexit handler does not affect the process exit
    code (nor does ``sys.exit``), so on a genuine leak this prints the report and
    calls ``os._exit(1)`` to ensure the failure is visible to the runner/CI. When
    nothing leaked it returns quietly, leaving a successful run's exit code intact.

    Because ``os._exit`` skips any atexit handlers not yet run, this only happens on
    the failure path — a run that is already going to be reported as broken.
    """
    if not _registry:
        return
    sys.stderr.write(_leak_report() + "\n")
    sys.stderr.flush()
    sys.stdout.flush()
    os._exit(1)
