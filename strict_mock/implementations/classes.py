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
        """Build a MockClass from a class, capturing its constructor signature.

        The signature is taken from the class itself rather than from its own
        ``__init__``: a class may inherit its ``__init__`` or build instances in
        ``__new__``, and pathlib.Path does both depending on the Python version.
        Note that a class signature carries no ``self`` parameter.

        The return annotation is dropped: instantiation yields an instance, not
        whatever ``__init__`` is annotated to return (usually None).

        Args:
            name: The attribute name the class is exposed under on the module.
            class_: The class whose instantiation is being mocked.

        Returns:
            A MockClass carrying the constructor signature (empty if the class
            takes no arguments or cannot be introspected).
        """
        try:
            signature = inspect.signature(class_)
        except (TypeError, ValueError):
            signature = inspect.Signature()
        return cls(name, signature.replace(return_annotation=inspect.Signature.empty))


class Classes:
    def __init__(self, spec: Any, e_set: Set[str]) -> None:
        self._classes: Dict[str, MockClass] = {
            name: MockClass.construct(name, class_) for name, class_ in
            inspect.getmembers(spec, predicate=inspect.isclass) if name in e_set
        }

    def add_classes(self, spec_mocked: Dict[str, Callable], check_type: CheckType) -> Dict[str, Callable]:
        """Add a mock constructor for each gathered class to ``spec_mocked``.

        Each entry records instantiation of the class (via the mock module) as an
        expected event.

        Args:
            spec_mocked: The mapping of mocked members being assembled.
            check_type: The type checker used to validate constructor arguments.

        Returns:
            The updated ``spec_mocked`` mapping.
        """
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
