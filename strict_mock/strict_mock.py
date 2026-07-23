import inspect
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from strict_mock.analysis import ImportedTypes, MockCreationError
from strict_mock.implementations import (BaseMock, Classes, Events, Methods,
                                         Prop, Properties, cm_dunders,
                                         container_dunders, default_dunders,
                                         get_call_dunder, get_spec_dict,
                                         get_unsupported_dunders, iter_dunders)
from strict_mock.implementations.registry import MockData, register_mock


def _is_supported(spec) -> bool:
    return inspect.isclass(spec) or inspect.isfunction(spec) or inspect.ismodule(spec)


def _get_caller_info() -> Tuple[str, str, int]:
    stack = inspect.stack()
    # Frame 0: _get_caller_info, Frame 1: strict_mock(), Frame 2: caller of strict_mock()
    filename = ""
    function_name = ""
    line_number = 0
    if len(stack) > 2:
        filename = stack[2].filename
        function_name = stack[2].function
        line_number = stack[2].lineno
    for frame in stack[2:]:
        if frame.function.startswith("test_"):
            function_name = frame.function
            break
    return filename, function_name, line_number


def _get_caller_globals() -> dict:
    stack = inspect.stack()
    merged: dict = {}
    for frame_info in stack[1:]:
        if frame_info.frame.f_globals.get("__name__") != __name__:
            merged.update(frame_info.frame.f_globals)
    return merged


def _get_e_set(events: Events) -> Set[str]:
    e_set: Set[str] = set()
    for e in events:
        e_set.add(e.name)
    return e_set


def strict_mock(spec: Union[Type[Any], Callable, ModuleType],
                name: Optional[str] = None,
                events: Optional[Events] = None,
                properties: Optional[List[Prop]] = None,
                imported: Optional[ImportedTypes] = None) -> BaseMock:
    """Create a strict mock object based on the given spec.

    Args:
        spec: The class, function, or module to mock. Defines the interface the
            mock will enforce.
        name: Optional name for the mock. Defaults to ``StrictMock<spec.__name__>``.
        events: The ordered sequence of expected calls. If omitted, an empty
            ``Events`` list is used.
        properties: Optional list of ``Prop`` descriptors that override or extend
            the properties discovered on the spec.
        imported: Additional types needed for return-type checking when the spec
            uses string annotations or third-party types. If omitted, only the
            built-in types are available.

    Returns:
        A mock instance whose type is dynamically created from the spec.

    Raises:
        MockCreationError: If spec is not a class, function, or module.
    """
    if not _is_supported(spec):
        raise MockCreationError("class, function, or module required to define spec")
    name = name or f"StrictMock{spec.__name__}"
    events = events or Events()
    spec_mocked: Dict[str, Callable] = {}
    spec_dict = get_spec_dict(spec)
    spec_mocked = get_call_dunder(spec_mocked, spec)
    if imported is None:
        imported = ImportedTypes()
        imported.check_type.import_from_globals(_get_caller_globals())
    e_set = _get_e_set(events)

    if inspect.isclass(spec) or inspect.ismodule(spec):  # class
        for dunders in [default_dunders, cm_dunders, container_dunders, iter_dunders]:
            for d in dunders.keys():
                if d in spec_dict:
                    spec_mocked[d] = dunders[d]
        spec_mocked = get_unsupported_dunders(spec_mocked, spec)
        properties_builder = Properties(spec)
        spec_mocked = properties_builder.add_properties(spec_mocked, properties)
        m = Methods(spec, e_set)
        spec_mocked = m.add_methods(spec_mocked, imported.check_type)

        if inspect.ismodule(spec):
            c = Classes(spec, e_set)
            spec_mocked = c.add_classes(spec_mocked, imported.check_type)

    # function
    mock_type = type(name, (BaseMock,), spec_mocked)
    mock = mock_type(spec, name, events, imported)
    events._add_mock(name, mock)
    filename, test_name, line_number = _get_caller_info()
    mock._mock_id = register_mock(MockData(filename, test_name, name, line_number))
    return mock
