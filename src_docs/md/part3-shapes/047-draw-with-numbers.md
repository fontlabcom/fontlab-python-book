---
this_file: src_docs/md/part3-shapes/047-draw-with-numbers.md
---

# 47. Draw with numbers

Tuesday. Every font has a glyph called `.notdef`. It's the one a program shows when the text asks for a character the font doesn't have, and you've seen it a thousand times as a little empty box in the middle of a word. Plum's is a box with four triangles cut out of it, like the back of an envelope.

Ines doesn't like it. Halfmoon's house style is a plain frame, a rectangle with a rectangular hole, and the frame should be as heavy as the letters around it: thin in the Light, thick in the Bold. "As heavy as the `l`," she says. "Exactly as heavy."

That last word is why this is a job for a script. Mira could draw a frame by eye in three masters. But the rule isn't "about that thick". It's a measurement taken from one glyph and used in another, three times. Yesterday you typed the corners of a box as numbers. Today the numbers come from the font.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `box` and `rect`.
- A new empty glyph called `notdef.new`. Make it the way chapter 40 did: put that one name in a text file and run **Add Glyphs From List**. It will be 500 wide in all three masters.

We draw into a new glyph and leave the real `.notdef` alone, so that Mira can put the two side by side before anything is replaced. The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. The arithmetic ran in plain Python with a measuring pen, which you'll use too.

## Step 1: Measure the stem

How heavy is the `l`? In Plum it's a plain rectangle of four nodes, so its bounding box is the stem itself. Chapter 43 gave you the tool:

```python
import halfmoon
from fly import fl

font = fl.CurrentFont()
for master in ["Light", "Regular", "Bold"]:
    left, bottom, right, top = halfmoon.box(font, font["l"], master)
    print(master, right - left)
```

```text
Light 34.0
Regular 82.0
Bold 132.0
```

That's three stems and nobody had to type them. If Mira makes the Bold bolder next month, the script will measure the new stem and the frame will follow. A number you type goes out of date when the font changes, and a number you measure doesn't.

Put it in the module, since "how heavy is this master" will be asked again:

```python
def stem(font, master="Regular"):
    left, bottom, right, top = box(font, font["l"], master)
    return right - left
```

It leans on a fact about this font, that the `l` is a bare stem. In a font whose `l` has a tail or serifs it would give the wrong answer, and a comment above the function should say so.

## Step 2: A box inside a box

The frame is two rectangles. The outer one we can write down as we did yesterday: 50 units in from each side of a 500 glyph, standing on the baseline, as tall as a capital. The inner one is the same box, moved in by the stem on all four sides.

Moving in on all four sides is called an inset, and it's four small sums:

```python
def inset(sides, amount):
    left, bottom, right, top = sides
    return left + amount, bottom + amount, right - amount, top - amount
```

It takes a box as one tuple and hands back a new one. The left and bottom grow by the amount, and the right and top shrink by it. Try it:

```python
outer = (50, 0, 450, 688)
inner = halfmoon.inset(outer, 82)
print(inner)
```

```text
(132, 82, 368, 606)
```

Now draw the inner box. `rect` wants a pen and four numbers. You have a pen and one tuple. The obvious thing fails:

```python
from fly.pens import RecordingPen

pen = RecordingPen()
halfmoon.rect(pen, inner)
```

```text
TypeError: rect() missing 3 required positional arguments: 'bottom', 'right', and 'top'
```

Read it closely, because it tells you what Python did. It put the pen in the first slot and the whole tuple in the second, the one called `left`, and then found three slots with nothing in them. A tuple of four numbers is one thing, and it went into one slot.

You could unpack it yourself, with `left, bottom, right, top = inner` and then four names in the call. Python has a shorter way:

```python
halfmoon.rect(pen, *inner)
```

The star in front of `inner` says: open this up and deal its items into the slots, one each. Picture a hand of four cards. Without the star you put the whole hand in one slot, and with it you deal one card to each of four. The call does the same as `halfmoon.rect(pen, 132, 82, 368, 606)`.

The star only works inside the parentheses of a call, and the count has to fit. If you deal a tuple of three into four slots you'll get a "missing" complaint again, about one argument this time.

## Step 3: The hole runs the other way

On Friday you learned what makes a hole: a contour inside another, running against it. `rect` goes round counter-clockwise. For the hole we need one that goes clockwise. That's a job for a default argument from chapter 34. In `halfmoon.py`, change `rect` to this:

```python
def rect(pen, left, bottom, right, top, clockwise=False):
    corners = [(left, bottom), (right, bottom), (right, top), (left, top)]
    if clockwise:
        corners.reverse()
    pen.moveTo(corners[0])
    for corner in corners[1:]:
        pen.lineTo(corner)
    pen.closePath()
```

Every call written yesterday still works, because they don't mention `clockwise` and it stays `False`. The four corners are now a list of tuples. `corners.reverse()` turns the list back to front where it stands, and the same four corners visited in the opposite order go round the opposite way. The pen moves to the first corner and draws to the others. `corners[1:]` is a slice, which you've used to take the first few items of a list. With the number before the colon it means "from item 1 to the end", which is everything but the first.

