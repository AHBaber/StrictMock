# A Comparison of Mock, Magic Mock, and StrictMock

## Spec

Mock, Magic Mock: not required
StrictMock: required

## Asserts

Mock, MagicMock: has several functions to check if the mock was called or not

```
    assert_called()                             -- the mock was called at least once
    assert_called_once()                        -- the mock was called once and only once
    assert_called_with(*args, **kwargs)         -- checks if the last time the mock was called with the specific args and/or kwargs
    assert_called_once_with(*args, **kwargs)    -- the mock was called once with the specific args and/or kwargs
    assert_any_call(*args, **kwargs)            -- checks if the mock was called with specific args and/or kwargs
    assert_has_calls(calls, any_order=False)    -- checks if all these calls were made
    assert_not_called()                         -- checks to see if the mock was never called
```

StrictMock: has all the above functionality performed by two components

```
    [Expected]          -- a list of all events that happen in order
    assert_all_calls()  -- checks to see if all of the expected calls were acutally made
```

StrictMock's corresponding actions are:

```
    assert_called()                             -- [Expected] is not empty
    assert_called_once()                        -- [Expected] has a length of 1
    assert_called_with(*args, **kwargs)         -- all calls must be in [Expected]
    assert_called_once_with(*args, **kwargs)    -- all calls must be in [Expected]
    assert_any_call(*args, **kwargs)            -- all calls must be in [Expected]
    assert_has_calls(calls, any_order=False)    -- all calls must be in [Expected]
    assert_not_called()                         -- [Expected] is an empty list
```

Furthermore, StrictMock checks all args/kwargs passed into the mock to see if they match what is in the
Expected() line. If there are any discrepancies (type or value) than an error is raised. Note: this error will prevent a
returns_value() or raises_error() from being executed.

StrictMock does not implement:

```
reset_mock(*, return_value=False, side_effect=False)
mock_add_spec(spec, spec_set=False)
attach_mock(mock, attribute)
configure_mock(**kwargs)
__dir__() 
_get_child_mock(**kw)
called -- implicitly part of [Expected]
call_count -- implicitly part of [Expected]
call_args -- implicitly part of [Expected]
call_args_list -- implicitly part of [Expected]
method_calls -- implicitly part of [Expected]
mock_calls -- implicitly part of [Expected]
```

## return_value

Mocks and MagickMocks will automatically return a new mock if a return value is not set.

StrictMock

- will return None by default if the function / method has no return value specified, or has None as it's return value
- will raise an error if the function / method has a return type specified, but no returns_value set on the Expected()
  line.
- will raise an error if the function / method is called and the returned value is not the correct type

## side_effect

This is used by Mock and MagicMock to return a series of values, or raise an error.

```
mock.side_effect = [5, 4, 3, 2, 1]
mock(), mock(), mock()
(5, 4, 3)
```

StrictMock returns a series of values by using returns_value() on each Expected() line.

```
expected_calls = Events([
    Expected("__call__").returns_value(5),
    Expected("__call__").returns_value(4),
    Expected("__call__").returns_value(3),
])
mock = strict_mock(Spec, events=expected)
mock(), mock(), mock()
(5, 4, 3)
```

side_effect may also be used by Mock and MagicMock to raise an error. StrictMock does this with
Expected().raises_error()

```
expected = [
    Expected("method", 3, 5, "abc").raises_error(ValueError("Hamster Huey and the Gooy Kablooy")),
]
```

Note: if the args in Expected() do not match the values actually passed in, then a MockError will be raised, and not
the error in raises_error(). If for some reason returns_value() and raises_error() are attached to the same Expected,
then raises_error will take precedence.

## unittest.mock.NonCallableMock

This type is not needed as the StrictMock is only callable if the spec it is mocking is callable.

## class unittest.mock.PropertyMock

This is not needed, as the StrictMock will either have the properties, or will have them created via Prop.

## class unittest.mock.AsyncMock

Not yet implemented

## class unittest.mock.ThreadingMock

Not yet Implemented

## Deleting Attributes

If you do not want an attribute to be callable there are multiple ways to handle this:

1) If spec has an existing property on it, you can pass a Prop() with is_active=False during the creation of the
   StrictMock. This will make the property unusable.
2) Create an Expected().raises_error() object, and have it raise the appropriate error.
