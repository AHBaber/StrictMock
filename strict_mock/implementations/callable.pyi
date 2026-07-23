from ..analysis import MockCallableError as MockCallableError, TypeData as TypeData
from ..analysis.param_list import get_params_from_signature as get_params_from_signature
from types import ModuleType
from typing import Any, Callable

def get_call_dunder(spec_mocked: dict[str, Any], spec: type[Any] | Callable | ModuleType) -> dict[str, Any]: ...
