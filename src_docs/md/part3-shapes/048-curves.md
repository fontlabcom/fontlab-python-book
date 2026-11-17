---
this_file: src_docs/md/part3-shapes/048-curves.md
---

# 48. Curves

Wednesday. The cookbook has lists of ingredients, and the publisher's designer wants each line to start with a bullet. Plum has no bullet. It has a period, which is too small and sits on the baseline, and a designer who uses a raised period as a bullet gets a list that looks as if it's stammering.

A bullet is a filled circle. So today the pen learns its fourth order, the one I put off on Monday. A straight line needs one piece of information, which is where to stop. A curve needs three, and most of this chapter is about the other two.

By the end, your script will draw Plum's own period, node for node, from a center and a radius. Then it will draw the bullet.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `box`, `rect` and the rest.
- A new empty glyph called `bullet`, made with **Add Glyphs From List** as you made `notdef.new` yesterday.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. Every number comes from running the pens in plain Python and from that file.

## Step 1: Three points for one curve

In chapter 42 you counted the nodes of the `o` and found that a curve costs three: two handles and the on-curve node where it ends. `curveTo` takes those three, in that order:

```python
from fly.pens import RecordingPen

pen = RecordingPen()
pen.moveTo((0, 60))
pen.curveTo((33, 60), (60, 33), (60, 0))
pen.endPath()

for order in pen.value:
    print(order)
```

```text
('moveTo', ((0, 60),))
('curveTo', ((33, 60), (60, 33), (60, 0)))
('endPath', ())
```

That's a quarter of a circle of radius 60, from the top, at 0, 60, round to the right side, at 60, 0. I ended it with `endPath`, because one arc isn't a closed shape.

Here's how to read the three points. The curve starts where the pen is. The last point, 60, 0, is where it ends. The two in the middle are the handles, and the curve never touches them. The first handle belongs to the start: the pen sets off from 0, 60 heading straight for 33, 60, which is to say due east. The second handle belongs to the end: the pen arrives at 60, 0 as if it had come from 60, 33, which is to say heading due south. In between, the curve bends from one heading to the other.

So a handle says two things. Its direction from its node says which way the curve is heading there. Its distance says how long the curve holds that heading before it gives way. If you've pulled handles in the Glyph window you know both by feel. The pen needs them as numbers.

## Step 2: How long is a handle?

The directions are simple for a circle. At the top it runs level, and at the side it runs straight down. The distance is the puzzle. Why 33, for a radius of 60?

Let's try other lengths and measure what comes out. Yesterday's measuring pen will do it. Here's a rough circle function with the handle length as a share of the radius, and three shares to try:

```python
from fly.pens import AreaPen


def rough_circle(pen, radius, share):
    h = radius * share
    pen.moveTo((-radius, 0))
    pen.curveTo((-radius, -h), (-h, -radius), (0, -radius))
    pen.curveTo((h, -radius), (radius, -h), (radius, 0))
    pen.curveTo((radius, h), (h, radius), (0, radius))
    pen.curveTo((-h, radius), (-radius, h), (-radius, 0))
    pen.closePath()


for share in [0, 0.5523, 1]:
    pen = AreaPen()
    rough_circle(pen, 60, share)
    print(share, round(pen.value, 1))
```

```text
0 7200.0
0.5523 11313.0
1 13680.0
```

Read the function before the numbers. It's four curves: from the left side down to the bottom, on to the right side, up to the top, and back to the left. That's counter-clockwise, as an outside should be. Each curve has a handle `h` units along from its start and another `h` units back from its end.

Now the numbers. A true circle of radius 60 has an area of 3.14159 times 60 times 60, which is 11,310. With handles of no length the shape has an area of 7,200. That's a diamond: with nothing to hold a heading, each curve goes straight to the next corner. With handles as long as the radius it's 13,680, a fat cushion on its way to a square. With 0.5523 it's 11,313, three square units off, in a shape of eleven thousand.

