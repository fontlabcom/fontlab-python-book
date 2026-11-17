---
this_file: src_docs/md/part3-shapes/046-draw-a-rectangle.md
---

# 46. Draw a rectangle

Monday of the ninth week. The publisher's art director wants to see a page of the cookbook set with small caps, and Mira has drawn three of them. The other seven exist as names with nothing inside, and an empty glyph prints as a gap. On a proof, a gap looks like a mistake in the text. A plain box the size of a letter looks like what it is: a letter that isn't drawn yet.

So Mira wants a placeholder box in each empty small cap. She could draw seven boxes in three masters by hand, twenty-one rectangles, and she'd rather not.

For five chapters your scripts have read outlines. Today one draws. The tool for it is called a pen, and it works the way you'd tell a child to draw a square without lifting the pencil: put the point here, draw to there, to there, to there, and back home.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `anatomy.py` and `check_direction.py`.
- The empty `e.sc` open in a Glyph window. Its width is 500 in each master, from chapter 40.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. The pen commands themselves ran in plain Python, with a pen that draws nowhere, and you'll meet that pen in Step 1.

## Step 1: A pen that only listens

A pen takes four kinds of order. `moveTo` puts the point down at a place, without drawing. `lineTo` draws a straight line from where the pen is to a new place. `curveTo` draws a curve, and it can wait until chapter 48. `closePath` draws back to the start and finishes the contour.

Before you draw in a glyph, give those orders to a pen that draws nothing and only writes down what it's told:

```python
from fly.pens import RecordingPen

pen = RecordingPen()
pen.moveTo((60, 0))
pen.lineTo((440, 0))
pen.lineTo((440, 478))
pen.lineTo((60, 478))
pen.closePath()

for order in pen.value:
    print(order)
```

```text
('moveTo', ((60, 0),))
('lineTo', ((440, 0),))
('lineTo', ((440, 478),))
('lineTo', ((60, 478),))
('closePath', ())
```

Four corners and a closing. The output is the pen's notebook, one tuple for each order, and its exact layout needn't concern you. What matters is that nothing in FontLab changed. A recording pen is safe to play with, and it's a good way to find out what a piece of drawing code does before you let it near a font.

Look at the double parentheses in `pen.moveTo((60, 0))`. The outer pair is the slot, as always. The inner pair makes a tuple, the fixed little row from chapter 35, and here it holds an x and a y. A place on the drawing is one thing, so it travels as one thing. If you write `pen.moveTo(60, 0)`, Python will complain that `moveTo` was given more than it takes, because you handed it two numbers where it wanted one point.

Now read the corners in order. Bottom left, bottom right, top right, top left. Trace it with a finger: you go against the clock. That's deliberate. Friday's rule said the outside of a shape runs counter-clockwise, and a script that draws should follow the convention from its first line.

## Step 2: The same orders, in a glyph

To draw for real, swap the recording pen for one that writes into a layer. It needs to know which layer:

```python
from fly.pens import FlPen, layer_of
from fly.tr.proxy.fl.objects.glyph import pGlyph

glyph = pGlyph()
layer = layer_of(glyph.fl, "Regular")

with FlPen(layer, notify="Draw box") as pen:
    pen.moveTo((60, 0))
    pen.lineTo((440, 0))
    pen.lineTo((440, 478))
    pen.lineTo((60, 478))
    pen.closePath()
```

Run it with `e.sc` in the Glyph window. A rectangle should appear, 380 units wide and 478 tall, standing on the baseline with 60 units of space on each side.

There are three new things here, and the orders in the middle aren't among them. They're the ones you gave the recording pen.

`layer_of(glyph.fl, "Regular")` fetches a layer by its master's name. `glyph.fl` you used once in chapter 29: it's the plain FontLab glyph inside the rich one, which is what the pens package wants. `layer_of` won't guess. Give it a name that isn't there and it raises a `KeyError` that tells you so.

`FlPen(layer, notify="Draw box")` makes a pen for that layer. The `notify` text is the name of the Undo step. Leave it out and the pen still draws, but FontLab isn't told, and you get no Undo and perhaps no redraw. So always give it.

And `with`. You know it from chapter 26, where it opened a file and saw to it that the file was closed. It does the same for a pen. The pen doesn't write each line into the glyph as you give the order. It collects them, and when the `with` block ends it hands the finished contour to FontLab in one go. If something fails inside the block, nothing is written at all.

Check the work with last week's tools. `anatomy.py` should say:

```text
e.sc, layer Regular
  elements: 1
  contour 1: closed, 4 nodes
  total: 1 contours, 4 nodes
```

Press ++cmd+z++ on a Mac, or ++ctrl+z++ on Windows, and the box should go. Press it only once and look. Then redo, or run the script again.

## Step 3: Forget to close

Take out the `pen.closePath()` line, undo the box and run the script:

```text
Traceback (most recent call last):
  File "<string>", line 7, in <module>
  File ".../site-packages/fontlab_pens/fontlab.py", line 240, in __exit__
    self.close()  # raises PenError on an unfinished contour
    ^^^^^^^^^^^^
  File ".../site-packages/fontlab_pens/fontlab.py", line 229, in close
    raise PenError("Unfinished contour: call closePath() or endPath() before close()")
fontlab_pens.base.PenError: Unfinished contour: call closePath() or endPath() before close()
```

Read it the way chapter 38 taught. Last line first: an unfinished contour, and it even tells you the two ways to finish one. Then find the last line of the trail that's in a file of yours. It's line 7, the `with` line. The other frames are inside the pens package, which noticed at the end of the block that you'd started a contour and never ended it.

