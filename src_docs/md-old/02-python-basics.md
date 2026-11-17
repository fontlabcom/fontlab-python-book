---
this_file: src_docs/md/02-python-basics.md
---

# 2. Python basics for a small report

Before a script can report on a font, it needs to hold data, choose what to include and repeat an operation. You can learn those parts with a few names typed into Python. The examples here use fictional glyph-name data: strings such as `"A"` and `"space"`. They do not read a font, create glyphs or change FontLab's selection.

Read [Fonts, FontLab and Python](01-fonts-fontlab-and-python.md) first. Each code block below is a complete, separate example, followed by its expected output. Each has been checked in Python 3.11 outside FontLab. To try one in FontLab's Scripting panel, follow the first chapter's procedure for preserving existing work and starting an empty script; enter only that example's code. Native panel testing remains pending.

This chapter is a provisional introduction. Its coverage and place in the complete book remain subject to the pending semantic map and editorial review.

## Values have types

A **value** is a piece of data. Its **type** determines which operations Python supports for it. Text, numbers and yes-or-no results have different uses:

| Example | Type | Meaning |
| --- | --- | --- |
| `"A"` | `str` | A string containing text |
| `3` | `int` | An integer |
| `1.25` | `float` | A floating-point number |
| `True` or `False` | `bool` | A Boolean value |
| `None` | `NoneType` | A value often used to represent absence |

