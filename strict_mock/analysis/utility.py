import inspect
from typing import Any


class _ValueIgnore:
    """Sentinel that causes a positional or keyword argument to be skipped during comparison.

    Use the module-level singleton ``ValueIgnore`` rather than instantiating this
    class directly. When ``ValueIgnore`` appears in an ``Expected`` entry, the
    corresponding argument is accepted regardless of its value or type.

    Example::

        Expected("method", ValueIgnore, key=ValueIgnore)
    """

    def __repr__(self) -> str:
        return "ValueIgnore"

    def __deepcopy__(self, memo: Any) -> "_ValueIgnore":
        # ValueIgnore is a singleton sentinel that is compared by identity
        # (``arg is ValueIgnore``). Returning self keeps that identity intact
        # when an Expected is deep-copied, e.g. inside AsyncGroup.
        return self

    def __copy__(self) -> "_ValueIgnore":
        return self


ValueIgnore = _ValueIgnore()


class TypeIgnore:
    """Wraps a value so that its type is not checked during return-value validation.

    While this is typically used explicitly with ``Expected(...)``, it also used
    internally by ``returns_mock(ignore_type=True)`` to bypass the return-type
    assertion when returning a mock whose type does not exactly match the spec's
    annotation. Using this in tests is a code smell and should be done with care.

    Example::

        Expected("method").returns_mock("my_mock", ignore_type=True)
    """

    def __init__(self, value: Any):
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return self.value == other

    def __repr__(self) -> str:
        return f"TypeIgnore({stringify(self.value)})"


class IValueEqual:
    """Interface for custom argument matchers used inside ``Expected`` entries.

    Subclass ``IValueEqual`` and implement ``__eq__`` to define your own matching
    logic. When an ``IValueEqual`` instance appears as an argument in an
    ``Expected`` entry, its ``__eq__`` is called with the value actually passed to
    the mock, and the type check for that parameter is suppressed.

    Implementations must verify that ``other`` is the expected type themselves,
    since the normal type-checking path is bypassed.

    Example::

        class AnyPositiveInt(IValueEqual):
            def __eq__(self, other: Any) -> bool:
                return isinstance(other, int) and other > 0

        Expected("method", AnyPositiveInt())
    """

    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError("Did not implement ValueEqual.__eq__(...)")

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(...)"


def stringify(value: Any) -> str:
    """Render a value as Python source, wrapping strings in double quotes."""
    if type(value) is str:
        return f'"{value}"'
    return str(value)


def type_name(t: Any) -> str:
    """Render a type (or type string) as readable source text.

    Handles ``None``, string annotations, and parameterized generics such as
    ``Optional[...]``, ``Callable[...]``, and other subscripted types, recursing
    into their type arguments.
    """
    if t is type(None) or t is None:
        return "None"
    if type(t) is str:
        return f'"{t}"'
    if hasattr(t, '__origin__') and t.__origin__ is not None:
        base_type = getattr(t, '_name', None) or t.__origin__.__name__
        if not hasattr(t, '__args__'):
            return base_type
        args = t.__args__

        if base_type == "Optional":
            return f"Optional[{type_name(args[0])}]"

        if base_type == "Callable":
            if len(args) > 1:
                args_ = ", ".join([type_name(a) for a in args[:-1]])
                return_type = type_name(args[-1])
                return f"Callable[[{args_}], {return_type}]"
            elif len(args) == 1:
                return f"Callable[[], {type_name(args[0])}]"

        args_str = ', '.join(type_name(arg) for arg in args)
        return f"{base_type}[{args_str}]"
    else:
        return t.__name__


_prefixes = {
    inspect.Parameter.VAR_POSITIONAL: "*",
    inspect.Parameter.VAR_KEYWORD: "**",
}


def name_with_prefix(name: str, kind: Any) -> str:
    """Prefix a parameter name with ``*`` or ``**`` according to its kind.

    ``self`` is returned unchanged.
    """
    if name == "self":
        return "self"
    p = _prefixes.get(kind, "")
    return f"{p}{name.lstrip('*')}"
