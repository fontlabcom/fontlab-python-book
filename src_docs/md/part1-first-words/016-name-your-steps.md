---
this_file: src_docs/md/part1-first-words/016-name-your-steps.md
---

# 16. Name your steps

The publisher has asked for an inventory of Plum: how many glyphs are empty, how many have no Unicode value, how many are small caps. Mira has a script for each of those questions. Late on Tuesday she pastes the three into one file, runs it, and gets the right answers.

Then she scrolls up to change the heading of the second list and can't find it. The script is thirty-one lines long and it looks like the same paragraph written three times. She changes a line, runs it, and the wrong list changes.

She sends the file to Oskar with one word: *Help.* The answer: "You've written one thing three times. Write it once and give it a name."

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- The long script below. Type it, or build it from `empty_glyphs.py` and `find_suffix.py`. Save it as `three_lists.py`. One spelling in it is new: `glyph.unicode is None` asks the same question as `== None` did in chapter 8. It's the usual way to write that test, and chapter 18 explains it.

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

font = fl.CurrentFont()

empty = []
for glyph in font.glyphs:
    if pGlyph(font, glyph).isEmpty():
        empty.append(glyph.name)
print("Empty")
print(len(empty), "of", len(font))
for name in empty:
    print("   ", name)

no_unicode = []
for glyph in font.glyphs:
    if glyph.unicode is None:
        no_unicode.append(glyph.name)
print("Without Unicode")
print(len(no_unicode), "of", len(font))
for name in no_unicode:
    print("   ", name)

small_caps = []
for glyph in font.glyphs:
    if glyph.name.endswith(".sc"):
        small_caps.append(glyph.name)
print("Small caps")
print(len(small_caps), "of", len(font))
for name in small_caps:
    print("   ", name)
```

Its output starts like this, and goes on for two more lists:

```text
Empty
4 of 208
    space
    a.sc
    b.sc
    c.sc
```

## Step 1: Give a step a name

Leave the long script for a moment and open a new, empty one. Type this:

```python
def greet():
    print("Good morning, Ines.")
    print("The report is on its way.")
```

Run it. Nothing is printed, and nothing is wrong.

`def` is short for "define". The line says: here's a step, and its name is `greet`. The indented lines under it are what the step consists of. Python reads them, remembers them under that name, and does not carry them out. You've written a recipe, and nobody has cooked from it yet.

To carry the step out, say its name with parentheses after it. Add two lines at the bottom, against the left edge:

```python
greet()
greet()
```

```text
Good morning, Ines.
The report is on its way.
Good morning, Ines.
The report is on its way.
```

Each `greet()` runs the two lines once. A named step like this is called a **function**, and using it is called **calling** it. You've been calling functions since chapter 2: `print()`, `len()`, `sorted()`. Somebody wrote those with `def`, the same way. Now you can add your own to the set.

The shape is one you know. A `def` line ends with a colon and the lines that belong to it are indented, as with `for` and `if`. The first line back at the left edge is outside the function.

## Step 2: A slot for what changes

The greeting is always for Ines. To greet somebody else, you'd need a second function, and that's the copying we're trying to stop. So give the function a slot. In chapter 2 you put things into the slot of `print`. Now you build one.

```python
def greet(name):
    print(f"Good morning, {name}.")


greet("Ines")
greet("Tomas")
```

```text
Good morning, Ines.
Good morning, Tomas.
```

The word in the parentheses of the `def` line is a box that belongs to the function. Each time you call the function, whatever you put through the slot lands in that box, and the lines inside use it. The first call puts `"Ines"` in `name` and the second puts `"Tomas"` there. The thing you pass through the slot is called an **argument**.

If the function has a slot, it wants it filled. Call it with nothing:

```python
greet()
```

```text
TypeError: greet() missing 1 required positional argument: 'name'
```

The message names the function, says how many arguments are missing and gives the name of the box that stayed empty.

A function can have several slots, separated by commas, and the arguments go in by position: the first argument into the first box, the second into the second.

## Step 3: Hand something back

`greet` does something: it prints. Most functions you'll write should answer something, so that the rest of the script can go on working with the answer. `len` doesn't print the count. It hands the count back, and you decide what to do with it.

The word for handing back is `return`.

```python
def half(number):
    return number / 2


print(half(596))
side = half(596) + 10
print(side)
```

```text
298.0
308.0
```

When Python reaches `return`, the function is over, and the value after the word travels back to the place where the function was called. You can read `half(596)` in the last lines as if `298.0` stood there. You can print it, put it in a box or do arithmetic with it.

Now the mistake, and it's one everybody makes. Delete the word `return` and leave the rest:

```python
def half(number):
    number / 2


