---
this_file: src_docs/md/part2-a-toolbox/034-arguments-with-defaults.md
---

# 34. Arguments you can leave out

Wednesday. Mira is spacing the capitals, and she has `A`, `H`, `M` and `W` selected in the Font window. She wants to know which of those four is the widest. She has a function for the widest glyph. It tells her `emdash`, as it does every time, because it looks at the whole font and the em dash is the widest thing in it.

She could write a second function, `widest_selected_glyph`, with the same loop and one line changed. Then a third for "widest glyph that's wider than some number", and by Friday she'd be pasting six functions into every script that all do nearly the same thing.

What she wants is one function with a knob on it. Most days the knob stays where it is and she doesn't think about it. Now and then she turns it.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- An empty window in the Scripting panel. Today's functions and the calls that test them all go in that one script. Save it as `widest.py` so you can come back to it. Each new call goes at the bottom, below the functions.
- The selection helper, `names_selected_names`, from [chapter 15](../part1-first-words/015-the-selection.md).

## Step 1: A slot with something already in it

You've thought of a function's parentheses as slots since chapter 16. `widest_glyph(font)` has one slot, and you must fill it. A slot can also come with a value already in it. You write the value into the `def` line, after an equals sign:

```python
from fly import fl


def wider_than(font, limit=700):
    names = []
    for glyph in font.glyphs:
        if glyph.width > limit:
            names.append(glyph.name)
    return names
```

Call it two ways, below the function:

```python
font = fl.CurrentFont()
print(len(wider_than(font)))
print(len(wider_than(font, 800)))
```

```text
22
11
```

The first call fills one slot and leaves the second alone. Python uses the value that was already there, 700, and finds 22 glyphs wider than that. The second call fills both, and 800 takes the place of 700 for that one call. The 700 isn't gone. The next call that leaves the slot empty gets it again.

The value in the `def` line is called a **default**. It's what the function uses when you don't say otherwise.

A good default is the answer you'd give nine times in ten. In chapter 17 the limit lived in a constant, `LIMIT = 700`, and that was right for a single script. In a function that several scripts use, a default is better: every call gets 700 without asking, and the one script that needs 800 can say so without changing anything for the others.

## Step 2: Say the name

Look at this call as a stranger would:

```python
wider_than(font, 800)
```

What is 800? You know today, because you wrote the function ten minutes ago. Python lets you say which slot you're filling, by name:

```python
wider_than(font, limit=800)
```

It does the same thing, and it explains itself. You've already written calls like this. `open(path, "w", newline="")` in chapter 28 and `history.commit(..., operation="geometry", facts=facts)` in chapter 29 both fill slots by name. I asked you to copy them then, and now you can see how they work.

So there are two ways to fill a slot. By position: the first value goes in the first slot, the second in the second. Or by name: `limit=800` goes in the slot called `limit`, wherever it sits in the line. The habit I'd recommend is the one those two calls follow. Fill the one or two obvious slots by position and name the rest.

If you get the name wrong, Python tells you at once:

```python
wider_than(font, limt=800)
```

```text
TypeError: wider_than() got an unexpected keyword argument 'limt'
```

"Keyword argument" is Python's term for a slot filled by name. The message says there's no slot called `limt`. Compare that with chapter 14, where a misspelled drawer name on the left of `=` was accepted in silence. A misspelled slot name is refused.

## Step 3: A yes-or-no knob

Now Mira's problem. The knob she wants has two positions: the whole font, or only what's selected. That's a `True` or `False`, like the switch in chapter 31, except that it sits in a slot. Here's `widest_glyph` from chapter 33 with the knob added. Replace the old one in your script with it:

```python
import fly.ap.core.scripting as scripting


def widest_glyph(font, only_selected=False):
    if only_selected:
        glyphs = []
        for name in scripting.names_selected_names():
            glyphs.append(font[name])
    else:
        glyphs = font.glyphs

    widest = None
    for glyph in glyphs:
        if widest is None or glyph.width > widest.width:
            widest = glyph
    return widest
```

The import goes at the top of the script, below `from fly import fl`. Select `A`, `H`, `M` and `W` in the Font window and run:

```python
font = fl.CurrentFont()
print(widest_glyph(font).name)
print(widest_glyph(font, only_selected=True).name)
```

```text
emdash
W
```

The first half of the function decides which glyphs to look at. With the knob on, it builds a list from the selected names, as chapter 15 did. With the knob off, it takes all of them. Either way the result lands in a box called `glyphs`, and the second half of the function doesn't care which way it was filled. That's the trick to adding an option: branch once at the start to settle what you're working on, and write the real work once.

The default is `False`, so every call that already says `widest_glyph(font)` goes on working exactly as it did. Paste this version into `Friday Report.py` and its old call doesn't need to change. It doesn't know the knob exists. This is what makes defaults so useful: you can teach an old function something new without breaking the lines that call it.

The knob is named after the unusual behavior, so that `False` is the ordinary case and a call that says nothing gets the ordinary case. Chapter 31's switch worked the other way round, and for a reason: a switch that guards a change should default to safe, while an option on a report should default to ordinary.

## Step 4: When there's nothing to hand back

Two lines of that function changed for a reason I haven't given yet. The old version began with `widest = font[0]`: start with the first glyph and let the others challenge it. The new one begins with `widest = None`.

Click an empty spot in the Font window so that nothing is selected, and run the second call again:

```text
AttributeError: 'NoneType' object has no attribute 'name'
```

You met this message in chapter 19, where the font itself was missing. Here the font is fine. The selection is empty, so the list of glyphs is empty, so the loop never runs, so `widest` is still the `None` it started as, and the function hands that back. Then the calling line asks `None` for its name.

