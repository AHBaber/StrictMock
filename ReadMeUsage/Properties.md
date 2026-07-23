## Properties

StrictMock supports properties on classes. Getters, setters, and deleters are all supported. Note that if a deleter is
called, then subsequent calls to a getters or setter will cause an error to be raised.

#### getter

This will return a value when called. The exact value returned will be set on the corresponding Expected event.

#### setter

A value may be "set" on a property. This value will be verified in the Expected Event. Note: the set value is not
actually stored.

#### deleter

If enabled, del may be called on a property. Once this is done, the mock will consider the property to be deleted, and
thus any subsequence calls will cause an error to be raised.

### Examples

Decorator

* [UnitTest Example](../tests/test_example_python_unittest/test_example_properties_decorator.py)
* [PyTest Example](../tests/test_example_pytest/test_example_properties_decorator.py)

Class Type Annotations

* [UnitTest Example](../tests/test_example_python_unittest/test_example_properties_class.py)
* [PyTest Example](../tests/test_example_pytest/test_example_properties_class.py)

Artificial

* [UnitTest Example](../tests/test_example_python_unittest/test_example_properties_artificial.py)
* [PyTest Example](../tests/test_example_pytest/test_example_properties_artificial.py)

### Decorator Properties

Classes may have properties added to them via decorators. StrictMock will identify these properties and add them to the
mock automatically. StrictMock supports getter, setter, and deleter.

Note: due to some oddity in the inspect library, the actual type of the getter is not retrieved. This means type safety
is effectively disabled when mocking a property created via a decorator.

### Class Properties

StrictMock will identify properties that are part if the class definition, and add them to the mock. However, if a
property is added to the class as part of instantiation, then it will not be part of the StrictMock.

```
class ClassWithProperty:
    prop: str  # will be mocked

    def __init__(self):
        self.later = ...   # will NOT be mocked
```

### Artificial Properties

The primary purpose of Artificial Properties is to provide the ability to add a property that does not exist in the
class, but is added to the instance at a later point. For example, values that are added to the class inside an
__init__() will not be created as properties. Adding an Artificial Property may be done when instantiating a
StrictMock by using the Prop class.

```
expected_calls = Events([
   ...
])
props: List[Prop] = [
    Prop("prop", str, True, True),
]
mock = strict_mock(Spec, events=expected_calls, properties=props)

mock.prop = 5
actual = mock.prop
```

Note: Artificial Properties will override decorator or class properties.

### Prop Class

The Prop class is a simple structure that lets us define a single property. By default, getter, setter, and deleter are
not enabled.

```
@dataclass
class Prop:
    name: str                # the name of the property
    type: Type[Any]          # the type of the property
    getter: bool = False     # use True to enable getter
    setter: bool = False     # use True to enable setter
    deleter: bool = False    # use True to enable deleter
    is_active: bool = True   # flag to indicate if the prop is enabled or not
```

An error will be raised when using the property under the following conditions:

- any call to the property is made when the property is disabled
- the getter is called when the getter is disabled
- the setter is called when the setter is disabled
- the deleter is called when the deleter is disabled