Then look at the glyph. Nothing was drawn. Three sides of a box would have been an open contour, the very thing you hunted on Thursday, and the pen refused to leave one behind by accident.

Sometimes you want an open contour. For that there's `pen.endPath()`, which finishes a contour without closing it. Whichever you mean, you have to say it.

## Step 4: A function that takes a pen

Twenty-one rectangles are coming, so the four corners should be a function. Here's the design question: what should the function be given? It could take a layer and do everything, making the pen and the Undo step too. But then it could never draw two rectangles in one step, or draw into a recording pen for a test. So give it a pen and let it give orders:

```python
def rect(pen, left, bottom, right, top):
    pen.moveTo((left, bottom))
    pen.lineTo((right, bottom))
    pen.lineTo((right, top))
    pen.lineTo((left, top))
    pen.closePath()
```

Define it in this script. It needs no import, because it doesn't care what kind of pen it gets. Anything that understands `moveTo`, `lineTo` and `closePath` will do. Test it on the pen that only listens:

```python
from fly.pens import RecordingPen

pen = RecordingPen()
rect(pen, 60, 0, 440, 478)
print(len(pen.value))
```

```text
5
```

Five orders, with no font involved. The argument order, left, bottom, right, top, is the order `box` gives its answers in, so the two fit together: whatever `box` measures, `rect` can draw.

Now the three masters. Each has its own layer, and a pen writes to one layer, so you need one pen per master, in a loop:

```python
for master in MASTERS:
    layer = layer_of(glyph.fl, master)
    with FlPen(layer, notify="Draw box") as pen:
        rect(pen, 60, 0, 440, 478)
```

There's one danger left, and it's a new kind for us. Run the script twice and you get two boxes, one on top of the other. They look like one. `anatomy.py` would say two contours, and a font with doubled outlines prints badly. A script that reads can be run a hundred times without harm. A script that draws can't, unless you make it check first. So before it draws into a layer, it should look whether anything is there:

```python
if glyph.contours(master):
    print(master, "already has outlines, skipped")
    continue
```

That guard also means the script can never draw a box over a drawn letter. A glyph built from components has no contours of its own and would still get one, so keep to empty glyphs.

## The whole script

Here is `draw_box.py`. It defines `rect` from Step 4 at the top, so it runs by itself.

```python
# Draws a placeholder box in every empty master of the current glyph.
from fly.pens import FlPen, layer_of
from fly.tr.proxy.fl.objects.glyph import pGlyph

MASTERS = ["Light", "Regular", "Bold"]
SIDE = 60
TOP = 478


def rect(pen, left, bottom, right, top):
    pen.moveTo((left, bottom))
    pen.lineTo((right, bottom))
    pen.lineTo((right, top))
    pen.lineTo((left, top))
    pen.closePath()


def main():
    glyph = pGlyph()
    drawn = 0
    for master in MASTERS:
        if glyph.contours(master):
            print(f"{master}: already has outlines, skipped")
            continue
        layer = layer_of(glyph.fl, master)
        width = layer.advanceWidth
        with FlPen(layer, notify="Draw box") as pen:
            rect(pen, SIDE, 0, width - SIDE, TOP)
        drawn = drawn + 1
    print(f"{glyph.name}: {drawn} boxes drawn")


main()
```

With `e.sc` holding the box you drew in Regular in Step 2:

```text
Regular: already has outlines, skipped
e.sc: 2 boxes drawn
```

The box's right side isn't typed in. It's worked out from the layer's width, `width - SIDE`, so the box sits in the middle of whatever width the glyph has, with 60 units either side. `layer.advanceWidth` is the drawer you changed in chapter 29. `TOP` is the x-height from chapter 43, a stand-in until Mira decides how tall her small caps are.

Each pen makes its own Undo step, so undoing this run should take one press per master. That is how the pen is built, so see for yourself.

Finish with Friday's check. Run `check_direction.py`:

```text
366 layers checked, 0 wrong.
```

That's three more layers than on Friday, and none of them is wrong, because `rect` goes round against the clock. Mira prints the cookbook page. Where the `e.sc` should be there's a neat black box, and the art director can see what's coming.

Now think of doing the same for `f.sc`, and then for `g.sc`, and you'll feel what's wrong with the script. It does one glyph at a time and you do the walking. Doing every empty small cap in one run is exercise 2, and you have everything you need for it.

## What you learned

A pen draws by orders: `moveTo`, `lineTo` and `closePath`, each place given as an `(x, y)` tuple. `RecordingPen` writes the orders down and touches nothing, and `FlPen` in a `with` block draws them into a layer as one Undo step, named by `notify`. A drawing function should take a pen, so it can be tested without a font and combined with others. A script that draws must check what's already there, because running it twice isn't harmless.

## Try it yourself

1. Change `rect` so that it goes round clockwise, draw a box in an empty glyph and run `check_direction.py`. Then change it back and undo. How many layers were wrong?
2. Make `draw_box.py` work on the whole font: loop over `font.glyphs`, keep the names that end in `.sc`, and use `pGlyph(font, glyph)` in place of `pGlyph()`. Print one line per glyph. Run it twice and check that the second run draws nothing. Then undo the run, so that `e.sc` is again the only small cap with a box. Chapter 51 counts on that.
3. Draw a box into a `RecordingPen` with `rect`, then print only the points, one per line, by taking them out of `pen.value`. Each order is a tuple of a name and a tuple of points. You'll need two indexes, as in chapter 35.

## Next

A box is one contour. The glyph that fonts show when a character is missing is a box with a hole in it, and you now know what makes a hole. Chapter 47 draws it from numbers.
