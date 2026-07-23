from typing import Any, Dict, List, NoReturn, Optional, Type

from strict_mock.analysis import (Actual, ErrorExpected, Expected,
                                  MockCreationError, MockError, TypeData,
                                  TypeIgnore)
from strict_mock.implementations.formatter import (DefaultFormatter,
                                                   IReportFormatter)


class Events:
    """Ordered sequence of expected calls for one or more mocks in a single test.

    Pass a populated ``Events`` instance to ``strict_mock()`` to declare what
    calls the mock is expected to receive and in what order. When ``assert_all_calls``
    is called on the mock, ``Events`` verifies that every expected call was made
    and raises a ``MockError`` with a formatted report if there is any discrepancy.

    When multiple mocks share the same ``Events`` instance (chained mocks), all
    mock names must be unique within that instance.

    Args:
        expected: Initial list of ``Expected`` entries.
        formatter: Custom formatter for discrepancy reports. Defaults to
            ``DefaultFormatter``.
    """

    def __init__(self, expected: Optional[List[Expected]] = None,
                 formatter: Optional[IReportFormatter] = None):
        self._formatter = formatter or DefaultFormatter()
        self._expected: List[Expected] = expected or []
        self._actual: List[Actual] = []
        self._type_data: List[Optional[TypeData]] = []
        self._error_type: Type[MockError] = MockCreationError
        self._error_reported = False
        self._mocks: Dict[str, Any] = {}

    def __iter__(self):
        """Iterate over the expected calls in declaration order."""
        return iter(self._expected)

    def _add_mock(self, name, mock) -> None:
        if name in self._mocks:
            raise MockCreationError(f"All mocks must be unique names in a given test, '{name}' has been declared twice")
        self._mocks[name] = mock

    def _check_for_mock(self, mock: Any, expected: Expected, index: int) -> Expected:
        if not expected._is_mock():
            return expected
        name = expected._get_mock_name()
        if name:
            if name not in self._mocks:
                raise MockCreationError(f"No mock named '{name}' was created")
            mock = self._mocks[name]
        elif len(self._mocks) > 1:
            message = "\n".join([
                "All chained mocks must be named when returning self;",
                f"    index  : {index}\n"
                f"    current: {expected}\n"
                f"    fixed  : {expected._report_mock_fix(mock._name)}",
            ])
            raise MockCreationError(message)
        expected._check_for_self(mock)
        return expected

    def _assert_all_calls(self, mock) -> bool:
        # this will return true, or raise an error
        # on success it returns true so the call assert mock.assert_all_calls()
        # will appear consistent with all of the other values being checked
        if self._error_reported:
            return True  # only report one error at a time
        if self._has_errors():
            self._set_error_type(MockCreationError)
            self._report_errors(mock)
        return True

    def _set_error_type(self, error_type: Type[MockError]):
        self._error_type = error_type

    def _report_errors(self, mock) -> NoReturn:
        self._error_reported = True
        err = self._formatter.report(mock._name, self._expected, self._actual, self._type_data)
        raise self._error_type(err)

    def add_actual(self, mock, call_name: str, type_data: TypeData, *args, **kwargs) -> Any:
        """Record a call that was made on the mock and validate it against the next expected entry.

        Appends the call to the internal actual list, compares it to the
        corresponding ``Expected`` entry, runs argument type checks, validates
        the return value, and returns whatever the ``Expected`` entry specifies.
        Raises a ``MockError`` immediately if any discrepancy is found.

        Args:
            mock: The mock instance on which the call was made.
            call_name: The name of the method or dunder that was called.
            type_data: Type-checking context for this call, built from the spec's
                signature.
            *args: Positional arguments passed to the mock.
            **kwargs: Keyword arguments passed to the mock.

        Returns:
            The value specified by the matching ``Expected`` entry, or ``None`` if
            no return value was set.

        Raises:
            MockError: If the call does not match the next expected entry, a type
                check fails, or there are no remaining expected entries.
        """
        actual = Actual(call_name, *args, **kwargs)
        self._actual.append(actual)
        self._type_data.append(type_data)
        index = len(self._actual) - 1
        if index < len(self._expected):
            e = self._expected[index]
            if type(e) is not Expected:
                message = f"{type(e).__name__} where Expected was required"
                fix = "Expected(...)"
                self._expected[index] = ErrorExpected(message, fix, None, e)
                self._report_errors(mock)

            has_errors = e.compare_actual(actual)
            type_data.adjust_params(*e.args, **e.kwargs)  # apply ValueIgnore before checking
            has_errors |= type_data.check_types(*args, **kwargs)
            if has_errors:
                type_data.as_fix_method()
                self._report_errors(mock)
            e = self._check_for_mock(mock, e, index)
            rv = e._get_return_value()
            if type_data.check_return_value(rv):
                self._report_errors(mock)
            if isinstance(rv, TypeIgnore):
                return rv.value
            return rv
        # no expected
        type_data.as_fix_method()
        self._report_errors(mock)

    def _has_errors(self) -> bool:
        # if we have the same number of expected and actual
        # and an error was not already found, then are no errors
        # if actual < expected, then we have too many expected,
        # or not enough calls were made
        # if actual > expected then we have more going on then we expected
        return len(self._expected) != len(self._actual)
