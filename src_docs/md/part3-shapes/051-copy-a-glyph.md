---
this_file: src_docs/md/part3-shapes/051-copy-a-glyph.md
---

# 51. Copy a glyph

Monday, the tenth week. The small caps have been ten empty glyphs since chapter 40, and one of them holds a placeholder box. The art director's proof page is due on Thursday.

Nobody draws small caps from nothing. You start from the capitals, shrink them to the height of the lowercase, and then spend a week putting back the weight that the shrinking took away. Mira knows the week of drawing is hers. The shrinking is a chore, and chores go to a script.

So today a script copies each capital into its small-cap glyph, scaled down. That part is short, because chapter 50 did nearly the same thing with the dashes. The longer part of this chapter is about the word "copy" itself. Python uses it more strictly than people do, and the difference bites everybody once.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `box` from chapter 43 and `set_width` from chapter 49. You'll write them out again here.
- The small-cap glyphs from chapters 8 and 40: `a.sc` to `h.sc`, `zero.sc` and `one.sc`. Leave the box in `e.sc` where it is. It has a part to play. Every other `.sc` glyph has to be empty in all three masters. If you drew boxes in `f.sc` or `g.sc`, did exercise 2 of chapter 46 without undoing it, or left a practice sketch from chapters 44 and 45, delete those outlines first. If you don't, your run will say `already has outlines, skipped` where this chapter shows a draft.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. The pen numbers come from running the pens in plain Python.

## Step 1: Two names, one list

Mira starts with a list of the capitals she wants and makes a second list for the drafts:

```python
caps = ["A", "B", "C"]
drafts = caps
drafts.append("D")
print(drafts)
print(caps)
```

```text
['A', 'B', 'C', 'D']
['A', 'B', 'C', 'D']
```

She added `D` to `drafts`, and `caps` has it too. Nothing went wrong and no error came, which is why this one is hard to find when it happens in a long script.

Since chapter 5 I've told you that a variable is a box with a label, and that `=` puts a thing in the box. That picture has carried you through fifty chapters, and here it gives out. The line `drafts = caps` didn't build a second list. It tied a second label to the list that was already there. There's one list, and it has two names. Whatever you do to it through one name, you see through the other.

Python can tell you whether two names mean the same thing. You've used the word before, in `is None`:

```python
print(drafts is caps)
```

```text
True
```

## Step 2: A real copy

To get a second list, you have to ask for one:

```python
caps = ["A", "B", "C"]
drafts = list(caps)
drafts.append("D")
print(drafts)
print(caps)
print(drafts is caps)
```

```text
['A', 'B', 'C', 'D']
['A', 'B', 'C']
False
```

`list(caps)` walks along the old list and builds a new one with the same things in it. Now there are two lists, and they go their own ways. You'll also see `caps.copy()`, which does the same job. Dictionaries and sets have `dict(...)`, `set(...)` and their own `.copy()`.

Why did you never run into this with numbers?

```python
a = 5
b = a
b = b + 1
print(a, b)
```

```text
5 6
```

Because `b + 1` makes a new number, and `b =` ties the label `b` to that new number. Nobody changed the 5. You can't change a 5. A number or a piece of text can only be replaced, and replacing moves one label. A list can be changed in place, with `append`, with `reverse`, with `names[0] = ...`, and a change in place is seen through every label the list has.

So the rule is short. `=` never copies. With numbers and text you can't tell. With lists, dictionaries and sets you can.

## Step 3: A function gets a label too

The same thing happens when you hand a list to a function. Here's a helper that turns names into small-cap names:

```python
def with_suffix(names):
    for i in range(len(names)):
        names[i] = names[i] + ".sc"
    return names

caps = ["A", "B"]
small = with_suffix(caps)
print(small)
print(caps)
```

```text
['A.sc', 'B.sc']
['A.sc', 'B.sc']
```

Inside the function, `names` is one more label on the caller's list. The function wrote into it, and the caller's list of capitals is gone. A function that changes what it's given, without saying so in its name, is a trap for whoever calls it. The honest version builds a new list and leaves its input alone:

```python
def with_suffix(names):
    return [name + ".sc" for name in names]
```

A comprehension always makes a new list. That's one more reason I reach for one.

## Step 4: The same question in a font

