---
this_file: src_docs/md/part2-a-toolbox/037-comprehensions.md
---

# 37. One line that builds a list

Monday of the seventh week. Mira is reading one of Oskar's old scripts in the `chores` folder, to see how he exported the kerning, and she gets stuck on the third line:

```python
wide = [glyph.name for glyph in font.glyphs if glyph.width > 800]
```

She can read every word in it. There's a `for`, an `in`, an `if`. But they're inside square brackets, in an order she's never seen, with no colons and no indents. She messages Oskar: *Is this a typo?*

He answers within the minute. *No. It's the four lines you'd write, folded into one. Unfold it and you'll see.*

Oskar's scripts are full of lines like that one, and so are the scripts you'll find on the web. You need to be able to read them, and after today you'll write a few yourself. I'll also show you where I think they stop being a good idea.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- The functions from chapters 33 to 36: `is_empty`, `glyphs_of` and `wider_than`. Where a listing needs one, it's shown.

Every listing in this chapter starts with the usual two lines:

```python
from fly import fl

font = fl.CurrentFont()
```

## Step 1: The loop you've written forty times

Here's the pattern from chapter 10, the one for building a list:

```python
names = []
for glyph in font.glyphs:
    names.append(glyph.name)

print(names[:6])
```

```text
['.notdef', 'A', 'Aacute', 'Abreve', 'Acircumflex', 'Adieresis']
```

Make an empty list. Walk through something. Each time around, work out one value and append it. You've written those three lines in nearly every chapter since, and your scripts from the last few chapters have them three times over.

When people write the same three lines often enough, the language grows a shorter way to say them. This is it:

```python
names = [glyph.name for glyph in font.glyphs]

print(names[:6])
```

```text
['.notdef', 'A', 'Aacute', 'Abreve', 'Acircumflex', 'Adieresis']
```

It's the same list. The square brackets say "this makes a list", as they always have. Inside them, read from the middle outward: `for glyph in font.glyphs` is the loop line you know, minus its colon, and `glyph.name` in front of it is what goes into the list each time around.

It's called a **list comprehension**. The name isn't a helpful one. Read the line aloud as "the name of each glyph in the font", which is close to how you'd say it to Ines.

The part in front can be anything that produces a value, as the argument to `append` could:

```python
widths = [int(glyph.width) for glyph in font.glyphs]
small_caps = [name + ".sc" for name in ["a", "b", "c"]]

print(widths[:6])
print(small_caps)
```

```text
[500, 596, 596, 596, 596, 596]
['a.sc', 'b.sc', 'c.sc']
```

## Step 2: Only some of them

The other half of the pattern is the filter from chapter 8, a loop with an `if` inside:

```python
wide = []
for glyph in font.glyphs:
    if glyph.width > 800:
        wide.append(glyph.name)
```

Folded up, the `if` goes at the end:

```python
wide = [glyph.name for glyph in font.glyphs if glyph.width > 800]

print(wide)
```

```text
['AE', 'M', 'OE', 'W', 'Wacute', 'Wcircumflex', 'Wdieresis', 'Wgrave', 'oe', 'emdash', 'at']
```

That's Oskar's line. Put the two versions side by side and you can see where each piece went:

| In the loop | In the comprehension |
|---|---|
| `wide = []` and `wide.append(...)` | the square brackets |
| `for glyph in font.glyphs:` | `for glyph in font.glyphs`, in the middle |
| `if glyph.width > 800:` | `if glyph.width > 800`, at the end |
| `glyph.name` | `glyph.name`, at the front |

So the order is: what you want, where it comes from, which ones. "The name of each glyph in the font, if it's wider than 800." The loop says the same things in the order a machine does them. The comprehension says them closer to the way you'd say the sentence.

When you meet one in somebody's script and can't read it, do what Oskar said. Unfold it into the four lines, in your head or on paper.

## Step 3: The if in the wrong place

Here's the mistake. It's the natural place to put the `if`. In the sentence I wrote a moment ago, the "if" comes last. It's tempting to put it where it sits in the loop, right after the thing it guards:

```python
wide = [glyph.name if glyph.width > 800 for glyph in font.glyphs]
```

```text
SyntaxError: expected 'else' after 'if' expression
```

