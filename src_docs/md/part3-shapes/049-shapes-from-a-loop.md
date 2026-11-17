---
this_file: src_docs/md/part3-shapes/049-shapes-from-a-loop.md
---

# 49. Shapes from a loop

Thursday. The cookbook's contents page has a row of dots between each recipe and its page number, and the publisher's designer made the rows by typing ellipses one after another. In the Regular it looks fine. The part titles are set in Bold, and there the dots come in clumps of three with almost no room between one clump and the next.

Ines forwards the page with one line: "Is that us or them?"

It's us. Mira opens the Bold ellipsis in the Glyph window and does the sums on paper, with the period's box from chapter 43 beside her. The dots inside an ellipsis are 108 units apart. The ellipsis is 684 wide, but its third dot ends at 746, which is 62 units past the edge of the glyph. The first dot of the next ellipsis starts 74 units in. So between two ellipses the dots are 12 units apart, where inside they're 108. In the Regular the two numbers are 110 and 104, close enough that nobody saw it.

Mira won't touch the ellipsis today, because a text that ends a sentence with one looks right as it is. The contents page needs something else: a glyph made for standing in rows, with every dot the same distance from the next, whether the next dot is in the same glyph or in the one after. She calls it `leader`.

Three dots are three circles, and you could call `circle` three times. Today you'll make the loop do it, and to do that the loop has to count.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `box` from chapter 43 and `circle` from chapter 48. You'll write them out again here.
- A new empty glyph called `leader`, made with **Add Glyphs From List** as in the last two chapters.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. The pen numbers come from running the pens in plain Python.

## Step 1: A loop that counts

Every loop you've written so far walked along something that was already there: the glyphs of a font, the nodes of a contour, the lines of a file. Sometimes there's nothing to walk along. You want to do a thing three times, and that's all. Python has a small tool for it:

```python
for i in range(3):
    print(i)
```

```text
0
1
2
```

`range(3)` hands the loop three numbers, one per round. Two things about them trip up everybody once. The count starts at 0, as positions in a list do. And 3 itself never arrives: the numbers stop before the one you wrote. Three rounds, numbered 0, 1 and 2.

The name `i` is a habit that programmers share. It stands for "index", and it's one of the few one-letter names I'll use in this book. When the number means something, give it a better name, as you will in a minute.

If you print a range, it doesn't show its numbers:

```python
print(range(5))
print(list(range(5)))
```

```text
range(0, 5)
[0, 1, 2, 3, 4]
```

A range is a recipe for numbers, and it makes each one when the loop asks. Wrap it in `list` when you want to see them all. I do that whenever I'm not sure what a range will give, and I'm unsure more often than I'd like.

## Step 2: Where to start, where to stop, how far to jump

The first line of that output says `range(0, 5)`. A range has a start, and when you leave it out the start is 0. You can write it yourself:

```python
print(list(range(1, 6)))
```

```text
[1, 2, 3, 4, 5]
```

It starts at 1 and stops before 6. And there's a third number, the **step**, which is how far the count jumps each round:

```python
print(list(range(0, 50, 10)))
```

```text
[0, 10, 20, 30, 40]
```

Start at 0, add 10 each time, stop before 50. Once more, 50 itself isn't in the list.

That third form is the one a row of dots needs. In Plum's Regular, the dots of the ellipsis are 230 units apart, center to center. If the first center is at 115, the row is:

```python
print(list(range(115, 690, 230)))
```

```text
[115, 345, 575]
```

Those are three x coordinates, one for each dot. The loop variable is a position now, and it'll get the name `cx`.

## Step 3: Three dots, and a number that isn't whole

Where do 115 and 690 come from? I'd rather work them out than type them. Call the distance from dot to dot the step, and say how many dots you want:

```python
STEP = 230
COUNT = 3

for cx in range(STEP / 2, COUNT * STEP, STEP):
    print(cx)
```

The first center is half a step in. The row ends after three whole steps. Run it:

```text
Traceback (most recent call last):
  File "<string>", line 4, in <module>
TypeError: 'float' object cannot be interpreted as an integer
```

In chapter 11 you met the two kinds of number: whole numbers, and floats with a decimal point. Dividing with `/` always gives a float, even when the answer comes out even. `230 / 2` is `115.0`. And `range` counts, so it takes whole numbers and nothing else.

You could wrap the division in `int()`. There's a shorter way, a second division sign that throws the remainder away and keeps the answer whole:

```python
print(230 / 2)
print(230 // 2)
print(7 // 2)
```

```text
115.0
115
3
```

