# StrictMock

## Design Concepts and Goals

Mocking a useful and standard tool for building unit tests. However, I have found a few frustrations with using them.
Most of these frustrations are around how developers use mocks more than how the mock actually function; but the
underlying
issue is that it is easy for developers to make several mistakes resulting in a passing tests, when the test should have
failed.

1) Each method must be tested separately.
2) Negative tests must be explicitly added to verify that specific method was mot called.
3) Quite often devs will verify that a method was called, but not what values are actually passed in.

## What StrictMock Brings

1) A single set of expected values that list every action the mock takes.
2) All actions the mock take are explicitly ordered.
3) Any discrepancy causes an error to be raised immediately.
4) The error will tell what needs to be done to fix the issue.
5) The errors raised will be a child of MockError to further indicate it is a StrictMock that has detected a
   discrepancy.
6) Each StrictMock will identify itself when raising an error so that a developer will be able to easily identify it
   for updating.

A StrictMock takes a fail fast approach. As soon as it encounters any discrepancy between what is expected and what has
actually happened, it will raise an error. This is based on the simple premise that if an error occurs early on, then
you cannot trust any events afterwards.

When an error is raised, it will be a subclass of MockError. This tells you that the error is due to an input (or
missing return value). Thus you know you need to fix some aspect of the mock.

Another advantage of this is that if code being tested is modified, then the StrictMock will immediately start raising
errors.

Finally, you may set up the StrictMock, not set any Expected events, and run the test. The Strict Mock will start
giving you suggestions on how to fix the missing Expected events.

### Supported Actions

1) Methods on a class
2) Decorator Properties
3) Class Properties
4) Artificial Properties
5) Functions and Functors (Callable)
6) Iterators
7) Context Managers
8) Mixed Objects (e.g object that acts as both a class and a container)
9) Modules (module.classes and module.functions)

## Limitations

1) Since the StrictMock addresses all events in a specific order, it may only be used for synchronous testing.
2) Properties created with decorators don't have type info, thus strict_mock will default to a type of Any. This can be
   worked around by using Artificial Properties.
3) Attributes that become assigned to an instance after it is initialized will not automatically be created. This is due
   to the fact that they do not exist as part of the class. Once again, Artificial Properties provide a solution.
4) There is an expectation that __eq__ is correctly implemented for all types being used for args in the tests. In the
   event a type does not implement __eq__ correctly, then you may use IValueEqual as a work around.
5) Modules global instances are not directly supported.
6) Module Constants should not be mocked. They are constants after all.
7) There is not a patch feature.  (Note: I am strongly biased towards dependency injection anyway).
8) Async is not officially supported as of yet.
9) Threading is not officially supported as of yet.
10) Importing classes with the same name from different modules may cause problems.

## Installing

pip install StrictMock

## Using the StrictMock

Concepts and usage are further explored in [ReadMeUsage](https://github.com/AHBaber/StrictMock/tree/main/ReadMeUsage)

Example files are also provided. These are all unit tests that also provide usage documentation. Each of these files has
the prefix "test_example". Furthermore, some of these files have the suffix "_errors". These files show common errors
that may occur while creating the StrictMock.

[UnitTest Examples](https://github.com/AHBaber/StrictMock/tree/main/tests/tests_example_python_unittest)
[PyTest Examples](https://github.com/AHBaber/StrictMock/tree/main/tests/tests_example_pytest)

# Set Up Local Development Environment

```
python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt

python setup.py egg_info

```

## Linting / Unit tests

```
sh check.sh
```

#### linting only

```
sh lint.sh
```

#### unit tests only

```
pytest --cov=strict_mock tests --cov-report term-missing
```

#### Stub Generation

```
stubgen -p strict_mock -o .
```

## Versions
### 0.5.0 
   Initial Release
### 0.5.1
   Removed requirement for pytest
