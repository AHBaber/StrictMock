import inspect
from types import ModuleType
from typing import Any, Callable, Dict, Type, Union

from ..analysis import MockCallableError, TypeData
from ..analysis.param_list import get_params_from_signature


def get_call_dunder(spec_mocked: Dict[str, Any],
                    spec: Union[Type[Any], Callable, ModuleType]) -> Dict[str, Any]:
    """Wire up a ``__call__`` mock when the spec is callable.

    Adds a ``__call__`` entry to ``spec_mocked`` when ``spec`` is a plain function
    or a class whose instances are callable (it defines ``__call__``). Modules and
    non-callable classes are left unchanged.

    Args:
        spec_mocked: The mapping of mocked members being assembled.
        spec: The class, function, or module being mocked.

    Returns:
        The updated ``spec_mocked`` mapping.
    """
    if inspect.isfunction(spec):
        spec_mocked["__call__"] = _call(spec)
        return spec_mocked
    if inspect.isclass(spec) and any("__call__" in cls.__dict__ for cls in spec.__mro__):
        spec_mocked["__call__"] = _call(getattr(spec, "__call__"))
    return spec_mocked


def _call(spec) -> Callable:
    signature = inspect.signature(spec)

    def _call(mock, *args, **kwargs) -> Any:
        pl = get_params_from_signature(signature)
        td = TypeData("__call__", mock._check_type, pl)
        mock._events._set_error_type(MockCallableError)
        return mock._events.add_actual(mock, "__call__", td, *args, **kwargs)

    return _call