Now look at a glyph with the same eyes. When a small cap comes from a capital, there are two ways to get it there.

One is a real copy. The script reads the outline of `A`, and draws the same shape, smaller, into `a.sc`. From then on the two have nothing to do with each other. If Mira moves a node in `A` next month, `a.sc` stays as it was.

The other is a second label. A glyph can hold a **component**: a note that says "show the outline of that other glyph here". Plum's `eacute` has two of them, as you saw in chapter 41, and when the `e` changes, the `eacute` changes with it. Chapter 52 is about those.

Which do you want for small caps? A copy, and for a plain reason: the small caps are going to be redrawn. They need their own nodes, because every one of them will be moved. A component can be shifted and scaled, but you can't thicken its stems.

## Step 5: How much smaller

A small cap stands about as tall as the lowercase `x`. In the Regular, the top of `x` is at 478 and the top of `H` is at 688, as chapter 43 found. The factor is one divided by the other, with `box` from that chapter:

```python
x_top = box(font, font["x"], master)[3]
cap_top = box(font, font["H"], master)[3]
factor = x_top / cap_top
print(round(factor, 3))
```

```text
0.695
```

`box` gives four numbers, and `[3]` picks the last one, the top. The factor differs a little by master, because the x-height does: 0.689 in the Light, 0.695 in the Regular and 0.701 in the Bold. So the script works it out for each master and nobody types it.

In chapter 50, scaling was a nuisance, because it's measured from the origin and the hyphen slid away from its place. Here that's what you want. The origin is the left end of the baseline. Scaling from there keeps the letter on the baseline and shrinks its left sidebearing by the same factor as the letter. Scale the width too, and the right sidebearing follows.

The copy itself is the chain from chapter 50, with one pen more:

```python
recording = RecordingPen()
draw(layer_of(source.fl, master), recording)
with FlPen(layer, notify="Small-cap draft") as pen:
    recording.replay(TransformPen(RoundingPen(pen), Transform().scale(factor)))
```

Read it from the inside out. `pen` writes into the layer. `RoundingPen(pen)` rounds each coordinate to a whole number and hands it on. `TransformPen(...)` scales and hands on to that. The capital's `A` runs from 13 to 585 and up to 688 in the Regular. Its draft runs from 9 to 406 and up to 478, on the x-height to the unit.

## Step 6: Which capital for which name

The script gets small-cap names and has to find the capital for each. `a.sc` comes from `A`. For a one-letter name that's two string methods you know:

```python
def source_name(name):
    base = name.removesuffix(SUFFIX)
    if len(base) == 1:
        return base.upper()
    return None
```

`zero.sc` and `one.sc` have longer names and get `None`. That's on purpose. Small-cap figures aren't shrunken figures, and Mira hasn't decided what they'll be.

One more thing, and it comes straight from step 1. The script loops over small-cap names while it draws into the font. I don't loop over `font.glyphs` for that. I collect the names into a list of my own first, and loop over the list. Today nothing gets added to the font, so it wouldn't matter. In chapter 53 glyphs will be added, and a loop over a list that grows under it is a bad afternoon.

## The whole script

Here is `make_sc_drafts.py`. It writes out `box` and `set_width` at the top, so it runs by itself:

