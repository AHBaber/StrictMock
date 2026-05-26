import inspect
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

from ..analysis import MockCallableError, TypeData
from ..analysis.param_list import get_params_from_signature

# this was made since the formatter keep moving part of the type
# to a new line, and then flake8 would complain about the indention
_GCDReturnType = Tuple[Dict[str, Any], Optional[Type[Any]]]


def get_call_dunder(spec_mocked: Dict[str, Any], spec: Union[Type[Any], Callable]) -> _GCDReturnType:
    if inspect.isfunction(spec):
        spec_mocked["__call__"] = _call(spec)
        return spec_mocked, None  # not returned to indicate that it is not a class
    if inspect.isclass(spec) and issubclass(spec, Callable):  # type: ignore
        spec_mocked["__call__"] = _call(getattr(spec, "__call__"))
    return spec_mocked, spec  # type: ignore


def _call(spec) -> Callable:
    signature = inspect.signature(spec)

    def _call(mock, *args, **kwargs) -> Any:
        pl = get_params_from_signature(signature)
        td = TypeData("__call__", mock._check_type, pl)
        mock._events._set_error_type(MockCallableError)
        return mock._events.add_actual(mock, "__call__", td, *args, **kwargs)

    return _call
