## Raising Errors

An Expected Event may also be used to raise an error. All it takes is to attach a .raises_error() to an Expected event.

```
expected_calls: List[Expected] = [
    Expected("__call__").raises_error(ValueError("boom")),
]
```

Note: the arguments must match between the Expected event and the Actual call before .raises_error() will be called. If
there is mismatch, then it must rectified before the call to .raises_error() will actually be raised.

### Examples

* [UnitTest Example](../tests/test_example_python_unittest/test_example_functions.py)
* [PyTest Example](../tests/test_example_pytest/test_example_functions.py)
