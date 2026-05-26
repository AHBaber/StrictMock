## Classes

When a StrictMock of a class is created, the mock will try to emulate the methods and properties of the class.

## Properties

See [Properties](Properties.md) for more details.

## Methods

Class Methods are emulated.

See [Args](Args.md) for more details.

## Dunders

Specific dunders are supported. They allow a StrictMock to mock classes, context managers, and iterators.

#### default defined on object

    __eq__
    __ne__
    __lt__
    __le__
    __gt__
    __ge__
    __hash__
    __repr__
    __str__
    __sizeof__
    __format__

Note: __str__, __repr__, and __format__ will return the name of the Mock. This also means these dunders are effectively
defined even though they are not in the Expected list. This is due to the fact that when reporting an error, the name of
the mock will appear in the error output, and we don't want to have infinite recursion to occur when reporting an error,
trying to get the name of the mock, no value appears in the Expected list, which causes a new error to be created...

#### type conversion

    __bool__
    __bytes__
    __complex__
    __float__
    __index__
    __int__
