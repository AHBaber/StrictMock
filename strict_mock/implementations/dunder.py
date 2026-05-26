from typing import Any, Type

from ..analysis import Param, ParamIgnore, ParamList, TypeData


def _event_compare(name: str):
    def _event_compare(mock, other: Any) -> bool:
        pl = ParamList([Param("self"), ParamIgnore("other")])
        pl.add_return_type(bool)
        td = TypeData(name, mock._check_type, pl)
        return mock._events.add_actual(mock, name, td, other)

    return _event_compare


def _event_no_arg(name: str, r_type: Type):
    def _event_no_arg(mock) -> Any:
        pl = ParamList([Param("self")])
        pl.add_return_type(r_type)
        td = TypeData(name, mock._check_type, pl)
        return mock._events.add_actual(mock, name, td)

    return _event_no_arg


def _event_repr(name: str):
    def _event_repr(mock) -> Any:
        return mock._name

    return _event_repr


def _format(mock, format_spec: str) -> str:
    return mock._name


default_dunders = {
    # defined on object
    "__eq__": _event_compare("__eq__"),
    "__ne__": _event_compare("__ne__"),
    "__lt__": _event_compare("__lt__"),
    "__le__": _event_compare("__le__"),
    "__gt__": _event_compare("__gt__"),
    "__ge__": _event_compare("__ge__"),
    "__hash__": _event_no_arg("__hash__", int),
    "__repr__": _event_repr("__repr__"),
    "__str__": _event_repr("__str__"),
    "__sizeof__": _event_no_arg("__sizeof__", int),
    "__format__": _format,
    # type conversion
    "__bool__": _event_no_arg("__bool__", bool),
    "__bytes__": _event_no_arg("__bytes__", bytes),
    "__complex__": _event_no_arg("__complex__", complex),
    "__float__": _event_no_arg("__float__", float),
    "__index__": _event_no_arg("__index__", int),
    "__int__": _event_no_arg("__int__", int),
}
