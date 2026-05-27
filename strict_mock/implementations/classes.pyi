import inspect
from dataclasses import dataclass
from strict_mock.analysis import CheckType as CheckType, MockClassError as MockClassError, TypeData as TypeData
from strict_mock.analysis.param_list import get_params_from_signature as get_params_from_signature
from typing import Any, Callable

@dataclass
class MockClass:
    name: str
    signature: inspect.Signature
    @classmethod
    def construct(cls, name: str, class_: type) -> MockClass: ...

class Classes:
    def __init__(self, spec: Any, e_set: set[str]) -> None: ...
    def add_classes(self, spec_mocked: dict[str, Callable], check_type: CheckType) -> dict[str, Callable]: ...