Two slashes: **floor division**. Seven halves is three and a bit, and the bit is dropped. Change the line to `range(STEP // 2, COUNT * STEP, STEP)` and the loop prints 115, 345 and 575.

Now hand those positions to the pen. The period in the Regular has a radius of 60 and its center is 50 units above the baseline, as chapter 48 found:

Define `circle` from chapter 48 in this script first, then:

```python
from fly.pens import RecordingPen

pen = RecordingPen()
for cx in range(STEP // 2, COUNT * STEP, STEP):
    circle(pen, cx, 50, 60)
print(len(pen.value))
```

```text
18
```

The recording has eighteen orders. A circle is six of them: one `moveTo`, four `curveTo` and one `closePath`. Three circles came from one line that draws.

## Step 4: Why half a step

The first dot sits half a step from the left edge for a reason, and the reason is the whole point of the `leader` glyph.

The dot is 120 wide and the step is 230, so the room between two dots is 110. With the first center at half a step, the first dot starts 55 units in, which is half of that room. If the glyph is three steps wide, 690, the last dot ends 55 units before the right edge. Put two `leader` glyphs side by side and the room between the last dot of one and the first dot of the next is 55 plus 55. That's 110 again, and the row has the same beat all the way across the page.

So the width of the glyph isn't a matter of taste here. It's the count times the step:

```python
width = COUNT * STEP
```

Plum's own ellipsis is built another way. Its width is meant to be two steps plus the width of a period. In the Regular that's 460 plus 224, which is 684. In the Bold the steps grew to 260, so the width should be 744. It is still 684, the Regular's width, and the third dot hangs over. That's how the rows on the contents page lost their beat.

## Step 5: Draw it in three masters

The step is different in each master: 160 in the Light, 230 in the Regular, 260 in the Bold. Those are the distances in Plum's ellipsis. I read them in the Glyph window, and chapter 52 will show you how a script reads them. For today they go in a dictionary, with the master names as keys:

```python
STEPS = {"Light": 160, "Regular": 230, "Bold": 260}
```

The size of the dot and its height come from the period, as they did for the bullet:

```python
font = fl.CurrentFont()
glyph = pGlyph(font, font["leader"])
for master in MASTERS:
    step = STEPS[master]
    left, bottom, right, top = box(font, font["period"], master)
    radius = round((right - left) / 2)
    cy = round((bottom + top) / 2)
    layer = layer_of(glyph.fl, master)
    with FlPen(layer, notify="Draw leader") as pen:
        for cx in range(step // 2, COUNT * step, step):
            circle(pen, cx, cy, radius)
```

This time the script finds `leader` by name, so it doesn't matter which glyph you're looking at. The loop over masters has the loop over positions inside it. That's the nesting from chapter 41, and the inner loop runs three times for each master. The `with` block sits between the two, so each master gets one pen, and all three dots of a master are one step in **Edit > Undo**.

## Step 6: Make the width fit

The dots are in, but the glyph is still 500 wide, the width chapter 40's script gave every new glyph. In the Regular the third dot ends at 635, well outside it.

You changed a width once before, in chapter 29, and the pattern was: put the change in a small function, then hand that function to `history.commit` so that FontLab records one Undo step. You'll set widths often from here on, so make the pattern a function. Define it in this script:

```python
def set_width(glyph, layer, width, title="Set width"):
    def change():
        layer.advanceWidth = width

    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    history.commit(title, [layer], [glyph.fl], change, operation="geometry", facts=facts)
```

There's a function inside a function here, which is new. `change` is written inside `set_width`, and it can see the boxes of the function around it: `layer` and `width` aren't handed to it, yet it uses them. In chapter 29 `widen` did the same with boxes at the top of the script. A function looks for a name in its own boxes first and then in the place where it was written.

The script needs the two import lines from `safe_edit.py` at its top for this:

```python
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
```

In the script it's one more line per master, after the `with` block:

```python
    set_width(glyph, layer, COUNT * step, "Fit leader")
```

Run the script with a Font window in front. FontLab keeps a separate Undo list for the Glyph window, and how this call behaves there is untested.

## The whole script

Here is `dot_row.py`. It writes out `box`, `circle` and `set_width` at the top, so it runs by itself.