The quotation marks matter. `"3"` is text, while `3` is a number. Adding two integers performs arithmetic; adding two strings joins their text. [Python tutorial: Numbers and text](https://docs.python.org/3.11/tutorial/introduction.html).

```python
print(3 + 2)
print("3" + "2")
```

```text
5
32
```

`None`, zero and an empty string are distinct values. In a later font-reading script, “no font was found” and “a font contains zero glyphs” would require different explanations. The API's documented result determines how you recognize those states; this chapter defines no such FontLab API contract. [Python reference: Built-in constants](https://docs.python.org/3.11/library/constants.html).

## Give a value a name

An **assignment** connects a name to a value. Python evaluates the right side of `=` and binds the name on the left to the result. Read `count = count + 1` as “calculate the old count plus one, then assign the result to count.” [Python reference: Assignment statements](https://docs.python.org/3.11/reference/simple_stmts.html#assignment-statements).

```python
count = 3
count = count + 1
print(count)
print(count == 4)
```

```text
4
True
```

The single `=` assigns. The double `==` compares values and produces a Boolean result. Names are case-sensitive: `count` and `Count` are different names. Choose a name that explains the data it refers to, such as `glyph_names`, rather than making the reader work out what `x` means.

## Keep related values together

A **list** holds an ordered collection. Square brackets create the list, and commas separate its items. `len` returns the number of items. An **index** identifies a position; the first item's index is zero. [Python reference: Built-in functions](https://docs.python.org/3.11/library/functions.html#len) and [sequence types](https://docs.python.org/3.11/library/stdtypes.html#sequence-types-list-tuple-range).

```python
glyph_names = ["A", "B", "space"]
print(len(glyph_names))
print(glyph_names[0])
```

```text
3
A
```

Here, `"space"` is a string of five letters used as a name. It is not a space character, and it is not a glyph object. Keeping those distinctions clear will matter when real font data enters your script.

A **dictionary** associates keys with values. Curly brackets create it; each colon connects a key with its value. Looking up a key retrieves the associated value:

```python
report = {"title": "Practice names", "count": 3}
print(report["title"])
print(report["count"])
```

```text
Practice names
3
```

The strings `"title"` and `"count"` are keys chosen for this example, not FontLab property names. Looking up an absent dictionary key raises `KeyError`; accessing a list item with an index outside its range raises `IndexError`. [Python reference: KeyError](https://docs.python.org/3.11/library/exceptions.html#KeyError) and [IndexError](https://docs.python.org/3.11/library/exceptions.html#IndexError).

### Two names can refer to one list

Assignment does not automatically copy a list. Both names below refer to the same list, so adding an item through `report_names` also changes what you see through `glyph_names`:

```python
glyph_names = ["A", "B"]
report_names = glyph_names
report_names.append("space")
print(glyph_names)
```

```text
['A', 'B', 'space']
```

`append` is a **method**, an operation accessed through an object. The dot in `report_names.append` selects that list's method. Use `glyph_names.copy()` when you need a separate list of these strings. That makes a shallow copy: nested objects, if present, would still be shared. [Python tutorial: Lists](https://docs.python.org/3.11/tutorial/datastructures.html#more-on-lists).

## Choose a path with a condition

An `if` statement runs its indented block when its condition is true. An `else` block covers the other case. The colons and indentation are part of Python's syntax; keep the four spaces shown here. [Python tutorial: if statements](https://docs.python.org/3.11/tutorial/controlflow.html#if-statements).

```python
glyph_names = []
if len(glyph_names) == 0:
    print("No names to report.")
else:
    print("Names are available.")
```

```text
No names to report.
```

The empty list `[]` is valid data. It contains no names to process. Change it to `["A"]` and the other message appears. You can also write `if glyph_names:` to test for a nonempty list; empty lists are false in a condition. This shorter form reverses which branch handles the empty case. [Python reference: Truth value testing](https://docs.python.org/3.11/library/stdtypes.html#truth-value-testing).

## Repeat an operation with a loop

A `for` loop takes each item from a collection in turn. On each pass, `name` refers to the next string. Only the indented line belongs to the loop, so the last message appears once. [Python tutorial: for statements](https://docs.python.org/3.11/tutorial/controlflow.html#for-statements).

```python
glyph_names = ["A", "B", "space"]
for name in glyph_names:
    print(name)
print("Report complete.")
```

```text
A
B
space
Report complete.
```

With an empty list, the indented line runs zero times; the final message still appears. An empty report and a report containing three names are both outcomes you can check. The loop itself makes no claim that its input represents the current FontLab selection.

## Give an operation a name with a function

A **function** groups an operation under a name. `def` defines it; a later call runs it. The **parameter** `names` receives the list supplied by the caller. `return` sends a result back, and `print` displays that result. [Python reference: Function definitions](https://docs.python.org/3.11/reference/compound_stmts.html#function-definitions).

```python
def count_names(names: list[str]) -> int:
    return len(names)


glyph_names = ["A", "B", "space"]
print(count_names(glyph_names))
print(count_names([]))
```

```text
3
0
```

`list[str]` and `-> int` are **type hints**: they describe the intended input and result. They do not enforce those types while the code runs. The parameter name belongs to the function's local scope; the caller can supply a list held under a different name. [Python reference: Type hints](https://docs.python.org/3.11/library/typing.html) and [function definitions](https://docs.python.org/3.11/reference/compound_stmts.html#function-definitions).

This function is deliberately small. It lets you follow an argument into a function and a result back out. In ordinary code, calling `len(glyph_names)` directly would do this particular job.

## Read and handle errors

A **syntax error** means Python cannot parse the code. For example, removing the colon after the `for` line makes that statement invalid. An **exception** occurs while code runs: valid syntax can still ask for an item that does not exist or a conversion that cannot succeed.

An unhandled exception normally ends that execution and produces a traceback. Read the exception type and message, then use the referenced line to locate the operation. A `NameError` can identify an undefined name; check spelling, capitalization and whether the assignment ran. [Python tutorial: Errors and exceptions](https://docs.python.org/3.11/tutorial/errors.html).

When you expect a particular failure and know how to respond, catch that exception explicitly. Here the conversion to an integer cannot accept `"three"`:

```python
count_text = "three"
try:
    count = int(count_text)
except ValueError:
    print("Enter an integer, such as 3.")
else:
    print(count)
```

```text
Enter an integer, such as 3.
```

The `except` block handles `ValueError` from the attempted conversion. The `else` block runs if the conversion succeeds. Change `"three"` to `"3"` to see that path. Conversion accepts negative integers too; a rule requiring a nonnegative count would need its own check. [Python reference: int](https://docs.python.org/3.11/library/functions.html#int).

Keep the failing operation close to its handler. Catching every error and continuing would hide mistakes this example cannot explain. Handling an exception also does not undo earlier changes. Before applying these ideas to real font edits, you will need the relevant API's rules for scope, updates and Undo, backed by native testing.

## Try a report of your own

Use the loop example as a starting point. Add `print(len(glyph_names))` before the loop. With the original data, the first line should be `3`, followed by the three names and the completion message. Replace the list with `[]`: the result should be `0` followed by the completion message.

This report still works entirely with local Python data. Connecting it to an open font is a separate step, requiring a verified way to obtain the intended glyph names.
