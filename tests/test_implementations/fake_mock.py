from typing import Any

from strict_mock.analysis import CheckType

# it's a fake that represents the StrictMock
# but it's not a mock, since we don't need the
# full capabilities of a mock
# so I feel the existence of this class and
# its name to be pretty ironic


class FakeMock:
    def __init__(self, name: str = "", events: Any = None):
        self._name = name
        self._check_type = CheckType()
        self._events = events
