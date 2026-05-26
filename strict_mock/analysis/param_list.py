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
        self._params.append(param)
        if param.name == "self":
            param.checked = True
        self._keys[param.name] = param
        param.index = len(self._params) - 1
        return self

    def add_return_type(self, t: Any) -> "ParamList":
        self.return_type = Param("return_type", t)
        return self

    def as_fix_method(self, name: str) -> str:
        m = f"fix: Expected({self.as_param_str(name)})"
        if self.return_type and self.return_type.type not in (_empty, type(None), None):
            m += f".returns_value({type_name(self.return_type.type)})"
        return m

    def params(self) -> List[Param]:
        if len(self._params) > 0 and self._params[0].name == "self":
            return self._params[1:]
        return self._params

    def param_keys(self) -> Dict[str, Param]:
        return {p.name: p for p in self._params}

    def as_param_str(self, method_name: Optional[str] = None) -> str:
        params = []
        if method_name:
            params.append(f'"{method_name}"')
        params.extend([p.as_param() for p in self._params if p.name != "self"])
        return ", ".join(params)

    def __contains__(self, key: str) -> bool:
        return key in self._keys and not self._keys[key].checked

    def get(self, key: str) -> Param:
        p = self._keys[key]
        p.checked = True
        return p

    def get_next_positional(self) -> Optional[Param]:
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
        return [p for p in self._params if p.checked is False]


def get_params(method) -> ParamList:
    signature = inspect.signature(method)
    return get_params_from_signature(signature)


def get_params_from_signature(signature: inspect.Signature) -> ParamList:
    pl = ParamList()
    for p in signature.parameters.values():
        param = Param(p.name, p.annotation, p.default, p.kind)
        pl.append(param)
    pl.add_return_type(signature.return_annotation)
    return pl
