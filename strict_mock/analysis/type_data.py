import inspect
from typing import Any, List, Optional

from .check_type import CheckType
from .param import Param, ParamDefault, ParamExtra, ParamValue
from .param_list import ParamList
from .utility import IValueEqual, TypeIgnore, ValueIgnore, stringify, type_name

_empty = inspect.Parameter.empty


class TypeData:
    """Validates the argument types and return type of a single mock call.

    Each time a mocked method is invoked, a ``TypeData`` instance is created for
    that call. It holds the expected parameter list derived from the spec's
    signature and runs type checks against the values actually passed in.
    Errors are accumulated in ``self.errors`` and can be inspected via
    ``has_errors`` after calling ``check_types`` or ``check_return_value``.
    """

    def __init__(self, name: str, check_type: CheckType, pl: Optional[ParamList] = None,
                 p: Optional[Param] = None) -> None:
        self.name = name
        if pl is None:
            pl = ParamList()
        if p:
            pl.append(p)
        self._params = pl
        self._check_type = check_type
        self.errors: List[str] = []
        self.results: ParamList = ParamList()
        self._no_fix: bool = False

    def __repr__(self) -> str:
        ct = repr(self._check_type)
        return f"TypeData({self.name}, {ct}, {self._params})"

    @property
    def has_errors(self) -> bool:
        """Return ``True`` if any type or argument errors have been recorded."""
        return len(self.errors) > 0

    def adjust_params(self, *args, **kwargs) -> None:
        """Relax type constraints for arguments that use ``ValueIgnore``, ``TypeIgnore``, or ``IValueEqual``.

        Called before ``check_types`` with the arguments from the matching
        ``Expected`` entry. Any positional or keyword argument that is
        ``ValueIgnore``, a ``TypeIgnore`` wrapper, or an ``IValueEqual`` instance
        has its corresponding parameter type set to ``Any``, so the normal type
        check is skipped for that position.
        """
        params = self._params.params()
        intersect = min(len(params), len(args))
        for i in range(intersect):
            if args[i] is ValueIgnore:
                params[i].type = Any
            elif isinstance(args[i], (TypeIgnore, IValueEqual)):
                params[i].type = Any
        param_keys = self._params.param_keys()
        for k, v in kwargs.items():
            if v is ValueIgnore and k in param_keys:
                param_keys[k].type = Any
            elif isinstance(v, (TypeIgnore, IValueEqual)) and k in param_keys:
                param_keys[k].type = Any

    def no_fix(self) -> "TypeData":
        """Suppress fix-suggestion output when errors are reported.

        Used for inactive properties and other internal call sites where a
        suggested ``Expected(...)`` line would be misleading.

        Returns:
            self, to allow chaining at construction time.
        """
        self._no_fix = True
        return self

    def as_fix_method(self, prefix: str = "Expected", postfix: str = "") -> str:
        """Append and return a suggested ``Expected(...)`` fix string for the current call.

        Returns an empty string and does nothing when ``no_fix()`` has been called.
        Otherwise, the fix string is both appended to ``self.errors`` and returned
        so callers can use it directly.
        """
        if self._no_fix:
            return ""
        fix = self._params.as_fix_method(self.name, prefix, postfix)
        self.errors.append(fix)
        return fix

    def check_types(self, *args, **kwargs) -> bool:
        """Validate the positional and keyword arguments against the parameter list.

        Checks each argument's type, reports extra or missing arguments, and
        falls back to defaults where available. Results are stored in
        ``self.results`` and any error messages are appended to ``self.errors``.

        Returns:
            ``True`` if any type or arity errors were found, ``False`` otherwise.
        """
        has_errors = False
        results: List[Param] = []
        # find positional
        for a in args:  # process all args, if any
            p = self._params.get_next_positional()
            if p:  # param found
                if self._check_type(p.type, a):  # type allows for value
                    results.append(ParamValue(index=p.index, value=a))
                else:  # type does not allow value
                    self.errors.append(
                        f"positional: {p.name}; required type: {type_name(p.type)}; actual value: {stringify(a)}; index: {p.index};")  # noqa: E501
                    results.append(p)
                    has_errors = True
            else:  # more positional values passed in than params listed
                self.errors.append(f"extra positional value: {stringify(a)}; index: {len(results)};")
                results.append(ParamExtra(index=len(results), extra=a))
                has_errors = True
        # report unused positionals
        while p := self._params.get_remaining_positional():
            if p.default is not _empty:
                results.append(ParamDefault(p.name, p.type, p.default, p.kind, index=p.index))
            else:
                self.errors.append(
                    f"positional: {p.name}: required type: {type_name(p.type)}; no value provided; index: {p.index};")
                results.append(p)
                has_errors = True
        # kwargs
        p_kwargs, var_key = self._params.get_kwargs()
        for k, v in kwargs.items():
            p = p_kwargs.get(k, var_key)
            if not p:  # extra value found
                self.errors.append(f"key: {k}: extra value: {stringify(v)}")
                results.append(ParamExtra(k, index=len(results), extra=v))
                has_errors = True
                continue
            p.checked = True
            if self._check_type(p.type, v):
                results.append(ParamValue(p.name, p.type, index=p.index, value=v))
            else:
                self.errors.append(
                    f"key: {p.name}; required type: {type_name(p.type)}; actual value: {stringify(v)}")
                results.append(p)
                has_errors = True
        # find defaults or report errors for unused kwargs
        # **kwargs is ignored since it can have zero values
        for p in p_kwargs.values():
            if p.checked:
                continue
            if p.default is not _empty:
                results.append(ParamDefault(p.name, p.type, p.default, p.kind, index=p.index))
                continue
            results.append(p)
            self.errors.append(f"param: {p.name}: required type: {type_name(p.type)}; no value provided")
            has_errors = True
        self.results = ParamList(results)
        return has_errors

    def check_return_value(self, rv: Any, prefix: Optional[str] = None, postfix: str = "") -> bool:
        """Validate the return value against the spec's return-type annotation.

        ``TypeIgnore`` values bypass this check. If the return type is unspecified
        or is ``None``, no check is performed.

        Args:
            rv: The value that was returned (or is about to be returned) by the mock.
            prefix: Optional text to prepend to the return value.
            postfix: Optional text to append to the return value.

        Returns:
            ``True`` if a type error was found, ``False`` otherwise.
        """
        errors: List[str] = []
        if isinstance(rv, TypeIgnore):
            return False
        if self._params.return_type:
            if not self._check_type(self._params.return_type.type, rv):
                e = type_name(self._params.return_type.type)
                a = f"{type(rv).__name__}({stringify(rv)})"
                errors.append(f"{self.name}: return_type; expected: {e}; actual: {a}")
                errors.append(self._params.as_fix_method(self.name, prefix, postfix))
        self.errors.extend(errors)
        return len(errors) > 0
