---
this_file: src_docs/md/part3-shapes/042-count-the-nodes.md
---

# 42. Count the nodes

Tuesday. Mira is still thinking about the `g` she guessed wrong yesterday, and about something a teacher told her years ago: a point you don't need is a point that can go wrong. Every node in an outline is a place where a curve can kink, where two masters can disagree, where a hand can slip. Good outlines are economical.

"So which glyph in Plum has the most?" she asks. "I'd like to look at it."

Nobody at Halfmoon knows the answer. To find it, a script has to open every glyph in the font, which is one more level than yesterday. And before it counts, it has to deal with what we left hanging: of the twelve nodes in an oval, four sit on the line and eight are handles. A count that mixes them up tells you little.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` from Part 2, in the folder where chapter 33 put it.
- Yesterday's idea of layer, contour and node.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. Treat what the calls return as what the helpers' source says they return.

## Step 1: On the line or off it

Open the `o` in a Glyph window and ask each node of the outer contour one question:

```python
from fly.tr.proxy.fl.objects.glyph import pGlyph

glyph = pGlyph()
outer = glyph.contours()[0]
for node in outer.nodes():
    print(f"{node.x:>5.0f}{node.y:>5.0f}  {node.isOn()}")
```

```text
  260  -10  True
  396  -10  False
  482   90  False
  482  239  True
  482  388  False
  396  488  False
  260  488  True
  124  488  False
   38  388  False
   38  239  True
   38   90  False
  124  -10  False
```

`isOn()` answers `True` for a node that sits on the outline and `False` for a handle. It's a question with a yes or no answer, like `isEmpty()` in chapter 8, and it wants its parentheses.

Look at the rhythm: one `True`, two `False`, and again. Each curved piece of the outline runs from one on-line node to the next, and it needs two handles to say how it bends, one for leaving and one for arriving. So a curve costs three nodes, and a straight piece costs one. A glyph made of straight lines is cheap, and a round one is expensive.

## Step 2: A mistake that says nothing

Count the two kinds for the whole glyph. `glyph.nodes()` hands you every node of the layer in one flat list, so you don't need the loop inside a loop for this:

```python
on = 0
off = 0
for node in glyph.nodes():
    if node.isOn:
        on = on + 1
    else:
        off = off + 1
print(on, off)
```

```text
24 0
```

That's wrong, and nothing complained. The `o` has eight nodes on the line and sixteen handles. This says twenty-four and none.

Did you see it? The parentheses are missing after `isOn`. Yesterday, the same slip with `len(glyph.contours)` earned you an error. Today it earns you nothing, and that's worse. Remember truthiness from chapter 31: `if` will take any value at all and decide whether it counts as true. `node.isOn` without parentheses is the method itself, not its answer, and a method is a thing that exists, so it counts as true. Every time. The script asked "is there such a question?" where it meant to ask the question.

This is one of the few mistakes in Python that a beginner and an old hand make equally often. You can't make Python catch it. What you can do is know what the result should look like. You knew the `o` has handles, so `24 0` looked wrong to you at once. Before you trust a count from a script, run it on one glyph where you already know the answer.

Put the parentheses in:

```python
    if node.isOn():
```

```text
8 16
```

## Step 3: A function with two answers

This belongs in `halfmoon.py`, because we'll want it again. Add it under `metrics_rows`:

```python
def node_counts(font, glyph, master="Regular"):
    nodes = rich(font, glyph).nodes(master)
    on = len([node for node in nodes if node.isOn()])
    return on, len(nodes) - on
