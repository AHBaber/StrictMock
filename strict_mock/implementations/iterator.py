from typing import Any, Callable, Dict, List

from ..analysis import Expected, ParamIgnore, TypeData
from ..analysis.errors import MockIteratorError


def _iter(mock) -> Any:
    mock._events._set_error_type(MockIteratorError)
    td = TypeData("__iter__", mock._check_type, p=ParamIgnore("self"))
    mock._events.add_actual(mock, "__iter__", td)
    return mock


def _next(mock) -> Any:
    mock._events._set_error_type(MockIteratorError)
    td = TypeData("__next__", mock._check_type, p=ParamIgnore("self"))
    return mock._events.add_actual(mock, "__next__", td)


def expected_iter(data: List[Any]) -> List[Expected]:
    """Build the ``Expected`` entries needed to mock a complete iteration over a sequence.

    Produces one ``__iter__`` entry followed by one ``__next__`` entry per item
    in ``data``, and a final ``__next__`` entry that raises ``StopIteration`` to
    signal the end of the sequence.

    Args:
        data: The values to be yielded by the iterator, in order.

    Returns:
        A list of ``Expected`` entries suitable for passing to ``Events``.

    Example::

        mock = strict_mock(MyIterable, events=Events(expected_iter([1, 2, 3])))
    """
    e = [Expected("__iter__")]
    e += [Expected("__next__").returns_value(d) for d in data]
    return e + [Expected("__next__").stop_iteration()]


iter_dunders: Dict[str, Callable] = {
    "__iter__": _iter,
    "__next__": _next,
}
