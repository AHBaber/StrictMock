## Supported Dunders

These dunders are implemented as part of the StrictMock. Accessing them is the same as for any methods, we just need to
explicitly use the dunder's name as the method name.

### Synchronous Dunders

```
__bool__
__bytes__
__call__
__complex__
__contains__
__delitem__
__enter__
__eq__
__exit__
__float__
__format__
__ge__
__getitem__
__gt__
__hash__
__index__
__int__
__iter__        used transparently when mocking iterators
__le__
__len__
__length_hint__
__lt__
__ne__
__next__
__repr__
__reversed__
__setitem__
__sizeof__
__str__
```

### Asynchronous Dunders

AsyncStrictMock uses specific dunders as well.

```
__aenter__
__aexit__
__aiter__   used transparently when mocking asynchronous iterators
__anext__
__await__   this is actully a synchronous dunder, but is only used when writing async code
__call__    this may be implemented as an asynchronous method as well
```

## Reserved

StrictMock reserves a small number of dunders to provide specific functionality.

```
__class__         used to disguise the StrictMock as instance of the specifying class
__del__           reserved for future use
__dict__          defines the structure of the StrictMock, and not the specifying class
__getattr__       used to catch and report unimplemented methods / methods not listed in Events
__getattribute__  used implicitly by StrictMock
__init__          used by the StrictMock during its creation
__init_subclass__ reserved for future use
__instancecheck__ reserved for future use
__iter__          used transparently when mocking iterators
__new__           used implicitly by the StrictMock during its creation
__prepare__       reserved for future use
__reduce__        reserved for future use
__setattr__       used implicitly by the StrictMock during its creation
__subclasscheck__ reserved for future use
__subclasshook__  reserved for future use
__weakref__       reserved for future use
```

## Disallowed

Several dunders are not allowed to be used with a StrictMock. The primary reason is that the features provided by these
dunders focused on logic / state that should not be part of a mock. Any values being returned by a mock should be
explicitly specified.

```
__abs__
__add__
__and__
__ceil__
__class_getitem__
__copy__
__deepcopy__
__delete__
__divmod__
__floor__
__floordiv__
__get__
__iadd__
__iand__
__ifloordiv__
__ilshift__
__imatmul__
__imod__
__imul__
__invert__
__ior__
__ipow__
__irshift__
__isub__
__itruediv__
__ixor__
__lshift__
__matmul__
__missing__
__mod__
__mul__
__neg__
__or__
__pos__
__pow__
__radd__
__rand__
__rdivmod__
__rfloordiv__
__rlshift__
__rmatmul__
__rmod__
__rmul__
__ror__
__round__
__rpow__
__rrshift__
__rshift__
__rsub__
__rtruediv__
__rxor__
__set__
__set_name__
__setstate__
__sub__
__truediv__
__trunc__
__xor__
```