print(half(596))
```

```text
None
```

There's no complaint. The function did the division and then dropped the result on the floor, because nobody told it to hand anything back. A function that reaches its end without a `return` hands back `None`, the nothing from chapter 5. When a function of yours gives you `None` and you expected a value, look for the missing `return` first.

## Step 4: Name the test

Back to `three_lists.py`. The longest line in it is the empty test, with its two pairs of parentheses. It's a step, and it can have a name:

```python
def is_empty(font, glyph):
    return pGlyph(font, glyph).isEmpty()
```

Two slots: the font and one glyph from it. The function asks the richer glyph the question and hands the answer back, `True` or `False`. Put these lines above the line `font = fl.CurrentFont()`, with an empty line or two around them, and change the first loop to use the new name:

```python
for glyph in font.glyphs:
    if is_empty(font, glyph):
        empty.append(glyph.name)
```

Run it. The output is the same. The script isn't shorter, but the `if` line now reads as a sentence, and the long line exists in one place only. If Part 2 gives you a better test for emptiness, you'll change it there and every script line that asks `is_empty` gets the better answer.

A function that answers yes or no usually gets a name that starts with `is_` or `has_`, so that the `if` line reads well.

## Step 5: Name the printing

Look at the three places where the script prints a list. They have the same three moves, a heading, a count and the names. Two things change from one to the next: the heading and the list. Each thing that changes becomes a slot.

```python
def report(title, names, total):
    print(title)
    print(len(names), "of", total)
    for name in names:
        print("   ", name)
```

The third slot is the size of the font. The function could reach out for the box `font` in the script around it, and it would work. But a function is easier to trust, and to carry to another script, when everything it needs comes in through its slots.

This function has no `return`, and that's fine. Its job is to print, like `greet`.

Now the twelve printing lines of the script shrink to three calls:

```python
report("Empty", empty, len(font))
report("Without Unicode", no_unicode, len(font))
report("Small caps", small_caps, len(font))
```

To change how every list looks, Mira changes one function. To change one heading, she changes one word in a line that has nothing else in it.

## Step 6: One loop, three lists

One more repair. The script walks through the font three times, once per list. One walk is enough: a glyph can be asked all three questions in the same turn of the loop. Here's the whole script. Save it as `three_lists.py`, over the old one.

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph


def is_empty(font, glyph):
    return pGlyph(font, glyph).isEmpty()


def report(title, names, total):
    print(title)
    print(len(names), "of", total)
    for name in names:
        print("   ", name)


font = fl.CurrentFont()

empty = []
no_unicode = []
small_caps = []
for glyph in font.glyphs:
    if is_empty(font, glyph):
        empty.append(glyph.name)
    if glyph.unicode is None:
        no_unicode.append(glyph.name)
    if glyph.name.endswith(".sc"):
        small_caps.append(glyph.name)

report("Empty", empty, len(font))
report("Without Unicode", no_unicode, len(font))
report("Small caps", small_caps, len(font))
```

Count the lines and you'll find it's as long as the script you started with. The gain is that you can read it. The bottom third says what the script does. The top third says how each step works, for the day you need to know.

The three `if` lines are separate questions, not `if`, `elif`, `elif` from chapter 13. A glyph like `a.sc` belongs in all three lists, and `elif` would stop asking after the first yes.

The order of the parts matters. Python reads a script from the top, and it has to have read a `def` before the line that calls it. Move the three `report` lines above the `def report` line and you get:

```text
NameError: name 'report' is not defined. Did you mean: 'repr'?
```

It's the complaint from chapter 3: Python doesn't know the name yet. So the custom is imports first, then the functions, then the work.

??? info "Going deeper: boxes inside a function"
    A box you make inside a function lives only while the function runs. If `is_empty` made a box called `rich`, the rest of the script couldn't see it: asking for `rich` afterwards gives a `NameError`. That's a feature. It means two functions can each have a box called `name` or `count` without disturbing each other, and that you can read a function without wondering what the rest of the script does to its boxes. The slots are the way in, and `return` is the way out.

## What you learned

`def name(slots):` teaches Python a step and gives it a name; the indented lines run only when you call the function with `name(...)`. The values you pass go into the function's own boxes by position, and `return` hands a value back to the caller, while a function without `return` hands back `None`. A script made of small named functions, defined above the work that calls them, says what it does in its last few lines.

## Try it yourself

1. Write `has_unicode(glyph)` that returns `True` when the glyph has a Unicode value. Use it in the loop, with `not` from chapter 13, to fill the `no_unicode` list.
2. Add a fourth list to `three_lists.py`: glyphs wider than 800 units. You need one new list, one new `if` and one new `report` line. The count should be 11.
3. Change `report` so that it prints the names on one line, separated by spaces, when there are fewer than six of them, and one per line otherwise. Only the function changes. Start with an empty string and add each name to it. Check that all four lists follow.

## Next

Chapter 17 is about the reader of your script a week from now, and what you can leave in the file for her.
