# Coding Style Guides

Follow [Pep 8](https://peps.python.org/pep-0008/)

## Imports

Use isort with no flags

## Sort Everything in __all__

All values in __all__ need to be in alphabetical order, case-sensitive.

## Flake8

Run flake8 with the following commands:

```
max-line-length = 120
ignore = F405
```

These flags are setup in tox.ini

## Mypy

Run mypy with the following flags:

```
check_untyped_defs = true
```

This flag is set up in pyproject.toml

## Do not use multiline single lines

Do not reformat a single line if the only thing the reformatting does is place parenthesis or square brackets onto
separate lines. All this does is triple the line count and does not actually improve readability.

Wrong:

```
results.append(
    ParamDefault(p.name, p.type, p.default, p.kind, index=p.index)
)
```

Correct:

```
results.append(ParamDefault(p.name, p.type, p.default, p.kind, index=p.index))
```

## List / Array

The opening square bracket must be on the first line. If the entire list is able to be on one line without exceeding the
maximum line length, the list may be formatted that way, though it is not required to be formatted in that manner. If it
is formatted as a single line, then the closing square bracket must be on that line as well.

If the list is split across multiple lines, then each line contains one entry per line. The closing square bracket must
then be on its own line, and match the indent of the first line.

These rule also apply for a list appearing as a function parameter.

Correct (for lines under maximum length):

```
values = [value1, value2]
```

Correct:

```
values = [
    value1,
    value2,
    ...
]
```

## Keep Single and Double Quotes Consistent
Prefer double quotes over single quotes.  Single quotes may be used if the string contains double quotes.  

However, if a single string is broken across multiple lines, make sure to use the same quote type in every line.
For example, since the 5th and 6th line contains double quotes internally, single quotes are used on those lines.
This results in the first four lines also using single quotes. 

```
expected = (
    'StrictMock: NoExpected Discrepancies\n'
        'Data Length\n'
        '    expected: 0\n'
        '    actual  : 1\n'
        'Extra          0: Actual("method_called")\n'
        '                      fix: Expected("method_called")\n\n'
)
```