That's where 33 came from. It's 60 times 0.5523, rounded. The number 0.5523 is the handle length that brings four curves closest to a circle. Nobody works it out at the desk. Type designers know it as "a bit more than half", and programmers keep it in a constant. We'll call ours `KAPPA`, which is its usual name, and give it a comment.

A font's curves can't draw an exact circle at all. Four of them come within a hair of one, close enough that nobody has ever seen the difference in print.

## Step 3: Plum's period, from two numbers

Clean up the rough function, give it a center, and put it in `halfmoon.py`:

```python
KAPPA = 0.5523  # handle length for a quarter circle, as a share of the radius


def circle(pen, cx, cy, radius):
    h = radius * KAPPA
    pen.moveTo((cx - radius, cy))
    pen.curveTo((cx - radius, cy - h), (cx - h, cy - radius), (cx, cy - radius))
    pen.curveTo((cx + h, cy - radius), (cx + radius, cy - h), (cx + radius, cy))
    pen.curveTo((cx + radius, cy + h), (cx + h, cy + radius), (cx, cy + radius))
    pen.curveTo((cx - h, cy + radius), (cx - radius, cy + h), (cx - radius, cy))
    pen.closePath()
```

Plum's period in the Regular master has a box from 41 to 161 across and from −10 to 110 up, as `halfmoon.box` will tell you. So its center is at 101, 50 and its radius is 60. Draw that into a recording pen and look at the first curve:

```python
pen = RecordingPen()
halfmoon.circle(pen, 101, 50, 60)
print(pen.value[1])
```

```text
('curveTo', ((41, 16.862000000000002), (67.862, -10), (101, -10)))
```

There's a mistake in the function, and nothing complained about it. Look at the handles: 16.862000000000002 and 67.862. Those would go into the font as they are. A font can hold fractions, but a designer's master drawing shouldn't have them by accident. They make nodes that refuse to line up with anything, and some of the formats you'll export to round them anyway, each in its own fashion. The long tail of digits is the computer's own trouble with decimal fractions. It stores numbers in twos, not tens, and most decimal fractions have no exact form there, as a third has none in tens. So a sum that should end in .862 can come back a hair off.

Round the handle length once, where it's made:

```python
    h = round(radius * KAPPA)
```

Run it again and print all the orders:

```text
('moveTo', ((41, 50),))
('curveTo', ((41, 17), (68, -10), (101, -10)))
('curveTo', ((134, -10), (161, 17), (161, 50)))
('curveTo', ((161, 83), (134, 110), (101, 110)))
('curveTo', ((68, 110), (41, 83), (41, 50)))
('closePath', ())
```

Now ask Plum for its period:

```python
for node in halfmoon.rich(font, font["period"]).nodes("Regular"):
    print(node.x, node.y)
```

```text
41.0 50.0
41.0 17.0
68.0 -10.0
101.0 -10.0
134.0 -10.0
161.0 17.0
161.0 50.0
161.0 83.0
134.0 110.0
101.0 110.0
68.0 110.0
41.0 83.0
```

Compare the two lists. They hold the same twelve points in the same order. The last curve of the recording comes back to 41, 50, which is the first node, so it isn't listed twice.

I didn't arrange that. I wrote the function, ran it and then looked at the font. Whoever drew Plum's period used a circle with handles at a bit more than half, rounded to whole units, starting at the left and going round against the clock. You've rebuilt a glyph of a published typeface from a center and a radius.

## Step 4: The bullet

A bullet is a bigger circle, higher up. How much bigger is Mira's call, and she says one and a half times the period, sitting at half the height of the lowercase. Both of those can be measured, per master, with the tools from chapter 43 and yesterday:

```python
left, bottom, right, top = halfmoon.box(font, font["period"], master)
radius = round((right - left) / 2 * 1.5)
cy = halfmoon.box(font, font["x"], master)[3] / 2
```

The period's box is as wide as its circle, so half of that is the radius. The top of the `x` is the x-height, and half of that is where the center goes.

