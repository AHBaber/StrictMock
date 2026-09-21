import inspect
from _typeshed import Incomplete
from dataclasses import dataclass
from strict_mock.analysis import CheckType as CheckType, MockMethodError as MockMethodError, TypeData as TypeData
from strict_mock.analysis.param_list import get_params_from_signature as get_params_from_signature
from typing import Any, Callable

_skip: Incomplete

@dataclass
class MockMethod:
    name: str
    signature: inspect.Signature
    is_async: bool = ...
    @classmethod
    def construct(cls, name: str, method: Callable) -> MockMethod: ...

def is_method(spec) -> bool: ...

class Methods:
    _methods: dict[str, MockMethod]
    def __init__(self, spec: Any, e_set: set[str]) -> None: ...
    @classmethod
    def _gather_methods(cls, spec: Any, e_set: set[str]) -> dict[str, MockMethod]: ...
    def add_methods(self, spec_mocked: dict[str, Callable], check_type: CheckType) -> dict[str, Callable]: ...
    @staticmethod
    def _create_mock_method(method: MockMethod, check_type: CheckType) -> Callable: ...
