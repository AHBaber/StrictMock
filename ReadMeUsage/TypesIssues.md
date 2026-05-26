## Type Issues

Python was originally designed so that beginners did not have to worry about types. Instead, they could simply place a
value into a variable and then use that variable. As time has gone on, people have found that using clearly defined
types and checking those types vastly improve code reliability. And, as such, several people have done a lot of work
adding typing to Python, as well as a lot of tools that use and check the typing.

Alas, as oft is the case, bolting on a feature afterwards means that feature may have issues. So, I have done a lot of
work in StrictMock to verify that actual types are the same as the expected types. And I have run into several road
blocks.

### Checking Types

As part of StrictMock, I built it to verify that the type that appears in Expected() matches the actual type used. And
if they do not match, an error is raised. But of course, there are complications.

### How Types are Identified

One of the standard ways to get a signature of a function or method is to use ```inspect.signature()```. However, there
is a surprise when making this call, it may return the type info as a string. Furthermore, if the type is a union or
optional, the string will contain a list of type names separated by vertical bars.

```
"TypeName"               # equivelant to TypeName
"TypeName1 | TypeName2"  # equivelant to Union[TypeName1, TypeName2]
"TypeName | None"        # equivelant to Optional[TypeName]
```

So, we need to be able to handle not just types, but strings that identify types as well.

### Evaluating Types

Each StrictMock will try to load all types that are present where it is being used.

In some cases, a type will not be evaluated correctly when being checked. Part of the issue is that since the code using
```eval()``` resides in a different file than the unit test. Each StrictMock instance will try to load all types present
in the unit test where it is being used. If this fails for some reason, then the work around to this is that use
```ImportedTypes``` as outlined in [Args](Args.md)

Note 1: if you use ```ImportedTypes```, then the auto load of types will be skipped.

Note 2: if a type is missing, the error will tell you the name of the type it was trying to find, and provide the code
fix needed to resolve the issue.

### Limitations

Currently, if two different libraries define the same class name, and use strings as type identifiers, then there may be
an unresolvable conflict. This is due to the fact that the string will type needs to be evaluated to be turned into an
actual type.

```IValueEqual``` may be (ab)used to remedy this issue. Doing so should be considered a code smell.

## Security

When evaluating strings, a regex is used to verify that the string only contains the characters that are allowed to
appear in type names.
