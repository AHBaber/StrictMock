from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

from strict_mock.analysis import Actual, ErrorExpected, Expected, TypeData


class Status(Enum):
    Correct = " "
    Extra = "Extra "
    Mismatched = "Mismatched "
    Error = "Error "


def _indent(status: Status, index: int) -> str:
    return f"{status.value:<11} {index:>4}: "


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
        labeled ``Extra``. Type-check errors from ``TypeData`` are indented
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
        # no AsyncGroup will be in the intersect section
        # as this covers everything that was tested with Expected.compare(Actual)
        intersect = min(len(expected), len(actual))
        for i in range(intersect):
            status = Status.Correct
            e = expected[i]
            a = actual[i]
            td = type_data[i]
            if isinstance(e, ErrorExpected):
                status = Status.Error
            elif e.compare_actual(actual[i]):
                status = Status.Mismatched
            _expected.append(e.report(_indent(status, i)))
            if td and td.has_errors:
                _expected.extend([f"                      {tde}" for tde in td.errors])
            _actual.append(a.report(_indent(status, i)))
        status = Status.Extra
        # this is safe, since anything in expected is Expected or derived from Expected
        for i in range(intersect, len(expected)):
            _expected.append(expected[i].report(_indent(status, i)))
        for i in range(intersect, len(actual)):
            _actual.append(actual[i].report(_indent(status, i)))
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