```

There are three things to notice.

The first line uses `rich`, the helper from chapter 33 that puts a plain glyph into the well-equipped box. Then it calls `nodes(master)`, with something in the slot this time. Yesterday `pGlyph()` and `nodes()` with empty parentheses meant "the glyph on screen, the layer that's showing". That's fine for one glyph you're looking at. A script that walks the whole font isn't looking at anything, so it should say which layer it wants by name: `"Regular"`. The name goes in as a default argument, the way chapter 34 showed, so you can ask for another master when you need to.

The second line is a comprehension with a filter, from chapter 37: collect the nodes that are on the line, and take the length of the collection.

The third line returns two values with a comma between them. You've seen this from the other side. In chapter 35 you unpacked a row with `name, lsb, width, rsb = row`. A comma between values makes a tuple, with or without parentheses around it, so `return on, len(nodes) - on` hands back one tuple of two numbers. The caller unpacks it the same way:

```python
import importlib
import halfmoon
from fly import fl

importlib.reload(halfmoon)
font = fl.CurrentFont()
on, off = halfmoon.node_counts(font, font["o"])
print(on, off)
```

```text
8 16
```

The `reload` line is there because you've edited the module, and FontLab may still be holding the old copy, as chapter 33 explained. Take it out once the function works.

Try a few more by hand. `H` gives `12 0`: it's all straight lines. `l` gives `4 0`, a plain rectangle. `n` gives `12 8`, which is four curved pieces with two handles each, and the rest straight.

## Step 4: Every glyph

Now walk the font. For each glyph we want a row with its name and its counts, as in chapter 35:

```python
rows = []
for glyph in font.glyphs:
    on, off = halfmoon.node_counts(font, glyph)
    rows.append((glyph.name, on, off, on + off))
print(len(rows))
print(rows[1])
```

```text
220
('A', 11, 0, 11)
```

There's a row for each of the 220 glyphs in the practice font (the 205 that Plum came with, and the 15 you've added since chapter 8), and the second one is the `A`: eleven nodes on the line, no handles, because Plum's `A` is all straight. Check that against the Glyph window, as Step 2 told you to. The outer shape has eight corners and the triangle inside has three.

If your `A` says something else, don't doubt the arithmetic yet. Print what you're measuring:

```python
print(font.info.familyName, len(font))
```

`fl.CurrentFont()` means the font in front, and when a second font is open behind your back it will answer for that one. Mira lost ten minutes to this in the morning, with one of Oskar's old files sitting in front of the practice font. It's the oldest trap in this book and it doesn't go away.

Many of the rows are all zeros: glyphs built from other glyphs, like `eacute`, and the empty ones waiting to be drawn. They'd only clutter the answer, so keep the rows that have something in them:

```python
rows = []
for glyph in font.glyphs:
    on, off = halfmoon.node_counts(font, glyph)
    if on + off > 0:
        rows.append((glyph.name, on, off, on + off))
print(len(rows))
```

```text
121
```

Of the 220 glyphs in the practice font, 121 have an outline of their own in the Regular master. The other 99 are borrowed or empty. That number alone tells you something about how Plum was made: fewer than six glyphs in ten were drawn.

## Step 5: The most, and the average

Sort the rows by the total, largest first, with a key function as in chapter 36:

```python
def by_total(row):
    return row[3]


for name, on, off, total in sorted(rows, key=by_total, reverse=True)[:5]:
    print(f"{name:<12}{on:>4}{off:>5}{total:>6}")
```

```text
ae            27   42    69
at            23   40    63
oe            20   34    54
ampersand     22   32    54
percent       20   32    52
```

There's Mira's answer. The `æ` has the most, 69 nodes, and that makes sense: it's two letters fused, with three contours. The at sign is next. Nothing here looks like a mistake. These are the glyphs you'd expect to be the most complicated, and that's a good sign for the font.

Now the average. Add up the totals and divide by the number of rows:

```python
total_nodes = sum([row[3] for row in rows])
print(total_nodes, total_nodes / len(rows))
```

```text
2585 21.363636363636363
```

So Plum's Regular master holds 2,585 nodes, about 21 for each drawn glyph. If you'd like to know how curvy a glyph is, you could divide its handles by its on-line nodes. Try that on a row:

```python
name, on, off, total = rows[0]
print(name, off / on)
```

That works for every row, because we kept only glyphs with nodes. But suppose you'd done it inside the first loop, before the filter, for every glyph in the font:

```python
for glyph in font.glyphs:
    on, off = halfmoon.node_counts(font, glyph)
    print(glyph.name, off / on)