Python doesn't say "the `if` is in the wrong place". It says it expected an `else`, which is a strange thing to want. The message makes sense once you know there are two different `if`s that can appear in a comprehension, and you've only met one.

The `if` at the end is a filter. It decides whether a glyph gets into the list at all.

An `if` at the front is something else, and it must have an `else`. It doesn't filter. Every glyph gets in, and the `if` chooses which of two values goes in for it:

```python
notes = ["wide" if glyph.width > 800 else "ok" for glyph in font.glyphs]

print(notes[:4])
print(len(notes))
```

```text
['ok', 'ok', 'ok', 'ok']
205
```

That list has one entry for every glyph in the font, `"wide"` or `"ok"`. My 205 is the count of Plum as it came in chapter 4, and so are the totals in the next step. Your practice font has grown since, so your counts run a little higher: 213 if you've followed every step. The piece `"wide" if glyph.width > 800 else "ok"` is a value with a choice built in: this, if the test is true, or else that. It works outside comprehensions too, anywhere a value can go.

So when you see that error, you put a filter at the front. Move it to the end.

## Step 4: Hand it straight on

Often you build a list only to hand it to something. There's no need to give it a name first:

```python
print(len([glyph for glyph in font.glyphs if glyph.width > 800]))
print(sum([int(glyph.width) for glyph in font.glyphs]))
print(max([len(glyph.name) for glyph in font.glyphs]))
```

```text
11
102107
14
```

Eleven glyphs are wider than 800. `sum` adds up a list of numbers, and here it gives the total of all the widths, the figure from exercise 2 of chapter 28. The longest glyph name has 14 characters. Your total will be larger than mine if the glyphs you've added have widths.

Each of those took you three or four lines in Part 1. That's the real gain: a question you can ask in one line is a question you'll ask more often. You can type a line like these into the Scripting panel, run it, read the answer and delete it, the way you'd use a calculator.

A comprehension is also a natural thing to hand to `sorted`:

```python
print(sorted([glyph.name for glyph in font.glyphs if glyph.name.endswith("acute")])[:5])
```

```text
['Aacute', 'Eacute', 'Iacute', 'Oacute', 'Uacute']
```

Read it from the inside out, as you read nested parentheses in arithmetic: the names that end in `acute`, sorted, and then the first five.

## Step 5: Dictionaries and sets fold too

The same fold works for the other two containers. With curly brackets and a colon, it builds a dictionary:

```python
width_of = {glyph.name: int(glyph.width) for glyph in font.glyphs}

print(width_of["A"], width_of["emdash"])
```

```text
596 1000
```

That's the lookup dictionary from chapter 21 in one line. Before the `for` there's a key, a colon and a value, the same three things you'd write inside `{}` by hand.

With curly brackets and no colon, it builds a set:

```python
distinct = {int(glyph.width) for glyph in font.glyphs}

print(len(distinct))
print(sorted(distinct)[:6])
```

```text
84
[190, 212, 217, 222, 224, 228]
```

A set keeps one of each, as chapter 25 showed, so this answers a question a spacer does ask: how many different advance widths does the font have? The untouched Plum has 84 in its Regular master, and the six narrowest start at 190. Your practice glyphs may add one or two. A font with a tidy rhythm has few. If that number were 180 for 205 glyphs, somebody had been nudging widths one at a time.

Curly brackets mean a dictionary or a set, depending on whether there's a colon, and that's the same rule as in chapters 21 and 25.

## Step 6: When to unfold it again

Now the other side. Here's `metrics_rows` from chapter 35, as a loop:

```python
def metrics_rows(font, only_selected=False):
    rows = []
    for glyph in glyphs_of(font, only_selected):
        if not is_empty(font, glyph):
            measured = pGlyph(font, glyph)
            rows.append((glyph.name, measured.getLSB(), int(glyph.width), measured.getRSB()))
    return rows
```

And here it is as a comprehension:

```python
def metrics_rows(font, only_selected=False):
    return [(glyph.name, pGlyph(font, glyph).getLSB(), int(glyph.width), pGlyph(font, glyph).getRSB()) for glyph in glyphs_of(font, only_selected) if not is_empty(font, glyph)]
```

