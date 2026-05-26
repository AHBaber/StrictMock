import inspect
from types import ModuleType
from typing import Any, Callable, Dict, Optional, Type, Union

from strict_mock.analysis import (ImportedTypes, MockCreationError,
                                  MockMethodError, TypeData, get_params)

from .events import Events
from .registry import deregister_mock
from .skip import skip


class BaseMock:
    def __init__(self, spec: Type[Any], name: str, events: Events, imported: Optional[ImportedTypes] = None):
        self._spec = spec
        self._name = name
        self._events = events
        imported_types = imported or ImportedTypes()
        self._check_type = imported_types.check_type
        self._mock_id: int = 0

    @property  # type: ignore
    def __class__(self) -> Any:
        return self._spec

    def assert_all_calls(self) -> bool:
        result = self._events._assert_all_calls(self)
        deregister_mock(self._mock_id)
        return result

    def __getattr__(self, name: str) -> Any:
        methods = inspect.getmembers(self._spec, predicate=inspect.isfunction)
        for n, m in methods:
            if n == name:
                def mock_method(*args, **kwargs):
                    self._events._set_error_type(MockMethodError)
                    td = TypeData(name, self._check_type, get_params(m))
                    return self._events.add_actual(self, name, td, *args, **kwargs)

                return mock_method

        sn = self._spec.__name__
        raise MockCreationError(f"StrictMock: '{self._name}'(spec: {sn}) does not implement '{name}'")


def get_spec_dict(spec: Union[Type[Any], Callable, ModuleType]) -> Dict[str, Any]:
    spec_dict = {
        n: v for n, v in inspect.getmembers_static(spec) if n not in skip
    }
    return spec_dict
