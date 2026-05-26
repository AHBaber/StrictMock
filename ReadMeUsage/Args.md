## Args and Kwargs

Functions and Methods quite often take in arguments when called. Positional arguments are determined by the order the
arguments appear in the functions declarations. Keyword Arguments use the explicit names of the arguments in the
function's declaration.

StrictMock supports both positional and key word arguments when mocking a function. All you need to do is include the
arguments in the Expected() event.

```
Expected("function", 1, 2, 3, 4)

Expected("function", a=1, b=2, c=3, d=4)

Expected("function", 1, 2, d=4, c=3)  # note order is changed in key words
```

When the StrictMock receives any values passed into the function, the actual values passed in must match what is
provided in the Expected() event, both by value and by type. If they do not match 100%, then a MockError will be raised;
and the values must be rectified.

### Examples

[tests/test_example_args.py](../tests/test_example_args.py)

### Defaults

If a function has default values, then the default value will be used if the argument is not passed in.

Requirements:

- if a default value is used in the actual call, then the argument cannot be listed in the Expected() event.
- if a value is used to override the default in the actual call, then it must appear in the Expected() event. Even if
  the value is the same as the default.

The reason for these rules is that it makes the values in Expected() reflect that fact that a default value is being
used, or not used.

### TypeIgnore

In some cases, the type of a parameter is incorrect. For example, in some database clients, the params field has a type
of ```Optional[Sequence]``` but will actually except ```Dict[str, Any]``` as well. Due to StrictMock's design to be
strict, passing in a Dict would result in an error. This can be overridden by using ```TypeIgnore```.

```
class Cursor:
    def execute(query: str, params: Optional[Sequence])
        ...
        
```

We can wrap the expected value in TypeIgnore, In which case, the values from the actual call must still match the value
in the Expected(), but the type returned from examining the function signature will be ignored.

```
query = "..."
Expected("execute", query, TypeIgnore(dict(a=1)))
```

Example: [tests/test_example_args.py](../tests/test_example_args.py)

### ValueIgnore

In some cases, we will have a value that we cannot accurately predict. Since the StrictMock requires precise values, we
have a situation where we cannot correctly predict the value that will be returned. In that case, we can use
```ValueIgnore``` to ignore the value.

Note: this feature was created specifically to deal with traceback objects (whose data includes line numbers). While it
may used when dealing with any expected event, doing so must be done with extreme circumspection. Otherwise, you are
bypassing one of the major reasons for using a StrictMock in the first place. See Context Managers for a more specific
example.

Example: [tests/test_example_equality.py](../tests/test_example_equality.py)

### IValueEqual

In some cases, you will be using classes that were created in such a way that the equality operator is not reliable
during unit testing. Either that the class does not implement it, or the instances contain data that is not
deterministic. The ideal fix is to correct the class such that the non-deterministic behavior is removed, and that the
equality method works correctly.

In the event that making these correction are unfeasible, we can use the IValueEqual interface to provide a workaround.
Albeit, this workaround should be viewed as a significant code smell.

To use IValueEqual, we need to override the __init__() and __eq__() methods so that we can create an object that may be
used to test. Optionally, we can override __repr__() to provide more details in the event a test is failing.

Example: [tests/test_example_i_value_equal.py](../tests/test_example_i_value_equal.py)

### ImportedTypes

Third Party libraries will define their own classes and types. This becomes an issue since those types may not exist in
the code where StrictMock is checking the type information.

We can deal with these situations by passing ImportedTypes() into the StrictMock during its creation.

```
expected_calls = Events([...])
imported = ImportedTypes(ThirdPartyType1, ThirdPartyType2)

mock = strict_mock(spec_type, events=expected_calls, imported=imported)
...
```

Furthermore, third party libraries function signatures may be returning strings for typing information instead of actual
types. For example, I have seen ```Optional[Sequence]``` be given a type string of ```"Sequence | None"```.

See test_example_context_manager for a more specific example.

Example: [tests/test_example_context_manager.py](../tests/test_example_context_manager.py)
