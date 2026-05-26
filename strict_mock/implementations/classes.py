import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Set, Type

from strict_mock.analysis import CheckType, MockClassError, TypeData
from strict_mock.analysis.param_list import get_params_from_signature


@dataclass
class MockClass:
    name: str
    signature: inspect.Signature

    @classmethod
    def construct(cls, name: str, class_: Type) -> "MockClass":
        init = vars(class_).get("__init__")
        signature = inspect.Signature() if init is None else inspect.signature(init)
        return cls(name, signature)


class Classes:
    def __init__(self, spec: Any, e_set: Set[str]) -> None:
        self._classes: Dict[str, MockClass] = {
            name: MockClass.construct(name, class_) for name, class_ in
            inspect.getmembers(spec, predicate=inspect.isclass) if name in e_set
        }

    def add_classes(self, spec_mocked: Dict[str, Callable], check_type: CheckType) -> Dict[str, Callable]:
        for name, mm in self._classes.items():
            spec_mocked[name] = self._create_mock_class(mm, check_type)
        return spec_mocked

    @staticmethod
    def _create_mock_class(cls: MockClass, check_type: CheckType) -> Callable:
        def mock_class(mock, *args, **kwargs):
            # mock is a stand in for self
            mock._events._set_error_type(MockClassError)
            td = TypeData(cls.name, check_type, get_params_from_signature(cls.signature))
            return mock._events.add_actual(mock, cls.name, td, *args, **kwargs)

        return mock_class
