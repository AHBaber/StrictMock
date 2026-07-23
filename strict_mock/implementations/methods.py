import inspect
from dataclasses import dataclass
from types import BuiltinFunctionType, FunctionType, MethodType
from typing import Any, Callable, Dict, Set

from strict_mock.analysis import CheckType, MockMethodError, TypeData
from strict_mock.analysis.param_list import get_params_from_signature

_skip = {"_make_descriptor"}


@dataclass
class MockMethod:
    name: str
    signature: inspect.Signature
    is_async: bool = False

    @classmethod
    def construct(cls, name: str, method: Callable) -> "MockMethod":
        """Build a MockMethod capturing a method's name and signature."""
        return cls(name, inspect.signature(method))


def is_method(spec) -> bool:
    """Return True if ``spec`` is a Python, bound, or builtin function/method."""
    return isinstance(spec, (FunctionType, MethodType, BuiltinFunctionType))


class Methods:
    def __init__(self, spec: Any, e_set: Set[str]) -> None:
        self._methods: Dict[str, MockMethod] = self._gather_methods(spec, e_set)

    @classmethod
    def _gather_methods(cls, spec: Any, e_set: Set[str]) -> Dict[str, MockMethod]:
        return {
            name: MockMethod.construct(name, method) for name, method in
            inspect.getmembers(spec, predicate=is_method)
            if not name.startswith("__") and name in e_set and name not in _skip
        }

    def add_methods(self, spec_mocked: Dict[str, Callable], check_type: CheckType) -> Dict[str, Callable]:
        """Add a mock for each gathered method to ``spec_mocked``.

        Args:
            spec_mocked: The mapping of mocked members being assembled.
            check_type: The type checker used to validate call arguments.

        Returns:
            The updated ``spec_mocked`` mapping.
        """
        for name, mm in self._methods.items():
            spec_mocked[name] = self._create_mock_method(mm, check_type)
        return spec_mocked

    @staticmethod
    def _create_mock_method(method: MockMethod, check_type: CheckType) -> Callable:
        def mock_method(mock, *args, **kwargs):
            # mock is a stand in for self
            mock._events._set_error_type(MockMethodError)
            td = TypeData(method.name, check_type, get_params_from_signature(method.signature))
            return mock._events.add_actual(mock, method.name, td, *args, **kwargs)

        return mock_method
