import inspect
import re
from typing import (Any, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple,
                    Type, Union, get_args, get_origin)

from .errors import MockTypeError

# Allowlist for type annotation strings passed to eval().
# Permits identifiers, brackets, commas, spaces, and pipes — nothing else.
_SAFE_TYPE_STRING = re.compile(r'^[A-Za-z0-9_\[\], |.]+$')

Empty = inspect.Parameter.empty


# eval() has a bit of fun.  All of the types that are in the file where
# eval() resides are available for it to use.
# which gets real fun when you try to create a class that calls eval()
# in a different file.  Suddenly you lose all the context
# unless you explicitly pass in the types that may be used.

# This is important to be aware of since, some third party libraries
# use return types that are strings and not actual types.
# We want to check those types of course, but then they don't exist
# in this file.  Wonderful.

# ImportedTypes() lets us explicitly specify extra types that need to be evaluated.
# If the types are simple, we don't even need to use eval.  For example:

# some_method(...) -> "SomeClass"

# If this type does not appear in globals(), then a MockTypeError will be
# raised.  It will contain instructions on how to fix the text.

# CheckType will map the string name to the proper type.

# eval() is only needed if there are more complicated types.  For example:

# some_method(...) -> "Optional[SomeClass]"

# Another fun one is that some types are returned as strings containing vertical
# bars that indicate a union.  For example:

# some_method(...) -> "type1 | type2".

# CheckType will convert those to a Union or Optional, and then eval() the
# result to create a proper type.


# Check Type is used implicitly
class CheckType:
    def __init__(self):
        self._imported: Dict[str, Type] = {}
        self.import_type(Any, Dict, Empty, FrozenSet, List,
                         Optional, Sequence, Set, Tuple, Type,
                         Union, bool, bytearray, bytes, complex,
                         float, int, str)

    @staticmethod
    def _qualified_name(t: Any) -> Tuple[Optional[str], Optional[str]]:
        name = getattr(t, '__name__', None) or getattr(t, '_name', None)
        if name:
            module = getattr(t, '__module__', None)
            if module and module != 'builtins':
                return f"{module}.{name}", name
        return name, name

    def import_type(self, *types: Any) -> "CheckType":
        for t in types:
            qual_name, name = self._qualified_name(t)
            if name:
                if qual_name:
                    if qual_name in self._imported:
                        raise MockTypeError(f"Duplicate type imported : {qual_name!r}")
                    self._imported[qual_name] = t
                if qual_name != name:
                    self._imported[name] = t
        return self

    def import_from_globals(self, globals_dict: dict) -> "CheckType":
        for v in globals_dict.values():
            if not isinstance(v, type):
                continue
            qual_name, name = self._qualified_name(v)
            if name and qual_name:
                if qual_name not in self._imported:
                    self._imported[qual_name] = v
                    if qual_name != name and name not in self._imported:
                        self._imported[name] = v
        return self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __call__(self, t: Union[Type, str], v: Any) -> bool:
        try:
            if type(t) is str:
                if not _SAFE_TYPE_STRING.match(t):
                    raise MockTypeError(f"Unsafe type string rejected: {t!r}")
                if t in self._imported:
                    return self._check(self._imported[t], v)
                type_string, types = self._parse_union(t)
                try:
                    t = eval(type_string, self._imported, {})
                except Exception:
                    all_set = set(self._imported.keys())
                    self._find_missing(types, all_set)  # raises error if any missing

            return self._check(t, v)  # type: ignore
        except MockTypeError:
            raise
        except Exception:
            return False

    @staticmethod
    def _find_missing(types: List[str], all_set: Set) -> None:
        missing: List[str] = []
        for t in types:
            if t not in all_set and t != "None":
                missing.append(t)
        if missing:
            m = ', '.join(missing)
            message = (f"Missing types: {m}"
                       f"\nfix: it = ImportedTypes({m})"
                       f"\n     mock=strict_mock(..., imported=it)")
            raise MockTypeError(message)

    @staticmethod
    def _parse_union(type_string: str) -> Tuple[str, List[str]]:
        if "|" in type_string:
            types = [t.strip() for t in type_string.split('|')]
            return "Union[" + ", ".join(types) + "]", types
        return type_string, [type_string]

    def _check(self, t: Type, v: Any) -> bool:
        if t in (Any, Empty):
            return True
        if t in (type(None), None):
            if v is None:
                return True
            return False
        if hasattr(t, '__origin__'):
            origin = f"_{get_origin(t).__name__}"  # type: ignore
            sub = getattr(self, origin, None)
            if sub:
                return sub(t, v)

        return isinstance(v, t)

    @staticmethod
    def _check_arg_count(name: str, required: int, args: Tuple[Any, ...]):
        if len(args) != required:
            raise MockTypeError(f"{name} requires {required} parameters; actual {len(args)}")

    def _dict(self, t: Type, v: Any) -> bool:
        self._check_arg_count("Dict", 2, get_args(t))
        key_type, value_type = get_args(t)
        return all(
            self._check(key_type, key) and self._check(value_type, val)
            for key, val in v.items())

    def _frozenset(self, t: Type, v: Any) -> bool:
        args = get_args(t)
        self._check_arg_count("FrozenSet", 1, args)
        item_type = args[0]
        return all(self._check(item_type, item) for item in v)

    def _list(self, t: Type, v: Any) -> bool:
        args = get_args(t)
        self._check_arg_count("List", 1, args)
        arg = args[0]
        return all(self._check(arg, d) for d in v)

    def _set(self, t: Type, v: Any) -> bool:
        args = get_args(t)
        self._check_arg_count("Set", 1, args)
        return all(self._check(args[0], item) for item in v)

    def _tuple(self, t: Type, v: Any) -> bool:
        args = get_args(t)
        if len(args) == 0:
            return isinstance(v, tuple)
        if len(args) != len(v):
            return False
        return all(self._check(item_type, item) for item_type, item in zip(args, v))

    def _type(self, t: Type, v: Any) -> bool:
        args = get_args(t)
        self._check_arg_count("Type", 1, args)
        return issubclass(v, args[0])

    def _Union(self, t: Type, v: Any) -> bool:
        args = get_args(t)
        return any(self._check(arg, v) for arg in args)


class ImportedTypes:
    """Carries additional types needed for return-type checking when the spec uses
    string annotations or third-party types that are not available in the default
    ``CheckType`` namespace.

    Pass an ``ImportedTypes`` instance to ``strict_mock()`` via the ``imported``
    parameter. The types are registered lazily on first access of ``check_type``.

    Example::

        it = ImportedTypes(MyClass, OtherClass)
        mock = strict_mock(SomeSpec, imported=it)
    """

    def __init__(self, *types: Any):
        self._types = types
        self._check_type: Optional[CheckType] = None

    @property
    def check_type(self) -> CheckType:
        """Return the ``CheckType`` instance loaded with the imported types.

        The instance is created and populated on first access, then cached for
        subsequent calls.
        """
        if self._check_type is None:
            self._check_type = CheckType()
            self._check_type.import_type(*self._types)
        return self._check_type
