from ..analysis import MockContextManagerError as MockContextManagerError, MockError as MockError, Param as Param, ParamIgnore as ParamIgnore, ParamList as ParamList, TypeData as TypeData
from typing import Any, Callable

def cm_enter(mock) -> Any: ...
def cm_exit(mock, exc_type, exc_val, exc_tb) -> bool | None: ...

cm_dunders: dict[str, Callable]
