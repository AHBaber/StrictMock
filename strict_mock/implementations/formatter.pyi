import abc
from abc import ABC, abstractmethod
from enum import Enum
from strict_mock.analysis import Actual as Actual, Expected as Expected, TypeData as TypeData

class Status(Enum):
    Correct = '           '
    Extra = 'Extra      '
    Mismatched = 'Mismatched '

class IReportFormatter(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def report(self, name: str, expected: list[Expected], actual: list[Actual], type_data: list[TypeData | None]) -> str: ...

class DefaultFormatter(IReportFormatter):
    def report(self, name: str, expected: list[Expected], actual: list[Actual], type_data: list[TypeData | None]) -> str: ...
