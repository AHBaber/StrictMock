from .events import Events as Events
from .registry import deregister_mock as deregister_mock
from .skip import skip as skip
from _typeshed import Incomplete
from strict_mock.analysis import ImportedTypes as ImportedTypes, MockCreationError as MockCreationError, MockMethodError as MockMethodError, TypeData as TypeData, get_params as get_params
from types import ModuleType
from typing import Any, Callable

_MockBase = Any

class BaseMock(_MockBase):
    _spec: Incomplete
    _name: Incomplete
    _events: Incomplete
    _check_type: Incomplete
    _mock_id: int
    def __init__(self, spec: type[Any], name: str, events: Events, imported: ImportedTypes | None = None) -> None: ...
    @property
    def __class__(self) -> Any: ...
    def assert_all_calls(self) -> bool: ...
    def __getattr__(self, name: str) -> Any: ...

def get_spec_dict(spec: type[Any] | Callable | ModuleType) -> dict[str, Any]: ...
