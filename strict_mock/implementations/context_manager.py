from typing import Any, Callable, Dict, Optional

from ..analysis import (MockContextManagerError, MockError, Param, ParamIgnore,
                        ParamList, TypeData)


def cm_enter(mock) -> Any:
    pl = ParamList([Param("self")])
    td = TypeData("__enter__", mock._check_type, pl)
    mock._events._set_error_type(MockContextManagerError)
    return mock._events.add_actual(mock, "__enter__", td)


def cm_exit(mock, exc_type, exc_val, exc_tb) -> Optional[bool]:
    # this check prevents us from recursively adding errors lines
    # in the event we have nested context managers
    if isinstance(exc_val, MockError):
        return False
    val = str(exc_val) if exc_val is not None else None
    pl = ParamList([
        Param("exc_type", Optional[Any]),
        Param("exc_val", Optional[str]),
        ParamIgnore("exc_tb"),
    ])
    pl.add_return_type(Optional[bool])
    td = TypeData("__exit__", mock._check_type, pl)
    mock._events._set_error_type(MockContextManagerError)
    return mock._events.add_actual(mock, "__exit__", td, exc_type, val, exc_tb)


cm_dunders: Dict[str, Callable] = {
    "__enter__": cm_enter,
    "__exit__": cm_exit,
}
