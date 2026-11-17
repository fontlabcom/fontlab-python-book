---
this_file: src_docs/md/part1-first-words/009-strings-are-made-of-letters.md
---

# 9. Strings are made of letters

Wednesday. Ines stops at Mira's desk with her coat still on.

"The small caps. How many are in the font so far?"

"Three," says Mira. She knows because she made them yesterday.

"And next month, when there are sixty, and some figures with a `.tf` on the end, and whatever else the publisher thinks of?"

Mira looks at Oskar's sheet. Line 9: *When the small caps come: list every glyph whose name ends in `.sc`.* He saw this coming.

Yesterday's loop picked glyphs by a number: wider than 800, exactly 708. Today it picks them by their names. A glyph name looks like one solid thing, but Python sees it as a row of characters, and it can check how the row starts, how it ends and what's in the middle.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open. It should have 208 glyphs, with the three small caps from [chapter 8](008-only-the-ones-i-want.md).
- Nothing else. Today's script starts from an empty Scripting panel.

## Step 1: Ask a name how it ends

No font yet. Type this and run it:

```python
name = "a.sc"
print(name.endswith(".sc"))
```

```text
True
```

Then change the first line to `name = "Aacute"` and run it again.

```text
False
```

You put a string in a box called `name` and asked it a question: do you end with `.sc`? The answer is one of the two values from yesterday, `True` or `False`.

Look at how the question is written. `name`, a dot, `endswith`, and then a slot with a string in it. You know the dot from [chapter 6](006-ask-a-glyph-its-name.md): it opens a drawer of the thing on its left. A glyph has drawers called `name` and `width`. It turns out a string has drawers too, and `endswith` is one of them. Like `isEmpty()` yesterday, it's a question the string works out when you ask, so it ends in parentheses. This time something goes through the slot: the ending you're asking about.

The whole word is lowercase. Type it with a capital W and see what happens:

```python
name = "a.sc"
print(name.endsWith(".sc"))
```

```text
Traceback (most recent call last):
  File "<string>", line 2, in <module>
AttributeError: 'str' object has no attribute 'endsWith'. Did you mean: 'endswith'?
```

You met `AttributeError` in chapter 6, when you asked for a drawer that wasn't there. Same thing here. `'str' object` is Python's way of saying "a string", and a string has no drawer called `endsWith`. Python is fussy about capitals everywhere, in the names it gives things as much as in the names you give things. Put the small w back.

## Step 2: Find the small caps

A glyph's name is a string. So everything you can ask `"a.sc"`, you can ask `glyph.name`:

```python
from fly import fl

font = fl.CurrentFont()
count = 0
for glyph in font.glyphs:
    if glyph.name.endswith(".sc"):
        print(glyph.name)
        count = count + 1
print("Small caps:", count)
```

```text
a.sc
b.sc
c.sc
Small caps: 3
```

Read the `if` line from left to right, one dot at a time. `glyph` is the glyph the loop is holding. `.name` opens its name drawer and takes out a string. `.endswith(".sc")` asks that string a question. Two dots, two drawers, one inside the other. The answer goes to `if`, and `if` decides whether the two lines below it run.

Save this as `find_suffix.py` in your `scripting-book` folder.

Why `".sc"` with the dot, and not `"sc"`? Try the shorter one on a name you make up:

```python
print("disc".endswith("sc"))
print("disc".endswith(".sc"))
```

```text
True
False
```

Plum has no glyph called `disc`, but some font will. The dot is part of the convention, so the dot belongs in the test. When you write a test, think about what else might pass it.

That last listing also shows you something new: you don't need a box. A string in quotes can be asked directly. `"disc".endswith("sc")` works for the same reason `name.endswith("sc")` works. The box only holds the string. The string answers.

## Step 3: Ask how it starts

The opposite question is spelled `startswith`. Plum has a family of quotation marks, and their names all begin the same way. Change the `if` line in your script and the text in the last line:

```python
from fly import fl

font = fl.CurrentFont()
count = 0
for glyph in font.glyphs:
    if glyph.name.startswith("quote"):
        print(glyph.name)
        count = count + 1
print("Quotes:", count)
```

```text
quotedbl
quotesingle
quotedblbase
quotedblleft
quotedblright
quoteleft
quoteright
Quotes: 7
```

Seven quotation marks, found by their first five letters. If Mira wants to check that all of them sit at the same height, that's her list.

Now a test that goes wrong in an instructive way. Which glyphs are versions of the lowercase *a*? Change `"quote"` to `"a"` and run it. You get sixteen names, and they start out well: `a`, `aacute`, `abreve`, `acircumflex`. Then, further down:

```text
ae
asterisk
asciitilde
ampersand
asciicircum
at
acute
a.sc
```

An asterisk is not a version of the letter *a*. Its name happens to begin with one. Python did what you said, and what you said was "starts with a". The test is too loose for the question you had in mind. There's no error message for that. The only protection is to read the list the first time you run a new test, before you trust the count. Chapter 13 gives you ways to tighten a test like this one.

## Step 4: Ask what's inside

Sometimes the interesting part of a name is in the middle or could be anywhere. For that, Python has a short word: `in`.

```python
print("acute" in "Aacute")
print("Acute" in "Aacute")
```

```text
True
False
```