```

```text
.notdef 0.0
A 0.0
Traceback (most recent call last):
  File "<string>", line 3, in <module>
ZeroDivisionError: division by zero
```

The third glyph is `Aacute`. It has no nodes of its own, so `on` is zero, and you can't divide by zero in Python any more than on paper. The script stops there.

It's an error you should expect whenever you divide by something you counted. A count can be zero, and one day it will be. The cure is to ask first:

```python
if on > 0:
    print(glyph.name, off / on)
```

The same goes for the average. `total_nodes / len(rows)` fails on a font where nothing is drawn, so the finished script checks that `rows` isn't empty before it divides.

## The whole script

Here is `node_count.py`:

```python
# Lists the glyphs with the most nodes in one master, and the font's totals.
# Reads only.
import halfmoon
from fly import fl

MASTER = "Regular"
HOW_MANY = 5


def by_total(row):
    return row[3]


def main():
    font = fl.CurrentFont()
    if font is None:
        print("Open a font first.")
        return

    rows = []
    for glyph in font.glyphs:
        on, off = halfmoon.node_counts(font, glyph, MASTER)
        if on + off > 0:
            rows.append((glyph.name, on, off, on + off))

    if not rows:
        print("No outlines in", MASTER)
        return

    print(f"{font.info.familyName}, {MASTER}")
    print(f"{'glyph':<12}{'on':>4}{'off':>5}{'total':>6}")
    for name, on, off, total in sorted(rows, key=by_total, reverse=True)[:HOW_MANY]:
        print(f"{name:<12}{on:>4}{off:>5}{total:>6}")

    all_on = sum([row[1] for row in rows])
    all_off = sum([row[2] for row in rows])
    print()
    print(f"{len(rows)} glyphs with outlines")
    print(f"{all_on + all_off} nodes: {all_on} on the line, {all_off} handles")
    print(f"{(all_on + all_off) / len(rows):.1f} nodes a glyph")


main()
```

```text
GG Plum, Regular
glyph         on  off total
ae            27   42    69
at            23   40    63
oe            20   34    54
ampersand     22   32    54
percent       20   32    52

121 glyphs with outlines
2585 nodes: 1413 on the line, 1172 handles
21.4 nodes a glyph
```

The script names the master in a constant at the top and prints it with the font's name, so nobody has to guess what was measured. Two guards stand before the work: no font, and nothing to count. And it stays short because the counting lives in the module.

Mira opens the `ae` and looks at it for a long time. Then she opens the `at`. "Forty handles," she says. "I'd have said twenty."

## What you learned

`isOn()` tells a node on the outline from a handle, and a curve costs three nodes where a straight line costs one. A method without its parentheses counts as true in an `if`, and Python won't warn you, so test a new count on a glyph whose answer you know. A function can return two values with a comma, and the caller unpacks them. Before you divide by a count, check that it isn't zero.

## Try it yourself

1. Change `MASTER` to `"Bold"` and run `node_count.py` again. Compare the totals with Regular. What does that tell you about how the three masters of Plum were drawn?
2. Turn the list upside down: show the glyphs with the fewest nodes, leaving out the ones with none. Several tie for last place, so show ten. You need to change one word. Which glyphs are they, and what shape do they share?
3. Add a fifth field to each row: handles divided by on-line nodes, to one decimal. Sort by it, largest first. The glyphs at the top are the roundest in the font. Is `o` among them? What's the largest value a glyph can have, and why can't it go higher?

## Next

Every node has an `x` and a `y`, and so far you've only printed them. Chapter 43 uses them to measure: how tall is the `H`, how far does the `o` dip below the baseline, and does every capital reach the same height?
