class BaseWidget:
    def __init__(self, name: str, size: int = 1) -> None:
        raise NotImplementedError()

    def render(self) -> str:
        raise NotImplementedError()


class Widget(BaseWidget):
    # Deliberately defines no __init__ of its own, so its constructor
    # parameters are only reachable through BaseWidget.
    def resize(self, size: int) -> None:
        raise NotImplementedError()
