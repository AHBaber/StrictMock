import inspect
from typing import Any, Dict, List, Optional, Tuple

from .param import Param
from .utility import name_with_prefix, type_name

_empty = inspect.Parameter.empty


class ParamList:
    # represents all the parameters in a function
    def __init__(self, params: Optional[List[Param]] = None):
        self._params: List[Param] = []
        self._keys: Dict[str, Param] = {}
        self._index = 0
        self.return_type: Optional[Param] = None
        if params:
            for p in params:
                self.append(p)

    def __repr__(self) -> str:
        sig: List[str] = []
        for p in self._params:
            n = p.name if p.name == "self" else name_with_prefix(type_name(p.type), p.kind)
            sig.append(n)
        rv = ""
        if self.return_type and self.return_type.type != _empty:
            rv = f"->{type_name(self.return_type.type)}"
        return f"ParamList({','.join(sig)}){rv}"

    def append(self, param: Param) -> "ParamList":
        """Append a parameter, indexing it by name and position.

        A parameter named ``self`` is marked as already checked so it is skipped
        during argument matching.

        Returns:
            self, to allow chaining.
        """
        self._params.append(param)
        if param.name == "self":
            param.checked = True
        self._keys[param.name] = param
        param.index = len(self._params) - 1
        return self

    def add_return_type(self, t: Any) -> "ParamList":
        """Record the function's return type for later return-value checking.

        Args:
            t: The return annotation.

        Returns:
            self, to allow chaining.
        """
        self.return_type = Param("return_type", t)
        return self

    def as_fix_method(self, name: str, prefix: Optional[str] = None, postfix: str = "") -> str:
        """Render a suggested ``Expected(...)`` line for this call as fix text.

        Appends a ``.returns_value(...)`` clause when the return type is a real,
        non-None type.

        Args:
            name: The call name to place inside the Expected.
            prefix: The constructor name to use; defaults to ``"Expected"``.
            postfix: Text appended to the end of the suggestion.

        Returns:
            A ``fix: ...`` string suitable for inclusion in an error report.
        """
        if prefix is None:
            prefix = "Expected"
        m = f"fix: {prefix}({self.as_param_str(name)})"
        if self.return_type and self.return_type.type not in (_empty, type(None), None):
            m += f".returns_value({type_name(self.return_type.type)})"
        m += postfix
        return m

    def params(self) -> List[Param]:
        """Return the parameters, excluding a leading ``self`` if present."""
        if len(self._params) > 0 and self._params[0].name == "self":
            return self._params[1:]
        return self._params

    def param_keys(self) -> Dict[str, Param]:
        """Return a mapping of parameter name to Param for all parameters."""
        return {p.name: p for p in self._params}

    def as_param_str(self, method_name: Optional[str] = None) -> str:
        """Render the parameters as a comma-separated argument string.

        Args:
            method_name: If given, it is quoted and placed first, as the call name
                in an ``Expected(...)`` suggestion.

        Returns:
            The joined parameter string, excluding ``self``.
        """
        params = []
        if method_name:
            params.append(f'"{method_name}"')
        params.extend([p.as_param() for p in self._params if p.name != "self"])
        return ", ".join(params)

    def __contains__(self, key: str) -> bool:
        return key in self._keys and not self._keys[key].checked

    def get(self, key: str) -> Param:
        """Return the parameter with the given name and mark it as checked."""
        p = self._keys[key]
        p.checked = True
        return p

    def get_next_positional(self) -> Optional[Param]:
        """Return the next unconsumed positional parameter, advancing the cursor.

        A variadic ``*args`` parameter is returned repeatedly since it can absorb
        any number of positional arguments. Returns None once the positional
        parameters are exhausted or a non-positional parameter is reached.
        """
        # returns each positional in order
        # if there is a variadic, then it will be returned repeatedly
        if self._index >= len(self._params):
            return None
        p = self._params[self._index]
        if not p.is_positional:
            return None
        if p.is_variadic:  # always last positional, but we can keep using it
            p.checked = True
            return p
        self._index += 1
        if p.checked:
            return self.get_next_positional()
        p.checked = True
        return p

    def get_remaining_positional(self) -> Optional[Param]:
        """Return the next positional-only parameter that has not yet been matched.

        Skips parameters already checked, and skips keyword-capable or variadic
        parameters since those may still be satisfied by keyword arguments. Returns
        None when no plain positional parameter remains at the cursor.
        """
        # used to find positional that hasn't been used
        if self._index >= len(self._params):
            return None
        p = self._params[self._index]
        # keyword might be used later
        # variadic may be used zero times
        if p.checked:
            self._index += 1
            return self.get_remaining_positional()
        if p.is_positional and not p.is_keyword and not p.is_variadic:
            p.checked = True
            self._index += 1
            return p
        return None

    def get_kwargs(self) -> Tuple[Dict[str, Param], Optional[Param]]:
        """Return the unmatched keyword parameters and any ``**kwargs`` parameter.

        Returns:
            A tuple of (mapping of name to unchecked keyword Param, the variadic
            keyword Param if the function defines ``**kwargs`` else None).
        """
        kwargs: Dict[str, Param] = {}
        var_key: Optional[Param] = None
        for p in self._params:
            if p.is_keyword:
                if p.is_variadic:
                    var_key = p
                elif not p.checked:
                    kwargs[p.name] = p
        return kwargs, var_key

    def remaining(self) -> List[Param]:
        """Return all parameters that have not yet been matched against an argument."""
        return [p for p in self._params if p.checked is False]


def get_params(method) -> ParamList:
    """Build a ParamList from a callable's signature.

    Args:
        method: Any callable to introspect.

    Returns:
        A ParamList describing the callable's parameters and return type.
    """
    signature = inspect.signature(method)
    return get_params_from_signature(signature)


def get_params_from_signature(signature: inspect.Signature) -> ParamList:
    """Build a ParamList from an already-computed signature.

    Args:
        signature: The inspect.Signature to convert.

    Returns:
        A ParamList describing the signature's parameters and return type.
    """
    pl = ParamList()
    for p in signature.parameters.values():
        param = Param(p.name, p.annotation, p.default, p.kind)
        pl.append(param)
    pl.add_return_type(signature.return_annotation)
    return pl
