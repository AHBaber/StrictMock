import inspect
from dataclasses import dataclass
from strict_mock.analysis import CheckType as CheckType, MockMethodError as MockMethodError, TypeData as TypeData
from strict_mock.analysis.param_list import get_params_from_signature as get_params_from_signature
from typing import Any, Callable

@dataclass
class MockMethod:
    name: str
    signature: inspect.Signature
    is_async: bool = ...
    @classmethod
    def construct(cls, name: str, method: Callable) -> MockMethod: ...

def is_method(spec) -> bool: ...

class Methods:
    def __init__(self, spec: Any, e_set: set[str]) -> None: ...
    def add_methods(self, spec_mocked: dict[str, Callable], check_type: CheckType) -> dict[str, Callable]: ...
