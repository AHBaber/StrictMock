import inspect
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Type, Union

from strict_mock.analysis import MockPropertyError, Param, ParamList, TypeData

_dsc = Dict[str, Callable]


@dataclass
class Prop:
    """Descriptor for a single property to be mocked on a spec.

    Pass a list of ``Prop`` instances to ``strict_mock()`` via the ``properties``
    parameter to override or extend the properties discovered automatically from
    the spec. Each flag controls which accessor will be wired up on the mock.

    Attributes:
        name: The attribute name as it appears on the spec.
        type: The expected type of the property value, used for type checking on
            get and set.
        getter: If ``True``, a getter is created that records the access as an
            expected call.
        setter: If ``True``, a setter is created that records the assignment as an
            expected call.
        deleter: If ``True``, a deleter is created that records the deletion as an
            expected call. The property becomes inactive after the deleter fires.
        is_active: If ``False``, all accessors are treated as inactive and their
            calls are not matched against expected entries.
    """

    name: str
    type: Type[Any]
    getter: bool = False
    setter: bool = False
    deleter: bool = False
    is_active: bool = True


class Properties:
    def __init__(self, spec: Union[Type[Any], Callable, ModuleType]):
        self._spec = spec
        self._properties: Dict[str, Prop] = {}

    def get_properties_with_setters(self) -> Dict[str, Prop]:
        properties_info = {}
        for name, obj in inspect.getmembers(self._spec, predicate=inspect.isdatadescriptor):
            if isinstance(obj, property):
                type_hint = getattr(self._spec, '__annotations__', {}).get(name, Any)
                properties_info[name] = Prop(
                    name,
                    type_hint,
                    obj.fget is not None,
                    obj.fset is not None,
                    obj.fdel is not None,
                )
        for name, prop_type in getattr(self._spec, '__annotations__', {}).items():
            properties_info[name] = Prop(
                name,
                prop_type,
                True,
                True,
            )
        self._properties = properties_info
        return properties_info

    def add_properties(self, spec_mocked: _dsc, props: Optional[List[Prop]] = None) -> _dsc:
        self.get_properties_with_setters()
        if props:
            for prop in props:
                self._properties[prop.name] = prop
        for name, prop in self._properties.items():
            spec_mocked[name] = self.create_prop(prop)
        return spec_mocked

    def create_prop(self, prop: Prop):
        g = self._create_getter(prop)
        s = self._create_setter(prop)
        d = self._create_deleter(prop)
        mock_property = property(g, s, d)
        return mock_property

    def _create_getter(self, prop: Prop) -> Optional[Callable]:
        if prop.getter and prop.is_active:
            def getter(mock):
                prop_name = f"{prop.name} getter"
                mock._events._set_error_type(MockPropertyError)
                if prop.is_active:
                    pl = ParamList().add_return_type(prop.type)
                    td = TypeData(prop_name, mock._check_type, pl)
                    return mock._events.add_actual(mock, prop_name, td)
                prop_name = f"{prop_name} inactive"
                td = TypeData(prop_name, mock._check_type).no_fix()
                return mock._events.add_actual(mock, prop_name, td)

            return getter
        return None

    def _create_setter(self, prop: Prop) -> Optional[Callable]:
        if prop.setter and prop.is_active:
            def setter(mock, value):
                prop_name = f"{prop.name} setter"
                mock._events._set_error_type(MockPropertyError)
                if prop.is_active:
                    pl = ParamList([Param("setter", prop.type)]).add_return_type(type(None))
                    td = TypeData(prop_name, mock._check_type, pl)
                    mock._events.add_actual(mock, prop_name, td, value)
                    return
                prop_name = f"{prop.name} setter inactive"
                td = TypeData(prop_name, mock._check_type).no_fix()
                return mock._events.add_actual(mock, prop_name, td, value)

            return setter
        return None

    def _create_deleter(self, prop: Prop) -> Optional[Callable]:
        if prop.deleter and prop.is_active:
            def deleter(mock):
                prop_name = f"{prop.name} deleter"
                mock._events._set_error_type(MockPropertyError)
                if prop.is_active:
                    pl = ParamList([]).add_return_type(type(None))
                    td = TypeData(prop_name, mock._check_type, pl)
                    mock._events.add_actual(mock, prop_name, td)
                    prop.is_active = False
                    return
                prop_name = f"{prop.name} deleter inactive"
                td = TypeData(prop_name, mock._check_type).no_fix()
                return mock._events.add_actual(mock, prop_name, td)

            return deleter
        return None