One warning about `round`. The Light's period has a radius of 33, and one and a half times 33 is 49.5. `round(49.5)` gives 50, as you'd expect. But `round(2.5)` gives 2. When a number is exactly halfway, Python rounds to the nearest even number, so that a long column of rounded halves doesn't drift upward. It matters rarely. When a result is off by one and you can't see why, remember it.

## The whole script

Here is `draw_circle.py`. `halfmoon.py` gains `KAPPA` and `circle`.

```python
# Draws a bullet in every empty master of the current glyph:
# one and a half times the period, centered at half the x-height.
import halfmoon
from fly import fl
from fly.pens import FlPen, layer_of
from fly.tr.proxy.fl.objects.glyph import pGlyph

MASTERS = ["Light", "Regular", "Bold"]
TIMES_PERIOD = 1.5


def main():
    font = fl.CurrentFont()
    glyph = pGlyph()
    for master in MASTERS:
        if glyph.contours(master):
            print(f"{master}: already has outlines, skipped")
            continue
        layer = layer_of(glyph.fl, master)
        left, bottom, right, top = halfmoon.box(font, font["period"], master)
        radius = round((right - left) / 2 * TIMES_PERIOD)
        cx = layer.advanceWidth / 2
        cy = halfmoon.box(font, font["x"], master)[3] / 2
        with FlPen(layer, notify="Draw bullet") as pen:
            halfmoon.circle(pen, cx, cy, radius)
        print(f"{master:<9}radius {radius:>4}  center {cx}, {cy}")


main()
```

With `bullet` in the Glyph window:

```text
Light    radius   50  center 250.0, 237.0
Regular  radius   90  center 250.0, 239.0
Bold     radius  114  center 250.0, 241.0
```

Check it with your own tools. `anatomy.py` should report one closed contour of 12 nodes. The node count from chapter 42 should say 4 on the line and 8 handles, the price of four curves. `check_direction.py` should find nothing wrong.

Two things about this bullet aren't finished, and I'd rather say so than have you find out at the printer. It sits in the middle of a glyph 500 units wide, which is far too much room for it. The width came from chapter 40's script and has nothing to do with bullets. Spacing is the subject of Part 4. And it has no Unicode value yet, so typing a bullet in a text won't find it. Chapter 23 told you what that number is for, and Part 5 will set it from a script.

Mira looks at the three masters. The bullets grow with the weight, as the periods do. She sends a page to the publisher's designer with a list of ingredients on it.

## What you learned

`curveTo` takes two handles and an end point, where a handle's direction is the curve's heading at that node and its length is how long the heading holds. For a quarter of a circle the handles are 0.5523 of the radius, kept in a named constant. Round the numbers you work out before they become nodes, and remember that `round` sends an exact half to the even neighbor. A measuring pen lets you try a shape and judge it by a number before any font is touched.

## Try it yourself

1. Write `oval(pen, cx, cy, rx, ry)` for a shape with different radii across and up. It needs two handle lengths, one from each radius. Draw the outer contour of Plum's `o` with it: the box is 38, −10 to 482, 488. Compare your twelve points with the font's, from chapter 41. The font's contour may start at a different node from yours, so match the points by position, not by their place in the list. The four on-curve nodes match. The handles don't: the font's are longer than yours by more than ten units each. Divide one of the font's handle lengths by its radius. What does a share bigger than 0.5523 do to the shape, and why might a type designer want that in an `o`?
2. Use `AreaPen` to find out how much of an `o`-sized box an oval fills. Draw `oval` and `rect` with the same sides into two measuring pens and divide. The answer is the same for every oval. Multiply it by four and you'll know the number.
3. Change `TIMES_PERIOD` to 2, undo the bullets and draw again. Then print the three radii without drawing, by swapping `FlPen` for a pen that only listens. What did you have to change, and what could stay?

## Next

Three periods in a row make an ellipsis, and Plum's three masters space them differently. Chapter 49 draws shapes in a loop, and to do it you'll count with `range`.