```python
# Fills every empty one-letter small-cap glyph with a scaled copy of its
# capital and scales the width to match. Drafts only: the stems come out thin.
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
from fly import fl
from fly.pens import FlPen, RecordingPen, RoundingPen, Transform, TransformPen, layer_of
from fly.pens.fontlab import draw
from fly.tr.proxy.fl.objects.glyph import pGlyph

MASTERS = ["Light", "Regular", "Bold"]
SUFFIX = ".sc"


def box(font, glyph, master="Regular"):
    nodes = pGlyph(font, glyph).nodes(master)
    if not nodes:
        return None
    xs = [node.x for node in nodes]
    ys = [node.y for node in nodes]
    return min(xs), min(ys), max(xs), max(ys)


def set_width(glyph, layer, width, title="Set width"):
    def change():
        layer.advanceWidth = width

    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    history.commit(title, [layer], [glyph.fl], change, operation="geometry", facts=facts)


def source_name(name):
    base = name.removesuffix(SUFFIX)
    if len(base) == 1:
        return base.upper()
    return None


def factor_for(font, master):
    x_top = box(font, font["x"], master)[3]
    cap_top = box(font, font["H"], master)[3]
    return x_top / cap_top


def draft(font, name, capital, master):
    source = pGlyph(font, font[capital])
    target = pGlyph(font, font[name])
    factor = factor_for(font, master)
    recording = RecordingPen()
    source_layer = layer_of(source.fl, master)
    draw(source_layer, recording)
    layer = layer_of(target.fl, master)
    with FlPen(layer, notify="Small-cap draft") as pen:
        recording.replay(TransformPen(RoundingPen(pen), Transform().scale(factor)))
    width = round(source_layer.advanceWidth * factor)
    set_width(target, layer, width, "Fit small cap")
    return width


def main():
    font = fl.CurrentFont()
    names = [glyph.name for glyph in font.glyphs if glyph.name.endswith(SUFFIX)]
    for name in names:
        capital = source_name(name)
        if capital is None or font[capital] is None:
            print(f"{name:<9}no capital to copy, skipped")
            continue
        target = pGlyph(font, font[name])
        if any([target.contours(master) for master in MASTERS]):
            print(f"{name:<9}already has outlines, skipped")
            continue
        widths = [draft(font, name, capital, master) for master in MASTERS]
        print(f"{name:<9}from {capital}  widths {widths[0]} {widths[1]} {widths[2]}")


main()
```

```text
a.sc     from A  widths 382 414 418
b.sc     from B  widths 339 359 362
c.sc     from C  widths 410 431 435
d.sc     from D  widths 445 462 466
e.sc     already has outlines, skipped
f.sc     from F  widths 285 319 322
g.sc     from G  widths 423 454 457
h.sc     from H  widths 422 467 471
zero.sc  no capital to copy, skipped
one.sc   no capital to copy, skipped
```

The order of your lines follows the order of glyphs in your font, so it may differ from mine.

`e.sc` was skipped because the box from chapter 46 is still in it. The script won't draw over what's there. A pen adds and never replaces, so drawing again would stack an `E` on the box. Delete the box by hand in all three masters, run the script again, and you get one new line, `e.sc     from E  widths 305 337 340`, with nine lines of "skipped" around it. The guard you wrote for the placeholder script makes this one safe to run twice.

Check `a.sc` with `bounds.py`: in the Regular the box should run from 9 to 406 across and from 0 to 478 up, in a glyph 414 wide.

Then look at the drafts next to the lowercase, and you'll see what Mira saw. They're the right height and too light. The stem of the capital `I` is 82 units wide in the Regular, and so is the stem of the lowercase `l`. Scaled by 0.695, a capital stem comes out 57 wide. Next to an 82-unit lowercase stem that's a different weight. The overshoot shrank as well: the round capitals go 10 units over the line and the drafts go 7.

That's the week of drawing, and no script in this book will do it. But Mira starts the week with every draft the right height and on the baseline, with matching sidebearings in three masters. And when she touches a node in `a.sc`, the capital `A` doesn't move, because the draft is a copy.

## What you learned

`=` ties a label to a thing and never copies it, so with a list, a dictionary or a set, two labels mean one thing, and a change through either shows through both. `is` tells you whether two names mean the same thing, and `list(...)` or `.copy()` makes a second one. A function gets a label on what you hand it, so a tidy function builds a new list and leaves its input alone. In a font the same choice has two names: an outline drawn again is a copy, and a component is a second label.

## Try it yourself

1. Predict, then run: `a = [1, 2]`, `b = a`, `b = b + [3]`, `print(a, b)`. Then the same with `b += [3]` in place of the third line. One of them changes `a`. Which, and what does that tell you about `+=` on a list?
2. A dictionary holds lists: `groups = {"round": ["O", "C"]}`. Write `mine = dict(groups)`, append `"G"` to `mine["round"]`, and print both dictionaries. The copy is only one level deep. Say in a sentence what `dict(...)` copied and what it didn't.
3. Make an empty glyph `i.sc`, run the script, and read the Regular width of the draft before you look: the capital `I` is 228 wide. Then measure the draft's stem with `bounds.py` and work out how many units Mira has to add to bring it to 82.

## Next

Oskar's sheet has two lines about glyphs that are built from other glyphs. Chapter 52 opens a component, reads which glyph it points to and how far it's shifted, and crosses one of those lines out.
