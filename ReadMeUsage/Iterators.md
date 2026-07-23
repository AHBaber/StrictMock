## Iterators

A StrictMock may easily mock an iterator. If the spec passed into the StrictMock is an iterator, the only work that
needs to be done is to set up the Expected events correctly.

### Examples

* [UnitTest Example](../tests/test_example_python_unittest/test_example_iterator.py)
* [PyTest Example](../tests/test_example_pytest/test_example_iterator.py)

### expected_iter()

This is a convenience function that will generate a list of Expected events to represent an iterator that is passed into
a for loop.

```
expected_calls: List[Expected] = expected_iter([1, 2, 3])
```

is the same as

```
expected_calls: List[Expected] = [
    Expected("__next__").returns_value(1),
    Expected("__next__").returns_value(2),
    Expected("__next__").returns_value(3),
    Expected("__next__").stop_iteration(),
]
```

Note: ```__iter``` is handled transparently, and simply returns the StrictMock itself. As such, it does not need to be
included in the expected calls list.
