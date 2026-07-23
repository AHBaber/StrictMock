import inspect
from types import ModuleType
from typing import Any, Callable, Dict, Type, Union

from ..analysis import MockCreationError

# dunders that StrictMock intentionally does not mock. When present on a spec
# they are wired to raise a MockCreationError if invoked (see unsupported.py),
# and they are excluded from normal member discovery via ``skip`` below.
unsupported = {
    # binary numeric / bitwise
    "__add__",
    "__sub__",
    "__mul__",
    "__matmul__",
    "__truediv__",
    "__floordiv__",
    "__mod__",
    "__divmod__",
    "__pow__",
    "__lshift__",
    "__rshift__",
    "__and__",
    "__xor__",
    "__or__",
    # reflected numeric / bitwise
    "__radd__",
    "__rsub__",
    "__rmul__",
    "__rmatmul__",
    "__rtruediv__",
    "__rfloordiv__",
    "__rmod__",
    "__rdivmod__",
    "__rpow__",
    "__rlshift__",
    "__rrshift__",
    "__rand__",
    "__rxor__",
    "__ror__",
    # in-place numeric / bitwise
    "__iadd__",
    "__isub__",
    "__imul__",
    "__imatmul__",
    "__itruediv__",
    "__ifloordiv__",
    "__imod__",
    "__ipow__",
    "__ilshift__",
    "__irshift__",
    "__iand__",
    "__ixor__",
    "__ior__",
    # unary numeric
    "__neg__",
    "__pos__",
    "__abs__",
    "__invert__",
    "__round__",
    "__trunc__",
    "__floor__",
    "__ceil__",
    # descriptor protocol
    "__get__",
    "__set__",
    "__delete__",
    "__set_name__",
    # container extras
    "__missing__",
    # copy
    "__copy__",
    "__deepcopy__",
    "__setstate__",
    # misc
    "__class_getitem__",
}


def get_unsupported_dunders(spec_mocked: Dict[str, Any],
                            spec: Union[Type[Any], Callable, ModuleType]) -> Dict[str, Any]:
    """Wire up unsupported dunders defined on the spec to raise if invoked.

    For each dunder in the ``unsupported`` set that the spec defines, adds a mock
    entry that raises ``MockCreationError`` when called, making the lack of support
    explicit rather than silently absent.

    Args:
        spec_mocked: The mapping of mocked members being assembled.
        spec: The class, callable, or module being mocked.

    Returns:
        The updated ``spec_mocked`` mapping.
    """
    for name, _ in inspect.getmembers_static(spec):
        if name in unsupported:
            spec_mocked[name] = _unsupported(name)
    return spec_mocked


def _unsupported(name: str) -> Callable:
    def _unsupported(mock, *args, **kwargs) -> Any:
        raise MockCreationError(f"StrictMock does not support {name}")

    return _unsupported


skip = {
    "__class__",
    "__del__",
    "__dict__",
    "__getattr__",
    "__getattribute__",
    "__init__",
    "__init_subclass__",
    "__instancecheck__",
    "__new__",
    "__prepare__",
    "__reduce__",
    "__setattr__",
    "__subclasscheck__",
    "__subclasshook__",
    "__weakref__",
}
skip |= unsupported
