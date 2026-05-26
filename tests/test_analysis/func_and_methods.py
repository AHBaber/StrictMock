from typing import Any, Dict, List, Optional, Tuple


def function0():
    pass


def function1(a: int) -> None:
    pass


def function2(a: int, b: str):
    pass


def function3(a: int, b: str, c: Dict[str, List[int]]):
    pass


def function1d(a: Optional[int] = None):
    pass


def function2d(x: int, y: int = 0):
    pass


def function0r() -> Dict[str, List[Tuple[int, str]]]:
    return {}


def function0a() -> Any:
    return None


def functionArgs(*args: Any) -> None:
    return None


def functionKwargs(**kwargs: Any) -> None:
    return None


def functionArgsKwargs(*args: Any, **kwargs: Any) -> None:
    return None


def functionPosOnly(a: bool, b: int, /) -> None:
    return None


def functionPosOnlyd(a: bool = False, b: int = 7, /) -> None:
    return None


def functionPosOnlyVarPos(a: bool, b: int, /, *dimensions: str) -> None:
    return None


def functionKeysOnly(*, a: bool, b: int) -> None:
    return None


def functionKeysOnlyKwargs(*, a: bool, b: int, **k_dimensions: Any) -> None:
    return None


def functionPosThenKwargs(a: int, *, b: int) -> None:
    return None


class Class:
    def method0(self):
        pass

    def method1(self, a: int) -> None:
        pass

    def method2(self, a: int, b: str):
        pass

    def method3(self, a: int, b: str, c: Dict[str, List[int]]) -> None:
        pass

    def method1d(self, a: Optional[int] = None):
        pass

    def method2d(self, x: int, y: int = 0):
        pass

    def method0r(self) -> Dict[int, List[Dict[int, str]]]:
        return {}

    def method0a(self) -> Any:
        return None

    def methodArgs(self, *args: Any) -> None:
        pass

    def methodKwargs(self, **kwargs: Any) -> None:
        return None

    def methodArgsKwargs(self, *args: Any, **kwargs: Any) -> None:
        return None

    def methodPosOnly(self, a: bool, b: int, /) -> None:
        return None

    def methodPosOnlyVarPos(self, a: bool, b: int, /, *dimensions: str) -> None:
        return None

    def methodKeysOnly(self, *, a: bool, b: int) -> None:
        return None

    def methodKeysOnlyKwargs(self, *, a: bool, b: int, **k_dimensions: Any) -> None:
        return None

    @staticmethod
    def static_method(a: bool) -> None:
        return None

    @staticmethod
    def static_pos_only(a: str, /) -> None:
        return None

    @classmethod
    def class_method0(cls) -> None:
        return None

    @classmethod
    def class_method1(cls, c: str) -> None:
        return None

    @classmethod
    def class_pos_only(cls, c: str, /) -> None:
        return None


class SubClass(Class):
    pass
