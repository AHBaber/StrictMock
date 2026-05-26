## Modules

We are able to mock modules via StrictMock. Any given module may contain one or more of the following elements. While I
provide a small discussion on mocking the functions and classes in modules. Other aspects of modules are noted below and
reasons why they probably should not be mocked.

## Functions

Module Functions may be mocked just like regular functions.

Example: [tests/test_example_module.py](../tests/test_example_module.py)

Note: the args and kwargs for builtin functions may not properly represent the usage. Quite often, they have no typing
information or don't even list the possible kwargs. In these cases, the lack of type info means the types will be
defaulted to Any.

For example os.execl() is defined as

    def execl(file, *args)

However, an actual call may look like this:

    os.execl("/bin/ls", "ls", "-l")

In these cases, You will need to look up proper documentation to ensure that function is being called correctly.

## Classes

Several modules allow a class to be instantiated. For example pathlib.Path() creates a Path object.

Example: [tests/test_example_module.py](../tests/test_example_module.py)

Note: the args and kwargs for module classes may not properly represent the usage. Quite often, they have no typing
information or don't even list the possible kwargs. In these cases, the lack of type info means the types will be
defaulted to Any.

## Constants

Most modules contain constant values. There is little reason to be trying to mock constant values.

## Instances

Some modules have global instances. These may be mocked if you can determine the underlying type of the global instance.

Another work around is to make an interface that represents the aspects of the global interface that are needed for the
test. And then mock that that interface. Note that this should be considered carefully, as any changes to the global
instance means the interface needs to be updated.

An important implication of mocking a global instance is that you can no longer use it directly as a global instance,
after all, you want your mock to be used instead. This can easily be dealt with by using dependency injection. And to
make it more convenient: you can use the global instance as a default value:

```
def some_function(i: int, b: bool, gi: GlobalInstanceType = GlobalInstance):
    ...


class SomeClass:
    def __init__(self, gi: GlobalInstanceType = GlobalInstance):
        self._gi = gi
        ...
```

Now, the function and class will use the global instance by default, but you are able to inject a mock in for testing
purposes.

## Exceptions

Exceptions are rather simple classes, and typically do not need to be mocked.
