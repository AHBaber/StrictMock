from enum import Enum
from typing import Any, Optional

from .actual import Actual
from .errors import MockCreationError
from .utility import TypeIgnore, ValueIgnore, stringify


class _ReturnType(Enum):
    kNone = 0
    kValue = 1
    kSelf = 2
    kSelfIgnore = 3


class Expected(Actual):
    """Declares a single expected call on a mock, including its arguments and optional return behavior.

    An ``Expected`` is constructed with the method name and the exact arguments
    that must be passed when the mock is called. It can optionally be chained
    with ``returns_value``, ``returns_mock``, ``raises_error``, or
    ``stop_iteration`` to control what happens when the call is matched.

    ``Expected`` entries are consumed in order: the first real call on the mock
    is compared to the first ``Expected``, the second call to the second, and so
    on. A mismatch at any position raises a ``MockError``.
    """

    def __init__(self, name: str, *args, **kwargs) -> None:
        super().__init__(name, *args, **kwargs)
        self._return_value: Any = None
        self._returns_type: _ReturnType = _ReturnType.kNone
        self._error: Optional[Exception] = None
        self._nomenclature = "Expected"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Expected):
            return False
        if self.name != other.name:
            return False
        if len(self.args) != len(other.args):
            return False
        if len(self.kwargs) != len(other.kwargs):
            return False
        for i in range(len(self.args)):
            if self.args[i] is ValueIgnore or other.args[i] is ValueIgnore:
                continue
            if self.args[i] != other.args[i]:
                return False
        for k, v in self.kwargs.items():
            if k not in other.kwargs:
                return False
            if v is ValueIgnore or other.kwargs[k] is ValueIgnore:
                continue
            if v != other.kwargs[k]:
                return False
        if self._returns_type != other._returns_type:
            return False
        if self._return_value != other._return_value:
            return False
        if self._error is not None:
            if other._error is None:
                return False
            if type(self._error) is not type(other._error):
                return False
            if str(self._error) != str(other._error):
                return False
        elif other._error is not None:
            return False
        return True

    def returns_value(self, value: Any) -> "Expected":
        """Set the value to be returned when this expected call is matched.

        Args:
            value: The value to return. Must satisfy the spec's return-type
                annotation; a ``MockError`` is raised at call time if it does not.

        Returns:
            self, to allow chaining (e.g. ``Expected(...).returns_value(x)``).
        """
        self._returns_type = _ReturnType.kValue
        self._return_value = value
        return self

    def returns_mock(self, name: Optional[str] = None, ignore_type: bool = False) -> "Expected":
        """Set this expected call to return a mock object rather than a plain value.

        When multiple mocks share the same ``Events`` instance (chained mocks),
        ``name`` must be provided so the correct mock is resolved at call time.

        Args:
            name: The name of the mock to return. If omitted, the single mock
                registered on the shared ``Events`` is returned.
            ignore_type: If ``True``, the return-type check is skipped. Use
                sparingly — skipping type checks is a code smell.

        Returns:
            self, to allow chaining (e.g. ``Expected(...).returns_mock("my_mock")``).
        """
        self._returns_type = _ReturnType.kSelfIgnore if ignore_type else _ReturnType.kSelf
        if name is not None:
            self._return_value = name
        return self

    def _is_mock(self) -> bool:
        return self._returns_type in (_ReturnType.kSelf, _ReturnType.kSelfIgnore)

    def _get_mock_name(self) -> Optional[str]:
        if self._returns_type in (_ReturnType.kSelf, _ReturnType.kSelfIgnore):
            return self._return_value
        return None

    def _check_for_self(self, mock: Any) -> None:
        if self._returns_type == _ReturnType.kSelfIgnore:
            self.returns_value(TypeIgnore(mock))
        elif self._returns_type == _ReturnType.kSelf:
            self.returns_value(mock)

    def raises_error(self, error: Exception) -> "Expected":
        """Set an exception to be raised when this expected call is matched.

        Args:
            error: The exception instance to raise.

        Returns:
            self, to allow chaining (e.g. ``Expected(...).raises_error(ValueError("bad")``).
        """
        self._error = error
        return self

    def stop_iteration(self) -> "Expected":
        """Raise ``StopIteration`` when this expected call is matched.

        Convenience wrapper around ``raises_error(StopIteration())`` intended
        for use as the terminal entry in an iterator mock.

        Returns:
            self, to allow chaining.
        """
        if self.name != "__next__":
            raise MockCreationError(f'.stop_iteration() may only be used with "__next__", not "{self.name}"')
        return self.raises_error(StopIteration())

    def stop_async_iteration(self) -> "Expected":
        """Raise StopAsyncIteration when this expected call is matched.

        Convenience wrapper around raises_error(StopAsyncIteration()) intended
        for use as the terminal entry in an iterator mock.

        Returns:
            self, to allow chaining.
        """
        if self.name != "__anext__":
            raise MockCreationError(f'.stop_async_iteration() may only be used with "__anext__", not "{self.name}"')
        return self.raises_error(StopAsyncIteration())

    def _get_return_value(self) -> Any:
        # if there is an error, then the error is raised
        # otherwise it will return the value if it is set
        # otherwise it will return none
        if self._error:
            raise self._error
        return self._return_value

    def compare_actual(self, actual: Actual) -> bool:
        """Compare this expected call against a call that was actually made.

        Arguments marked with ``ValueIgnore`` are skipped during comparison.
        Name, argument count, and keyword argument keys and values must all match
        for the calls to be considered equal.

        Returns:
            ``True`` if there is a discrepancy, ``False`` if the calls match.
        """
        if self.name != actual.name:
            return True
        if len(self.args) != len(actual.args):
            return True
        if len(self.kwargs) != len(actual.kwargs):
            return True
        for i in range(len(self.args)):
            if self.args[i] is ValueIgnore:
                continue
            if self.args[i] != actual.args[i]:
                return True
        for k, v in self.kwargs.items():
            if k not in actual.kwargs:
                return True
            if v is ValueIgnore:
                continue
            if v != actual.kwargs[k]:
                return True
        return False

    def report(self, indent: str = "") -> str:
        """Return a string representation of this expected call as valid Python source.

        The output includes the call arguments and any chained modifier
        (``returns_value``, ``returns_mock``, or ``raises_error``) so it can be
        pasted directly into a test as a fix suggestion.
        """
        rv = ""
        re = ""
        if self._returns_type == _ReturnType.kValue:
            rv = f".returns_value({stringify(self._return_value)})"
        elif self._returns_type == _ReturnType.kSelf:
            if isinstance(self._return_value, str):
                rv = f'.returns_mock("{self._return_value}")'
            else:
                rv = ".returns_mock()"
        elif self._returns_type == _ReturnType.kSelfIgnore:
            if isinstance(self._return_value, str):
                rv = f'.returns_mock("{self._return_value}", True)'
            else:
                rv = ".returns_mock(ignore_type=True)"
        if self._error is not None:
            e = str(self._error)
            re = f".raises_error({type(self._error).__name__}({stringify(e)}))"
        return f"{indent}{self._nomenclature}{self.as_str()}" + rv + re

    def _report_mock_fix(self, mock_name: str) -> str:
        rv = ""
        if self._returns_type == _ReturnType.kSelf:
            rv = f'.returns_mock("{mock_name}")'
        elif self._returns_type == _ReturnType.kSelfIgnore:
            rv = f'.returns_mock("{mock_name}", True)'
        return f"{self._nomenclature}{self.as_str()}" + rv


class ErrorExpected(Expected):
    def __init__(self, name: str, fix: str, expected: Optional[Expected] = None, other: Any = None) -> None:
        super().__init__(name)
        self._fix = fix
        self._expected = expected
        self._other = other

    def compare_actual(self, actual: Actual) -> bool:
        """Always report a discrepancy.

        An ErrorExpected stands in for a call that could not be matched, so any
        actual call compared against it is treated as a mismatch.

        Returns:
            True, always.
        """
        # always an error
        return True

    def report(self, indent: str = "") -> str:
        """Render this error as a multi-line fix suggestion.

        Includes the incorrect Expected or actual call when available, followed by
        the stored fix instruction.
        """
        lines = [f"{indent}Error in Expected: {self.name}"]
        indent = " " * (len(indent) + 4)
        if self._expected:
            lines.append(f"{indent}incorrect: {self._expected.report()}")
        if self._other:
            lines.append(f"{indent}incorrect: {type(self._other).__name__}: {self._other.location()}")
        lines.append(f"{indent}fix: {self._fix}")
        return "\n".join(lines)
