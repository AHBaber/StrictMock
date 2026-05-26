from typing import Any, Callable, Dict

from ..analysis import MockContainerError, Param, ParamList, TypeData


def _non_keyed(name: str, r_type: Any) -> Callable:
    def _non_keyed(mock) -> Any:
        pl = ParamList([Param("self")])
        pl.add_return_type(r_type)
        td = TypeData(name, mock._check_type, pl)
        mock._events._set_error_type(MockContainerError)
        return mock._events.add_actual(mock, name, td)

    return _non_keyed


def _keyed(name: str, r_type: Any) -> Callable:
    def _keyed(mock, key: Any) -> Any:
        pl = ParamList([Param("self"), Param("key", Any)])
        pl.add_return_type(r_type)
        td = TypeData(name, mock._check_type, pl)
        mock._events._set_error_type(MockContainerError)
        return mock._events.add_actual(mock, name, td, key)

    return _keyed


def _del(mock, key: Any) -> None:
    pl = ParamList([Param("self"), Param("key", Any)])
    td = TypeData("__delitem__", mock._check_type, pl)
    mock._events._set_error_type(MockContainerError)
    mock._events.add_actual(mock, "__delitem__", td, key)


def _set(mock, key: Any, value: Any) -> None:
    pl = ParamList([Param("self"), Param("key", Any), Param("value", Any)])
    td = TypeData("__setitem__", mock._check_type, pl)
    mock._events._set_error_type(MockContainerError)
    mock._events.add_actual(mock, "__setitem__", td, key, value)


container_dunders: Dict[str, Callable] = {
    "__contains__": _keyed("__contains__", bool),
    "__delitem__": _del,
    "__getitem__": _keyed("__getitem__", Any),
    "__len__": _non_keyed("__len__", int),
    "__length_hint__": _non_keyed("__length_hint__", int),
    # "__missing__"
    "__reversed__": _non_keyed("__reversed__", Any),
    "__setitem__": _set,
}
