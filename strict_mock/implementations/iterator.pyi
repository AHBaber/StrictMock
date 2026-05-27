from ..analysis import Expected as Expected, ParamIgnore as ParamIgnore, TypeData as TypeData
from ..analysis.errors import MockIteratorError as MockIteratorError
from typing import Any, Callable

def expected_iter(data: list[Any]) -> list[Expected]: ...

iter_dunders: dict[str, Callable]
