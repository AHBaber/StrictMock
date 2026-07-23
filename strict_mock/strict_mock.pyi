from strict_mock.analysis import ImportedTypes as ImportedTypes, MockCreationError as MockCreationError
from strict_mock.implementations import BaseMock as BaseMock, Classes as Classes, Events as Events, Methods as Methods, Prop as Prop, Properties as Properties, cm_dunders as cm_dunders, container_dunders as container_dunders, default_dunders as default_dunders, get_call_dunder as get_call_dunder, get_spec_dict as get_spec_dict, get_unsupported_dunders as get_unsupported_dunders, iter_dunders as iter_dunders
from strict_mock.implementations.registry import MockData as MockData, register_mock as register_mock
from types import ModuleType
from typing import Any, Callable

def strict_mock(spec: type[Any] | Callable | ModuleType, name: str | None = None, events: Events | None = None, properties: list[Prop] | None = None, imported: ImportedTypes | None = None) -> BaseMock: ...