It works. It's also 170 characters long, you have to scroll sideways to find the `for`, and it makes the `pGlyph` twice for every row because there's nowhere to keep it. The loop had a box called `measured` for that. Nobody will thank you for the second version, and that includes you, in a month.

My rule is this. Use a comprehension when you can say it in one breath: "the name of each glyph that's wider than 800". Use a loop when:

- the line won't fit on the screen without scrolling;
- you need a box in the middle to hold something you'll use twice;
- there's more than one `if`, or an `if` with an `else` and a filter as well;
- the loop does something, as opposed to building something.

A comprehension is for making a list. It isn't for marking glyphs red or renaming them or printing. You can write `[print(glyph.name) for glyph in font.glyphs]`, and it will print, and it will also build a list of `None`s, one for each glyph, and throw it away. A line that changes the font should look like one. A `for` loop with an indented body does, and a pair of square brackets doesn't.

`wider_than` passes the test:

```python
def wider_than(font, limit=700, only_selected=False):
    return [g.name for g in glyphs_of(font, only_selected) if g.width > limit]
```

Five lines became one, and you can read it aloud. The short name `g` is fine in a comprehension, because it lives and dies within the line. In a loop with ten lines in its body, I'd spell it out.

## The whole script

This is `empty_glyphs.py` from chapter 8, rewritten with today's tool and the `is_empty` function from chapter 33:

```python
# Lists the glyphs that have no shapes in them.
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph


def is_empty(font, glyph):
    return pGlyph(font, glyph).isEmpty()


font = fl.CurrentFont()

empty = [g.name for g in font.glyphs if is_empty(font, g)]

print(len(empty), "of", len(font), "glyphs are empty:")
print(" ".join(empty))
```

```text
9 of 213 glyphs are empty:
space a.sc b.sc c.sc a.ss01 ampersand.ss01 g.ss01 y.ss01 zero.alt
```

Yours will list whichever practice glyphs you've added and not yet drawn. In chapter 8 this script was a loop with a counter and a `print` inside it. Now it has three parts that each say one thing: find the font, build the list, report. The comprehension holds the question, and the lines after it decide what to do with the answer. Scripts tend to settle into that shape once comprehensions are available.

And two functions from chapter 34 get shorter. Paste these over the old versions wherever you use them:

```python
import fly.ap.core.scripting as scripting


def glyphs_of(font, only_selected=False):
    if not only_selected:
        return font.glyphs
    return [font[name] for name in scripting.names_selected_names()]


def wider_than(font, limit=700, only_selected=False):
    return [g.name for g in glyphs_of(font, only_selected) if g.width > limit]
```

`metrics_rows` and `status_tally` stay as loops. Put the new `glyphs_of` into `widest_first.py` from last week, run it, and check that its output hasn't changed by a character. That's the test from chapter 33 again: if you rewrote a function without changing what it does, its callers can't tell.

Mira goes back to Oskar's kerning script. The third line reads like a sentence now. The fourth line has two `for`s in one pair of brackets. She unfolds it on paper, as he told her to, and gets through it.

## What you learned

A list comprehension folds the make-a-list loop into one line: what you want, then where it comes from, then an optional `if` that filters. An `if` at the front needs an `else` and picks between two values without filtering. Curly brackets make a dictionary or a set the same way. Use a comprehension to build something you can describe in one breath, and go back to a loop when the line gets long, needs a box in the middle or changes the font.

## Try it yourself

1. Write each of these as one line, and check the count against a loop you trust: the names of all glyphs with no Unicode value; the widths of all glyphs whose names start with a capital letter (the test is in chapter 13); a set of all the marks used in the font, which is the listing from chapter 32 in a single line.
2. Unfold this line of Oskar's into a loop, then say in words what `pairs` holds:

    ```python
    pairs = [(name, name + ".sc") for name in names if name + ".sc" not in font_names]
    ```

3. `status_tally` from chapter 33 builds a dictionary with a loop. Try to write it as a dictionary comprehension. You'll find that you can't, at least not with what you know. Say why. What does the loop do on each pass that a comprehension has no way to do?

## Next

Mira's scripts now call her own functions, which call Fly, which calls FontLab. When something breaks, the error message runs to eight lines and names more than one file. Chapter 38 reads one from end to end.
