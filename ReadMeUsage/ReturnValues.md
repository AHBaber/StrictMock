## Return Values

StrictMock provides the ability for Expected() entries to return values. However, there
are some rules around this, which if not followed, will cause a MockError to be raised.

In fact, if a non-optional return value is specified, then StrictMock will raise an
error indicating that one needs to be added.

There are 4(5) different patterns of returned values that StrictMock addresses:

- no return value was specified.
- None was explicitly specified.
- A specific type was specified.
- A Union type was specified.
- An Optional type was specified.

Each pattern will have different effects on how StrictMock expects them to be addressed.
For demonstrations: see [tests/test_example_return_values](../tests/test_example_return_values.py)

Note: all arguments in the Expected() event must match what is actually passed in before a value is returned.

### Methods for Returning Values

By default, a value of None is returned whenever a mocked function or method is called. However, there are two important
methods that allow values to be returned:

```
Expected(...).returns_value(...)
Expected(...).returns_mock(str, bool)
```

```.returns_value(...)``` works as you would expect: it returns the value.

When we return the mock itself, or another mock, we don't use ```.returns_value(...)```, instead we use
```.returns_mock(str, bool)```. This method is used for the following reasons:

1) it makes is clear that a mock is being returned, and not an actual value.
2) we do not need to have the mock defined prior to listing it as being returned.

Furthermore, if you are chaining multiple mocks together, then you must put the name of the mock as a parameter. This is
to ensure that the proper mock is being returned.

In the event there is a typing issue with the mock being returned, you can pass ```ignore_type=True``` into the call,
and that will override the type checking. Using this override should be done with great circumspect, and should be
considered a code smell.

### Examples

[tests/test_example_return_values.py](../tests/test_example_return_values.py)

#### No Return Specified or Any specified

If no return type is specified, then there are no real expectations. This situation is treated the same as if Any is the
the return type.

```
def function_no_return_specified():
def method_returns_any() -> Any:
```

- Returns ```None``` by default.
- ```Any``` type may be returned from this function.

##### Passing

```
Expected(...)
Expected(...).returns_value(...)
```

#### Explicit None

The function explicitly returns None.

```def function_explicit_none() -> None:```

- Returns a value of ```None```.
- May return ```None``` via ```.returns_value(None)``` to the ```Expected()```; though the explicit return is unneeded.
- Any other value returned will cause a ```MockError``` to be raised.

##### Passing

```
Expected(...)
Expected(...).returns_value(None)
```

##### Will Raise Error

```
Expected(...).returns_value(...)
```

#### Specific Type

A specific type is specified to be returned.

```def function_explicit_type() -> SpecficType:```

- Must return a value.
- The returned value must match the specific type.

##### Passing

```
Expected(...).returns_value(SpecificType)
```

##### Will Raise Error

```
Expected(...)
Expected(...).returns_value(OtherType)
```

#### Optional Type

An Optional type is specified. Thus, None or a value of the specified type must be returned.

```def function_optional_type() -> Optional[SpecificType]:```

- Returns ```None``` by default.
- The returned value must be None or match the specific type.

##### Passing

```
Expected(...)
Expected(...).returns_value(None)
Expected(...).returns_value(SpecificType)
```

##### Will Raise Error

```
Expected(...).returns_value(...)
```

#### Union Type

An Union type is specified. Thus, a value of one the specified types must be returned.

```def function_union_type() -> Union[SpecificType1, SpecificType2]:```

- The returned value must match one of the specific types.

##### Passing

```
Expected(...).returns_value(SpecificType)
```

##### Will Raise Error

```
Expected(...)
Expected(...).returns_value(None)
Expected(...).returns_value(TypeNotSpecified)
```

Note: if one of the types specified include None, then these two lines will become passing:

```
Expected(...)
Expected(...).returns_value(None)
```
