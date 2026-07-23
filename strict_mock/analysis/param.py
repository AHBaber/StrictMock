import inspect
from dataclasses import dataclass, field
from typing import Any

from .utility import name_with_prefix, stringify, type_name

_empty = inspect.Parameter.empty
_ip = inspect.Parameter


def get_default_kind():
    """Return the default parameter kind (``POSITIONAL_OR_KEYWORD``)."""
    return inspect.Parameter.POSITIONAL_OR_KEYWORD


@dataclass
class Param:
    # represents a single parameter in a function
    name: str = _empty  # type: ignore
    type: Any = _empty  # type of the param, if known
    default: Any = _empty  # default value if there is one
    kind: Any = field(default_factory=get_default_kind)
    checked: bool = False
    index: int = 0

    @property
    def is_positional(self) -> bool:
        """Whether this parameter can be passed positionally (includes ``*args``)."""
        return self.kind in (_ip.POSITIONAL_OR_KEYWORD, _ip.POSITIONAL_ONLY, _ip.VAR_POSITIONAL)

    @property
    def is_keyword(self) -> bool:
        """Whether this parameter can be passed by keyword (includes ``**kwargs``)."""
        return self.kind in (_ip.POSITIONAL_OR_KEYWORD, _ip.KEYWORD_ONLY, _ip.VAR_KEYWORD)

    @property
    def is_variadic(self) -> bool:
        """Whether this parameter is variadic (``*args`` or ``**kwargs``)."""
        return self.kind in (_ip.VAR_POSITIONAL, _ip.VAR_KEYWORD)

    def __repr__(self) -> str:
        # returns a string that may be used as python code
        i = f", {self.index}" if self.index > 0 else ""
        c = f", {self.checked}" if self.checked or i else ""
        k = f", {self.kind}" if self.kind != get_default_kind() or c else ""
        d = ""
        if k or self.default is not _empty:
            if self.default is _empty:
                d = f", {self.default.__name__}"
            else:
                d = f", {stringify(self.default)}"
        t = f", {type_name(self.type)}" if self.type is not _empty else ""
        name = name_with_prefix(self.name, self.kind)
        return f"Param(\"{name}\"{t}{d}{k}{c}{i})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Param):
            return False
        if self.name != other.name:
            return False
        if self.type != other.type:
            return False
        if self.default != other.default:
            return False
        return True

    def as_param(self) -> str:
        """Render this parameter as it would appear in a signature (``name: type = default``)."""
        # returns a string as though it was a parameter in a function
        if self.name == "self":
            return "self"
        d = ""
        if self.default is not _empty:
            d = f" = {stringify(self.default)}"
        return f"{self.name}: {type_name(self.type)}{d}"


@dataclass
class ParamValue(Param):
    value: Any = _empty

    def as_param(self) -> str:
        """Render this parameter as a call argument (``name=value`` or a bare value)."""
        if self.name != _empty:
            return f"{self.name}={stringify(self.value)}"
        return stringify(self.value)


@dataclass
class ParamExtra(Param):
    extra: Any = _empty

    def as_param(self) -> str:
        """Render this parameter as an ``extra`` argument annotated with its runtime type."""
        n = f"{self.name}=" if self.name != _empty else ""
        return f"extra: {n}{type_name(type(self.extra))}({stringify(self.extra)})"


@dataclass
class ParamDefault(Param):
    def as_param(self) -> str:
        """Render this parameter as a signature entry that always shows its default value."""
        return f"{self.name}: {type_name(self.type)} = {stringify(self.default)}"


class ParamIgnore(Param):
    def __init__(self, name: str):
        super().__init__(name, Any)

    def as_param(self) -> str:
        """Render as ``ValueIgnore``, the placeholder for an ignored argument."""
        return "ValueIgnore"

    def __repr__(self):
        return "ValueIgnore"

    def __eq__(self, other):
        if isinstance(other, Param):
            return True
        return False
