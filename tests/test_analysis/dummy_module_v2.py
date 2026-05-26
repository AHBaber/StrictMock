# this is a dummy module used for testing types where a class is defined in two different modules with the same name

__all__ = [
    "Dummy",
]


class Dummy:
    def __init__(self, b: int):
        self.b = b

    def __repr__(self) -> str:
        return f"Dummy({self.b})"

    def __eq__(self, other):
        if not isinstance(other, Dummy):
            return False
        return self.b == other.b
