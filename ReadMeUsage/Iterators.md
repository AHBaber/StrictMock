## Iterators

A StrictMock may easily mock an iterator. If the spec passed into the StrictMock is an iterator, the only work that
needs to be done is to set up the Expected events correctly.

### Examples

[tests/test_example_iterator.py](../tests/test_example_iterator.py)

### expected_iter()

This is a convenience function that will generate a list of Expected events to represent an iterator that is passed into
a for loop.

```
expected_calls: List[Expected] = expected_iter([1, 2, 3])
```

is the same as

```
expected_calls: List[Expected] = [
    Expected("__iter__"),
    Expected("__next__").returns_value(1),
    Expected("__next__").returns_value(2),
    Expected("__next__").returns_value(3),
    Expected("__next__").stop_iteration(),
]
```

Note if the iterator is being passed into a comprehensions, an additional call to "__iter__" is performed. Thus, to use
expected_iter(), you need to set up the expected calls like this:

```
expected_calls: List[Expected] = [Expected("__iter__")] + expected_iter([1, 2, 3])
```

In other cases, "__iter__" may not be called at all. In that case we may need to slice the array to get the proper
Expected events.

Ultimately, running the test will tell you if you need to add an __iter__, or remove it.