`in` isn't a drawer. It stands between two strings, like `>` stands between two numbers, and it asks: does the row of characters on the left appear somewhere in the row on the right? The second line says `False` because of the capital A. `Aacute` contains `acute` but not `Acute`.

You've seen the word `in` before, in `for glyph in font.glyphs:`. There it's part of the loop's grammar. After `if`, or between two values, it's a question. Same word, two jobs, and Python tells them apart by what comes before.

Put it in the loop:

```python
from fly import fl

font = fl.CurrentFont()
count = 0
for glyph in font.glyphs:
    if "acute" in glyph.name:
        print(glyph.name)
        count = count + 1
print("With acute:", count)
```

```text
Aacute
Eacute
Iacute
Oacute
Uacute
Wacute
Yacute
aacute
eacute
iacute
oacute
uacute
wacute
yacute
acute
With acute: 15
```

Seven capitals, seven lowercase letters and, at the bottom, the accent itself. That last one is the `acute` glyph: the bare accent that the other fourteen borrow. If you're collecting "letters with an acute", it doesn't belong. If you're collecting "everything that changes when I redraw the acute", it's the most important line. The test is the same. Whether the answer is right depends on the chore.

One more use of `in`. Which glyphs have a dot anywhere in their name?

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if "." in glyph.name:
        print(glyph.name)
```

```text
.notdef
a.sc
b.sc
c.sc
```

The three small caps, and `.notdef`, whose name starts with a dot. Keep that odd one in mind for the next step.

## Step 5: Take a name apart

A name like `a.sc` has two parts with different meanings. The part before the dot says which letter. The part after says which version. To work with them separately, cut the string at the dot:

```python
name = "a.sc"
parts = name.split(".")
print(parts)
```

```text
['a', 'sc']
```

`split` cuts a string wherever it finds the thing you passed through the slot, throws the cutting marks away, and hands back the pieces as a list. You know lists from [chapter 5](005-a-font-is-a-list-of-glyphs.md): square brackets, things in a row, counted from zero. So the base name is piece number 0 and the suffix is piece number 1:

```python
name = "a.sc"
parts = name.split(".")
print(parts[0])
print(parts[1])
```

```text
a
sc
```

What does `split` do with a name that has no dot?

```python
print("Aacute".split("."))
print(len("Aacute".split(".")))
```

```text
['Aacute']
1
```

A list with one piece: the whole name. Nothing to cut, so nothing was cut. That gives you a second way to recognize a suffixed name: split it, and count the pieces with `len`. More than one piece means there was a dot.

Now the odd one:

```python
print(".notdef".split("."))
```

```text
['', 'notdef']
```

Two pieces, and the first is `''`, a string with nothing between its quotes. The dot was at the very start, so the piece before it is empty. `.notdef` isn't a letter with a suffix. It's a special name that begins with a dot, and a script that treats it as "base name, then suffix" gets an empty base. You'll deal with it in step 6.

## Step 6: Print the base and the suffix

Put the pieces together. For every glyph with a suffix, print the suffix first, then the letter it belongs to:

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    parts = glyph.name.split(".")
    if len(parts) > 1:
        print(parts[1], parts[0], glyph.name)
```

```text
notdef  .notdef
sc a a.sc
sc b b.sc
sc c c.sc
```

There's `.notdef` in the first line, with its empty base name showing as a gap. To leave it out, the test has to be stricter. You could count the pieces and also check the base, but you can't join two tests yet. So use a test that fails for `.notdef` in the first place: go back to `endswith`.

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if glyph.name.endswith(".sc"):
        parts = glyph.name.split(".")
        print(parts[0], "is the base of", glyph.name)
```

```text
a is the base of a.sc
b is the base of b.sc
c is the base of c.sc
```

The order of the lines matters here. The `if` comes first and lets only the small caps through. The `split` happens inside it, so it only ever cuts names that passed the test.

Mira runs `find_suffix.py` once more and tells Ines: three. Then she puts a pencil dot next to line 9 on Oskar's sheet. She won't cross it out while the list is three glyphs long. But the script is ready for sixty.

??? info "Going deeper: a string is a row you can count and pick from"
    `len("Aacute")` gives 6, the number of characters. `"Aacute"[0]` gives `A`, the first one. Counting and picking work on strings the way they work on lists. In the exercises of chapter 7 you walked through a string with a `for` loop for the same reason: to Python, a string is a row of characters in order.

## What you learned

A string can answer questions about itself: `endswith` and `startswith` check its two ends, and `in` checks whether a shorter string appears anywhere inside it. All three give `True` or `False`, so they fit after `if`. `split` cuts a string into a list of pieces, which is how you separate a base name from its suffix. A test on names does what you spell and not what you mean, so read the list it produces before you rely on it.

## Try it yourself

1. Change `find_suffix.py` so it lists the glyphs whose names end with `grave`. You should get fifteen. Which one of them isn't a letter?
2. List every glyph with `tilde` anywhere in its name. There are eight. One of them is neither a letter with a tilde nor the tilde accent. What is it?
3. Glyph names with exactly one character are the plain letters. Write a loop that counts the glyphs where `len(glyph.name) == 1`. How many do you expect before you run it?

## Next

Chapter 10 keeps what the loop finds. So far the names scroll past in the Output panel and are gone. With a list of your own, you can collect them, count them, sort them and take the first ten.
