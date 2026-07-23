from typing import Any, Callable, Dict, Optional, Tuple

from ..analysis import (MockContextManagerError, MockError, Param, ParamIgnore,
                        ParamList, TypeData)


def _enter(mock, ) -> TypeData:
    pl = ParamList([Param("self")])
    td = TypeData("__enter__", mock._check_type, pl)
    mock._events._set_error_type(MockContextManagerError)
    return td


def cm_enter(mock) -> Any:
    """Record a ``__enter__`` call and return its configured value.

    Wired in as the mock's ``__enter__`` when the spec is a context manager.
    """
    td = _enter(mock)
    return mock._events.add_actual(mock, "__enter__", td)


def _exit(mock, exc_type, exc_val, exc_tb) -> Tuple[Optional[str], TypeData]:
    val = str(exc_val) if exc_val is not None else None
    pl = ParamList([
        Param("exc_type", Optional[Any]),
        Param("exc_val", Optional[str]),
        ParamIgnore("exc_tb"),
    ])
    pl.add_return_type(Optional[bool])
    td = TypeData("__exit__", mock._check_type, pl)
    mock._events._set_error_type(MockContextManagerError)
    return val, td


def cm_exit(mock, exc_type, exc_val, exc_tb) -> Optional[bool]:
    """Record a ``__exit__`` call and return whether the exception is suppressed.

    ``exc_val`` is converted to its string form before matching. If the context is
    exiting because of a StrictMock error, the call is not recorded (returning
    False) to avoid cascading error reports in nested context managers.

    Returns:
        The configured return value: True suppresses the exception, False (the
        default) lets it propagate.
    """
    # this check prevents us from recursively adding errors lines
    # in the event we have nested context managers
    if isinstance(exc_val, MockError):
        return False
    val, td = _exit(mock, exc_type, exc_val, exc_tb)
    return mock._events.add_actual(mock, "__exit__", td, exc_type, val, exc_tb)


cm_dunders: Dict[str, Callable] = {
    "__enter__": cm_enter,
    "__exit__": cm_exit,
}
