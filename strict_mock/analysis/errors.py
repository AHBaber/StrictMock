# These are errors that are related to creating the mock
# and are thus most likely a developer error occurring when
# creating the test cases.
# Thus we can tell that the raised error is a testing issue
# and not a code issue

__all__ = [
    "MockCallableError",
    "MockClassError",
    "MockContainerError",
    "MockContextManagerError",
    "MockCreationError",
    "MockError",
    "MockIteratorError",
    "MockMethodError",
    "MockPropertyError",
    "MockTypeError",
]


# base type of all or errors that are raised by a StrictMock
class MockError(Exception):
    pass


# Raised when a mock detects an error while mocking a function or functor.
class MockCallableError(MockError):
    pass


# Raised when a mock detects an error while mocking a class
class MockClassError(MockError):
    pass


# Raised when a mock detects an error while mocking a container.
class MockContainerError(MockError):
    pass


# Raised when a mock detects an error while mocking a context manager.
class MockContextManagerError(MockError):
    pass


# Raised when a mock is created and an error occurs.
# Also an AttributeError so that failed attribute lookups on a mock
# cooperate with hasattr/getattr-with-default introspection
# (e.g. inspect.iscoroutinefunction probing the mock).
class MockCreationError(MockError, AttributeError):
    pass


# Raised when a mock detects an error while mocking a iterator.
class MockIteratorError(MockError):
    pass


# Raised when a mock detects an error while mocking a method.
class MockMethodError(MockError):
    pass


# Raised when a mock detects an error while mocking a property.
class MockPropertyError(MockError):
    pass


# Raised when a typing error occurs
class MockTypeError(MockError):
    pass