The function did the honest thing. Asked for the widest of no glyphs, it can't hand back the first glyph of the font, which is what the old opening line would have done. That would be a wrong answer that looks like a right one. `None` means "there isn't one", and it's the caller's job to ask:

```python
widest = widest_glyph(font, only_selected=True)
if widest is None:
    print("Select some glyphs first.")
else:
    print(widest.name, widest.width)
```

```text
Select some glyphs first.
```

`is None` is the test from chapter 19.

The line inside the loop needs the same care: `if widest is None or glyph.width > widest.width`. The first glyph the loop meets wins by default, because there's no champion yet. After that, a glyph has to be wider than the champion. The order of the two tests matters. Python reads an `or` from the left and stops as soon as one side is true, so when `widest` is `None` it never gets as far as asking `None` for a width.

## Step 5: The order of the slots

Now the mistake. Mira decides that `only_selected` is the more important slot and moves it to the front:

```python
def widest_glyph(only_selected=False, font):
```

Run the script, and none of it runs:

```text
SyntaxError: non-default argument follows default argument
```

A `SyntaxError` means Python couldn't read the script at all, so nothing in it runs until it's fixed, not even the lines above the mistake. The rule it's quoting: slots that must be filled come first, and slots with defaults come after them.

Think about why. Suppose Python allowed that line, and you called `widest_glyph(font)`. One value, two slots. Does the value go in the first slot, because it's first? Then `only_selected` holds a font and `font` holds nothing. Or should Python skip the first slot because it has a default? It would have to guess, and Python refuses to guess. With the required slots at the front, a call by position always fills them first and whatever's left over goes into the optional ones.

Put the line back as it was.

Two more messages belong to this family, and you'll see both sooner or later:

```python
widest_glyph()
widest_glyph(font, True, 800)
```

```text
TypeError: widest_glyph() missing 1 required positional argument: 'font'
TypeError: widest_glyph() takes from 1 to 2 positional arguments but 3 were given
```

The first says a slot without a default was left empty. The second says you brought more values than there are slots, and "from 1 to 2" is Python counting for you: one required, one optional.

## Step 6: Two knobs

A function can have several optional slots. Give `wider_than` the same knob, and move the choosing of glyphs into a small function of its own, since two functions now need it:

```python
def glyphs_of(font, only_selected=False):
    if not only_selected:
        return font.glyphs
    glyphs = []
    for name in scripting.names_selected_names():
        glyphs.append(font[name])
    return glyphs


def wider_than(font, limit=700, only_selected=False):
    names = []
    for glyph in glyphs_of(font, only_selected):
        if glyph.width > limit:
            names.append(glyph.name)
    return names
```

With `A`, `H`, `M` and `W` selected again:

```python
print(wider_than(font, only_selected=True))
print(wider_than(font, limit=600, only_selected=True))
print(len(wider_than(font, limit=900)))
```

```text
['M', 'W']
['H', 'M', 'W']
2
```

The first call skips `limit` and sets the knob after it. You can only do that by name. By position you'd have to write `wider_than(font, 700, True)`, repeating a default you didn't want to think about, and leaving a bare `True` that tells a reader nothing. Naming the slot is the only good way to write that call.

`glyphs_of` shows something else. A function can have more than one `return`. The first one hands back the whole font and leaves at once, and the rest of the function is only reached when the knob is on.

## The whole script

Here is `widest.py` as it stands by this evening, with the test calls at the bottom. It needs nothing but Fly.

```python
from fly import fl
import fly.ap.core.scripting as scripting


def glyphs_of(font, only_selected=False):
    if not only_selected:
        return font.glyphs
    glyphs = []
    for name in scripting.names_selected_names():
        glyphs.append(font[name])
    return glyphs


def widest_glyph(font, only_selected=False):
    widest = None
    for glyph in glyphs_of(font, only_selected):
        if widest is None or glyph.width > widest.width:
            widest = glyph
    return widest


def wider_than(font, limit=700, only_selected=False):
    names = []
    for glyph in glyphs_of(font, only_selected):
        if glyph.width > limit:
            names.append(glyph.name)
    return names


font = fl.CurrentFont()
widest = widest_glyph(font, only_selected=True)
if widest is None:
    print("Select some glyphs first.")
else:
    print(widest.name, widest.width)
print(wider_than(font, limit=700, only_selected=True))
```

`widest_glyph` is shorter than it was in Step 3, because `glyphs_of` took over its first half.

Mira selects her four capitals and gets her answer: `W`, at 859 units. Then she selects all 26 and asks which are wider than 700. The old calls in her other scripts still mean what they meant, because a call that says nothing gets the ordinary case.

## What you learned

A slot in a `def` line can carry a default, written `name=value`, and a call that leaves the slot empty gets that value. You can fill any slot by name, which makes a call explain itself and lets you skip the optional slots you don't care about. Slots that must be filled come before slots with defaults. A function that has nothing to hand back should return `None`, and its caller should ask `is None` before using the result.

## Try it yourself

1. Copy `status_tally` and `LEGEND` from chapter 33 into `widest.py`, and give `status_tally` an `only_selected=False` slot, using `glyphs_of`. Select the capitals and print the tally for them alone. Which line of the function did you have to change, besides the `def` line?
2. Write `narrower_than(font, limit=300, only_selected=False)`. Then look at it next to `wider_than`. They differ in one character. Is that worth a single function with a third knob, or are two functions clearer? There's no right answer, but decide, and say why in a comment.
3. Call `wider_than(font, only_selected=True, limit=600)`, with the two named slots the other way around. Does it work? Then call `wider_than(limit=600, font=font)`. What does that tell you about slots filled by name?

## Next

`wider_than` hands back names, and Mira wants the widths beside them. Chapter 35 builds rows: lists that hold lists.
