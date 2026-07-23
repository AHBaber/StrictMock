from .utility import stringify as stringify
from _typeshed import Incomplete

class Actual:
    name: Incomplete
    args: Incomplete
    kwargs: Incomplete
    def __init__(self, name: str, *args, **kwargs) -> None: ...
    def as_str(self) -> str: ...
    def report(self, indent: str = '') -> str: ...
