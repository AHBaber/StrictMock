from .utility import stringify

# Represents the actual data that is passed into the mock as arguments.


class Actual:
    """Records the name and arguments of a single call made on a mock.

    Instances are created automatically by the mock infrastructure each time a
    mocked method is invoked. They are compared against the corresponding
    ``Expected`` entry to determine whether the call matches.
    """

    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name  # the name of the function that was called
        self.args = args  # any args passed in
        self.kwargs = kwargs  # any kwargs that were passed in

    def as_str(self) -> str:
        """Return the call arguments formatted as a parenthesized parameter string.

        The result is suitable for embedding inside an ``Expected(...)`` or
        ``Actual(...)`` expression, for example ``("method_name", 1, key="val")``.
        """
        args = self._get_args()
        kwargs = self._get_kwargs()
        comma = ", " if args and kwargs else ""
        params = f"{args}{comma}{kwargs}"
        comma = ", " if params else ""
        m = f'("{self.name}"{comma}{params})'
        return m

    def report(self, indent: str = "") -> str:
        """Return a string representation of this actual call as valid Python source.

        The output can be pasted directly into a test as a fix suggestion,
        for example ``Actual("method_name", 1, key="val")``.
        """
        return f"{indent}Actual{self.as_str()}"

    def _get_args(self) -> str:
        if not self.args:
            return ""
        args = [stringify(a) for a in self.args]
        return ", ".join(args)

    def _get_kwargs(self) -> str:
        if not self.kwargs:
            return ""
        sorted_items = sorted(self.kwargs.items())
        return ", ".join(f"{key}={stringify(value)}" for key, value in sorted_items)

    def __repr__(self) -> str:
        """Return the same string as ``report()``, used when the object is printed or inspected."""
        return self.report()
