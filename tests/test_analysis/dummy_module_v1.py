# this is a dummy module used for testing types where a class is defined in two different modules with the same name

__all__ = [
    "Dummy",
]


class Dummy:
    def __init__(self, a: int):
        self.a = a

    def __repr__(self) -> str:
        return f"Dummy({self.a})"

    def __eq__(self, other):
        if not isinstance(other, Dummy):
            return False
        return self.a == other.a


def new_dummy(d: Dummy) -> "Dummy | None":
    return None