Does it work? You can't see a recording, and you don't want to draw in the font to find out. There's a third kind of pen for this, one that measures. `AreaPen` adds up the area inside what you draw, and it counts a counter-clockwise contour as positive and a clockwise one as negative:

```python
from fly.pens import AreaPen

outer = (50, 0, 450, 688)
inner = halfmoon.inset(outer, 82)

pen = AreaPen()
halfmoon.rect(pen, *outer)
print(pen.value)
halfmoon.rect(pen, *inner, clockwise=True)
print(pen.value)
```

```text
275200.0
151536.0
```

The outer box is 400 by 688, which is 275,200 square units. Then the hole is drawn, and the total goes down, to 151,536. That's the area of the black frame alone, and it went down because the hole ran against the box.

Now take out `clockwise=True` and run it again:

```text
275200.0
398864.0
```

The total went up. Both contours ran the same way, the pen counted the middle twice, and in a font the middle would print black. You'd have a solid box where you meant a frame. The measuring pen caught it in two lines, with no font involved.

So that's three pens now, and `rect` served all three without changing a word. One listens, one measures and one draws. That's what yesterday's decision bought us, the one to hand the function a pen.

## Step 4: Two contours, one pen

Yesterday each `with` block held one rectangle. A pen can take as many contours as you like before the block ends, and they all go into the glyph together, as one element and one Undo step:

```python
with FlPen(layer, notify="Draw frame") as pen:
    halfmoon.rect(pen, *outer)
    halfmoon.rect(pen, *inner, clockwise=True)
```

That's the right grouping here. A frame is one thing to the designer, so one press of Undo should take all of it away, and not leave a solid box behind.

## The whole script

Here is `notdef.py`. `halfmoon.py` gains `stem` and `inset`, and `rect` gains its sixth argument.

```python
# Draws the Halfmoon frame in every empty master of the current glyph.
# The frame is as heavy as the stem of the l in that master.
import halfmoon
from fly import fl
from fly.pens import FlPen, layer_of
from fly.tr.proxy.fl.objects.glyph import pGlyph

MASTERS = ["Light", "Regular", "Bold"]
SIDE = 50


def main():
    font = fl.CurrentFont()
    glyph = pGlyph()
    for master in MASTERS:
        if glyph.contours(master):
            print(f"{master}: already has outlines, skipped")
            continue
        layer = layer_of(glyph.fl, master)
        cap_top = halfmoon.box(font, font["H"], master)[3]
        weight = halfmoon.stem(font, master)
        outer = (SIDE, 0, layer.advanceWidth - SIDE, cap_top)
        inner = halfmoon.inset(outer, weight)
        with FlPen(layer, notify="Draw frame") as pen:
            halfmoon.rect(pen, *outer)
            halfmoon.rect(pen, *inner, clockwise=True)
        print(f"{master:<9}stem {weight:>5}  hole {inner}")


main()
```

With `notdef.new` in the Glyph window:

```text
Light    stem  34.0  hole (84.0, 34.0, 416.0, 654.0)
Regular  stem  82.0  hole (132.0, 82.0, 368.0, 606.0)
Bold     stem 132.0  hole (182.0, 132.0, 318.0, 556.0)
```

Only one number in the script is typed in, and that's `SIDE`. The frame's top is the top of the `H` in that master, taken from `box` with `[3]`, the fourth item. Its weight is the stem of the `l`, and its right side comes from the glyph's own width. Everything else is worked out from those.

Check it three ways, with tools you've built. `anatomy.py` should report one element with two closed contours of four nodes each. `check_direction.py` should count three more layers and find none wrong, because the biggest contour in each runs against the clock. And your eyes: flip through the masters in the Glyph window, and the frame should thicken as you go, by the same amount that the `l` does.

Mira puts `.notdef` and `notdef.new` next to each other in a text and shows Ines. "The new one," Ines says. Swapping them isn't a job for this book. It means deleting outlines from a glyph that every export uses, and Mira will do it by hand, in the Glyph window, after a proof.

## What you learned

Numbers that come from the font stay right when the font changes, so measure what you can and type only what you must. A star in a call, `*inner`, deals the items of a tuple into separate slots. A pen can hold several contours, and they become one element and one Undo step. `AreaPen` measures what's drawn into it, positive one way round and negative the other, so you can test a drawing function without a font.

## Try it yourself

1. In the Bold the hole is 136 units wide. Make the stem absurd: call `halfmoon.inset(outer, 250)` and look at the tuple. What's wrong with it? Add a check to `notdef.py` that refuses to draw, with a clear message, when the hole would have no width or no height.
2. Use `AreaPen` to answer a designer's question: what share of the frame's outer box is black, in each master? Divide the frame's area by the box's area and print it as a percentage with one decimal. You need no font for this, only the three stems.
3. Draw Plum's present `.notdef` into a `RecordingPen`: a box and four triangles. To do that, write `triangle(pen, a, b, c)` in the style of `rect`, taking three points. Should it take a `clockwise` argument, or should the caller pass the points in the order it wants? Decide, and say why in a comment.

## Next

So far the pen has only drawn straight lines. The period at the end of this sentence is round. Chapter 48 teaches the pen its fourth order, `curveTo`, and draws a circle with it.