```python
# Draws a row of COUNT dots in every empty master of the glyph "leader"
# and fits the width, so that rows of leaders keep an even beat.
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
from fly import fl
from fly.pens import FlPen, layer_of
from fly.tr.proxy.fl.objects.glyph import pGlyph

MASTERS = ["Light", "Regular", "Bold"]
STEPS = {"Light": 160, "Regular": 230, "Bold": 260}
COUNT = 3


def box(font, glyph, master="Regular"):
    nodes = pGlyph(font, glyph).nodes(master)
    if not nodes:
        return None
    xs = [node.x for node in nodes]
    ys = [node.y for node in nodes]
    return min(xs), min(ys), max(xs), max(ys)


KAPPA = 0.5523  # handle length for a quarter circle, as a share of the radius


def circle(pen, cx, cy, radius):
    h = round(radius * KAPPA)
    pen.moveTo((cx - radius, cy))
    pen.curveTo((cx - radius, cy - h), (cx - h, cy - radius), (cx, cy - radius))
    pen.curveTo((cx + h, cy - radius), (cx + radius, cy - h), (cx + radius, cy))
    pen.curveTo((cx + radius, cy + h), (cx + h, cy + radius), (cx, cy + radius))
    pen.curveTo((cx - h, cy + radius), (cx - radius, cy + h), (cx - radius, cy))
    pen.closePath()


def set_width(glyph, layer, width, title="Set width"):
    def change():
        layer.advanceWidth = width

    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    history.commit(title, [layer], [glyph.fl], change, operation="geometry", facts=facts)


def main():
    font = fl.CurrentFont()
    glyph = pGlyph(font, font["leader"])
    for master in MASTERS:
        if glyph.contours(master):
            print(f"{master}: already has outlines, skipped")
            continue
        step = STEPS[master]
        left, bottom, right, top = box(font, font["period"], master)
        radius = round((right - left) / 2)
        cy = round((bottom + top) / 2)
        layer = layer_of(glyph.fl, master)
        with FlPen(layer, notify="Draw leader") as pen:
            for cx in range(step // 2, COUNT * step, step):
                circle(pen, cx, cy, radius)
        width = COUNT * step
        set_width(glyph, layer, width, "Fit leader")
        print(f"{master:<9}{COUNT} dots  step {step}  radius {radius}  width {width}")


main()
```

```text
Light    3 dots  step 160  radius 33  width 480
Regular  3 dots  step 230  radius 60  width 690
Bold     3 dots  step 260  radius 76  width 780
```

Check it with `bounds.py`. In the Regular the box of `leader` should run from 55 to 635, in a glyph 690 wide: 55 units of room on each side. In the Light it's 47 on each side, and in the Bold 54. The two sides match in every master, and that's the test. Then type a row of leaders in a text, in the Bold, and look for the clumps.

The script makes six steps in **Edit > Undo**, a drawing and a width for each master. That's how the two calls are designed. If your copy shows fewer or more, believe your copy.

Mira types a line of `leader` glyphs under the row of ellipses and sends both to Ines. Ines writes back in a minute: "Second one. Tell the designer how to type it." That's a fair point. A glyph with no Unicode value can't be typed, and Part 5 will deal with it. For now the designer picks it from the Glyphs panel of the layout program.

On Oskar's sheet nothing gets crossed out. Mira adds a line of her own at the bottom, in pencil: "Bold ellipsis: third dot outside the glyph."

## What you learned

`range` makes a loop count when there's nothing to walk along: one number is where to stop, two are start and stop, three add the step, and the stop number itself never arrives. `range` takes whole numbers only, and `//` divides without leaving a decimal point. A loop variable can be a coordinate, so one drawing line makes as many shapes as the range has numbers, and the width of a glyph can be worked out from what's in it: here, count times step, so that the rhythm carries from one glyph into the next.

## Try it yourself

1. Before you run each of these, write down what you expect: `list(range(4))`, `list(range(2, 9, 3))`, `list(range(10, 0, -3))`, `list(range(5, 0))`. The third counts down. The fourth gives an empty list and no error, and a loop over it runs zero times. Why is that worth remembering when a script seems to do nothing?
2. Change `COUNT` to 5, undo the drawing and run `dot_row.py` again. The widths should be 800, 1150 and 1300. Which lines of the script did you have to touch? Then work out by hand, for each master, how wide Plum's `ellipsis` would have to be for rows of it to keep the beat, and compare with the 513, 684 and 684 it has.
3. Draw a colon without typing a single y coordinate. Make an empty glyph `colon.new`, and use `range` with a step to place two dots, one above the other, at the heights of Plum's own colon: the centers in the Regular are at 50 and 428. You'll need a range that goes up the y axis. What are its three numbers?

## Next

The part titles are set in capitals, and the art director says the dashes between them hang too low. Chapter 50 makes a raised copy of each dash: shifting, scaling and slanting outlines that are already there.
