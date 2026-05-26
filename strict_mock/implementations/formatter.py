from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

from strict_mock.analysis import Actual, Expected, TypeData


class Status(Enum):
    Correct = "           "  # noqa: E222
    Extra = "Extra      "  # noqa: E222
    Mismatched = "Mismatched "


class IReportFormatter(ABC):
    """Interface for formatting the discrepancy report raised by a failed mock assertion.

    Pass a custom implementation to ``Events`` via the ``formatter`` parameter to
    override how mismatches are presented.
    """

    @abstractmethod
    def report(self, name: str,
               expected: List[Expected],
               actual: List[Actual],
               type_data: List[Optional[TypeData]]) -> str:
        """Format and return the discrepancy report as a string.

        Args:
            name: The name of the mock that failed.
            expected: The ordered list of expected calls.
            actual: The ordered list of calls that were actually made.
            type_data: Type-check results aligned with ``actual``; entries may be
                ``None`` for calls where no type data was recorded.

        Returns:
            A human-readable string describing the mismatch, suitable for use as
            an exception message.
        """
        raise NotImplementedError("IReportFormatter.report() was not implemented")


class DefaultFormatter(IReportFormatter):
    """Default implementation of ``IReportFormatter``.

    Produces a side-by-side listing of expected and actual calls, annotated with
    a status label (``Correct``, ``Mismatched``, or ``Extra``) and any type-check
    error messages. The output is intended to be read as an exception message that
    guides the developer toward the correct ``Expected(...)`` declaration.
    """

    def report(self, name: str,
               expected: List[Expected],
               actual: List[Actual],
               type_data: List[Optional[TypeData]]) -> str:
        """Format the discrepancy report for a failed mock assertion.

        Paired calls that share the same index are compared and labelled
        ``Correct`` or ``Mismatched``. Calls that appear in only one list are
        labelled ``Extra``. Type-check errors from ``TypeData`` are indented
        beneath the relevant entry.

        Args:
            name: The name of the mock that failed.
            expected: The ordered list of expected calls.
            actual: The ordered list of calls that were actually made.
            type_data: Type-check results aligned with ``actual``; entries may be
                ``None`` for calls where no type data was recorded.

        Returns:
            A formatted multi-line string describing the mismatch.
        """
        _expected: List[str] = []
        _actual: List[str] = []
        intersect = min(len(expected), len(actual))
        for i in range(intersect):
            status = Status.Correct
            e = expected[i]
            a = actual[i]
            td = type_data[i]
            if e.compare_actual(actual[i]):
                status = Status.Mismatched
            _expected.append(f"{status.value:<11} {i:>4}: {e.report()}")
            if td and td.has_errors:
                _expected.extend([f"                      {tde}" for tde in td.errors])
            _actual.append(f"{status.value:<11} {i:>4}: {a.report()}")
        status = Status.Extra
        for i in range(intersect, len(expected)):
            _expected.append(f"{status.value:<11} {i:>4}: {expected[i].report()}")
        for i in range(intersect, len(actual)):
            _actual.append(f"{status.value:<11} {i:>4}: {actual[i].report()}")
            td = type_data[i]
            if td and td.has_errors:
                _actual.extend([f"                      {tde}" for tde in td.errors])
        lines: List[str] = [
            f"StrictMock: {name} Discrepancies",
            f"Data Length\n    expected: {len(expected)}\n    actual  : {len(actual)}",
        ]
        lines += _expected
        lines += _actual
        return "\n".join(lines) + "\n\n"
