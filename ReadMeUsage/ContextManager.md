## Context Managers

StrictMock supports mocking of classes that are context managers. Setting up the expected calls is pretty simple. The
first event to denote is "__enter__", as well as "__exit__". When the context exits, there are three args that will be
passed, all of them will be None.

```
expected_calls = Events([
    Expected("__enter__"),
    ...
    Expected("__exit__", None, None, None),
])
```

### Examples

* [UnitTest Example](../tests/test_example_python_unittest/test_example_context_manager.py)
* [PyTest Example](../tests/test_example_pytest/test_example_context_manager.py)

### Nesting Contexts

Multiple contexts may be nested. Simply create a mock for each context, and provide each mock with its list of expected
events.

### Error Handling

In some cases an error will occur within the context. If this is a situation you intend to test for, then there are
three values that must be checked as well.

| field    | description                           | notes                           |
|----------|---------------------------------------|---------------------------------|
| exc_type | the type of the error that was raised | this will be a type             |
| exc_val  | the text value of the error           | this will be a string           |
| exc_tb   | the traceback object                  | this will be a traceback object |

Note 1: exc_val is converted into a string by strict_mock. This was done to make writing the unit tests more simple.

Note 2: there is an issue where the traceback object cannot be reliably predicted. This is due to the fact that any file
changes, or even the run time may change values in the object. As a workaround, we are able to use ValueIgnore as
the third parameter.

For example, this situation:

```
with context_manager:
    raise ValueError("value was wrong")
```

Would have expected calls that look like this:

```
expected_calls = Events([
    Expected("__enter__").returns_mock(),
    Expected("__exit__", ValueError, "value was wrong", ValueIgnore).returns_value(False),
])
```

Another aspect is that when testing for an error within a context, you are able to control if the error escapes the
context or not. If the "__exit__" returns a value of False, then the error will exit the context and continue until it
is caught.

However, if the "__exit__" event returns a value of True, then the error will be swallowed.

```
.returns_value(True)  # swallows error
```

## Limitations

For some reason, a call to ```inspect.signature()``` returns no return type annotation. So, StrictMock treats this as no
return type is specified. So, technically speaking, this means that using a ```.returns_value(...)``` or
```returns_mock(...)``` is only necessary if we are using ```with ... as ...```. Failure to return a necessary value or
mock in this case should be rather obvious, as anywhere the "as value" is used will be none, and should raise an error
when it is used.

It is important to be aware of this limitation, as StrictMock will not report the need for a return value or mock when
reporting a fix recommendation.
