---
this_file: src_docs/md/part3-shapes/050-move-scale-slant.md
---

# 50. Move, scale, slant

Friday. The cookbook's part titles are set in Bold capitals: SOUPS, then a dash, then STEWS. The art director has circled the dash on the proof and written next to it: "Hangs low. Can it sit in the middle?"

She's right, and it isn't a mistake in Plum. A hyphen is drawn for lowercase text, so it sits near the middle of the x-height. Between capitals it looks as if it slipped. Type families solve this with a second set of dashes that sit higher, and the usual name for one is the old name plus `.case`.

Mira could draw three rectangles; she knows how since chapter 46. But the dashes exist already, with the right length and the right weight in every master. All a raised dash needs is the old outline, moved up. Today you'll take an outline that's there and put it through a rule that changes every point: up, bigger, mirrored, slanted.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `box`, `rich` and `set_width`.
- Three new empty glyphs: `hyphen.case`, `endash.case` and `emdash.case`. Put the three names in a text file and run **Add Glyphs From List**.

Steps 1 to 5 use no font at all, so you can see every number. They ran in plain Python. Step 6 and the section after it were not run in FontLab 9.

## Step 1: A rule for points

Here is Plum's hyphen in the Regular, as a recording. It's a rectangle, 236 units long and 48 thick:

```python
from fly.pens import RecordingPen

hyphen = RecordingPen()
hyphen.moveTo((56, 246))
hyphen.lineTo((292, 246))
hyphen.lineTo((292, 294))
hyphen.lineTo((56, 294))
hyphen.closePath()
```

Now the rule. The pens call it a **transform**:

```python
from fly.pens import Transform

up = Transform().translate(0, 74)
print(up)
print(up.transformPoint((56, 246)))
```

```text
<Transform [1 0 0 1 0 74]>
(56, 320)
```

`Transform()` with nothing after it is the rule that changes nothing. `.translate(0, 74)` makes a new rule from it: add 0 to every x and 74 to every y. "Translate" is the mathematician's word for shift. `transformPoint` tries the rule on one point, and the point comes back 74 higher.

A transform prints as six numbers. The last two are the shift. You'll see what the first four do in a moment.

## Step 2: Put the rule between two pens

A recording can do more than show its orders. It can give them again, to any other pen: `recording.replay(pen)` plays the list back, order by order, as if you were drawing a second time. And a `TransformPen` is a pen that stands in the middle. It takes each order, applies the rule to the points, and passes the order on to the pen behind it:

```python
from fly.pens import TransformPen

raised = RecordingPen()
hyphen.replay(TransformPen(raised, up))
for order in raised.value:
    print(order)
```

```text
('moveTo', ((56, 320),))
('lineTo', ((292, 320),))
('lineTo', ((292, 368),))
('lineTo', ((56, 368),))
('closePath', ())
```

Read the middle line from the inside out. `raised` is the pen at the end. `TransformPen(raised, up)` is a pen that shifts and then hands over to `raised`. And `hyphen.replay(...)` plays the old orders into that. The x values are untouched and every y is 74 more.

The pen at the end doesn't have to be a recording. Put an `FlPen` there and the raised hyphen lands in a glyph. That's step 6. Until then I'll use a short function that shows where the four corners go:

```python
def corners(rule):
    out = RecordingPen()
    hyphen.replay(TransformPen(out, rule))
    print([order[1][0] for order in out.value[:-1]])
```

`order[1]` is the tuple of points in an order, and `[0]` takes the first of them. The slice `[:-1]` leaves out the `closePath`, which has no points.

## Step 3: Bigger, flatter, mirrored

`scale` multiplies:

```python
corners(Transform().scale(2))
```

```text
[(112, 492), (584, 492), (584, 588), (112, 588)]
```

The hyphen is twice as long and twice as thick. It has also moved: it began at 56 and now begins at 112. Scaling multiplies every coordinate, so everything moves away from the point 0, 0, the origin of the glyph. A shape that should grow in place needs a shift as well, and step 5 comes back to that.

Give `scale` two numbers and the two directions get different treatment:

```python
corners(Transform().scale(1, 0.5))
```

```text
[(56.0, 123.0), (292.0, 123.0), (292.0, 147.0), (56.0, 147.0)]
```

Same length, half the thickness, and half the height above the baseline too. The numbers have turned into floats, because 0.5 is one.

And a negative number mirrors:

```python
corners(Transform().scale(-1, 1))
```

```text
[(-56, 246), (-292, 246), (-292, 294), (-56, 294)]
```

Every x has changed its sign. The hyphen now lies to the left of the origin, outside its glyph. Something else has happened that the corners don't show. Ask the `AreaPen` from chapter 47:

```python
from fly.pens import AreaPen

before = AreaPen()
hyphen.replay(before)
after = AreaPen()
hyphen.replay(TransformPen(after, Transform().scale(-1, 1)))
print(before.value, after.value)
```

```text
11328.0 -11328.0
```

The area has changed its sign. The contour ran counter-clockwise and its mirror image runs clockwise, as the hands of a clock do in a mirror. In chapter 45 direction decided what's black and what's a hole. A mirrored glyph needs every contour reversed afterwards, and a script that forgets this makes glyphs that look fine alone and go wrong where shapes overlap.

## Step 4: Slant, and a unit that isn't degrees

An oblique is a slanted roman, and twelve degrees is a common slant. `skew` does it:

```python
corners(Transform().skew(12))
```

```text
[(-100.42154245074886, 246.0), (135.57845754925114, 246.0), (105.05718097349526, 294.0), (-130.94281902650474, 294.0)]
```

No error, and nonsense. The hyphen has jumped 156 units to the left, and its top is further left than its bottom, so it leans backwards.

The number was read, but not as degrees. `skew` and `rotate` measure angles in **radians**, the unit mathematicians prefer, in which half a turn is 3.14159 and a bit. Twelve radians is nearly two full turns. Nothing in Python can know that you meant degrees, so there's no complaint. This is the silent kind of mistake again, and the cure is the same as always: look at the numbers that come out.

Python converts for you. The tool lives in a module that comes with Python, called `math`:

```python
import math

print(math.radians(12))
corners(Transform().skew(math.radians(12)))
```

```text
0.20943951023931956
[(108.28891417082545, 246.0), (344.2889141708254, 246.0), (354.4916291309865, 294.0), (118.4916291309865, 294.0)]
```

That's a slant. The bottom edge has moved 52 units to the right and the top edge 62: the higher a point, the further it goes. The y values are untouched.

The long decimals are honest, but a font wants whole numbers. There's a pen for that as well, and it goes in the chain like the other one:

```python
from fly.pens import RoundingPen

out = RecordingPen()
hyphen.replay(TransformPen(RoundingPen(out), Transform().skew(math.radians(12))))
print([order[1][0] for order in out.value[:-1]])
```

```text
[(108, 246), (344, 246), (354, 294), (118, 294)]
```

Three pens in a row now: slant, then round, then record.

## Step 5: Two rules in one, and which goes first

Rules can be chained with dots. The order matters, and it's the opposite of what you'd guess:

```python
print(Transform().translate(100, 0).scale(2))
corners(Transform().translate(100, 0).scale(2))
print(Transform().scale(2).translate(100, 0))
corners(Transform().scale(2).translate(100, 0))
```

```text
<Transform [2 0 0 2 100 0]>
[(212, 492), (684, 492), (684, 588), (212, 588)]
<Transform [2 0 0 2 200 0]>
[(312, 492), (784, 492), (784, 588), (312, 588)]
```

In the first chain the corner 56 became 212. That's 56 times 2, plus 100: scaled first, then shifted, though `translate` is written first. In the second chain 56 became 312, which is 56 plus 100, times 2. The rule written **last** touches the point **first**. Read a chain from right to left.

You can see it in the six numbers too. The first four hold the scaling and slanting, the last two the shift, and in the second chain the shift of 100 was itself doubled to 200.

I don't trust myself to remember the direction. I try a chain on one point with `transformPoint` before I let it near a font.

## Step 6: Raise the dashes

How far up? The art director said "in the middle", so work it out: the middle of the capitals minus the middle of the dash. `halfmoon.box` gives both.

```python
cap_top = halfmoon.box(font, font["H"], master)[3]
left, bottom, right, top = halfmoon.box(font, font["hyphen"], master)
shift = round(cap_top / 2 - (bottom + top) / 2)
```

In the Regular that's 344 minus 270, which is 74.

The source outline comes out of FontLab with `draw`, the reader that belongs to the pens. It's the opposite of `FlPen`: it walks a layer and gives the orders to any pen you hand it. Then the chain is the one from step 2, with an `FlPen` at the end:

```python
recording = RecordingPen()
draw(layer_of(source.fl, master), recording)
with FlPen(target_layer, notify="Raise dash") as pen:
    recording.replay(TransformPen(pen, Transform().translate(0, shift)))
```

A pen doesn't carry the advance width, so the script copies that with `set_width` from chapter 49. The whole of it is below.

## The whole script

Save this as `raise_dashes.py`.

```python
# Makes raised copies of the dashes for setting between capitals.
# The target glyphs must exist and be empty: hyphen.case and so on.
import halfmoon
from fly import fl
from fly.pens import FlPen, RecordingPen, Transform, TransformPen, layer_of
from fly.pens.fontlab import draw

MASTERS = ["Light", "Regular", "Bold"]
DASHES = ["hyphen", "endash", "emdash"]
SUFFIX = ".case"


def raise_copy(font, name, master):
    source = halfmoon.rich(font, font[name])
    target = halfmoon.rich(font, font[name + SUFFIX])
    if target.contours(master):
        print(f"{target.name} {master}: already has outlines, skipped")
        return
    cap_top = halfmoon.box(font, font["H"], master)[3]
    left, bottom, right, top = halfmoon.box(font, font[name], master)
    shift = round(cap_top / 2 - (bottom + top) / 2)
    source_layer = layer_of(source.fl, master)
    target_layer = layer_of(target.fl, master)
    recording = RecordingPen()
    draw(source_layer, recording)
    with FlPen(target_layer, notify="Raise dash") as pen:
        recording.replay(TransformPen(pen, Transform().translate(0, shift)))
    halfmoon.set_width(target, target_layer, source_layer.advanceWidth, "Fit dash")
    print(f"{target.name:<13}{master:<9}up {shift}")


def main():
    font = fl.CurrentFont()
    for name in DASHES:
        for master in MASTERS:
            raise_copy(font, name, master)


main()
```

```text
hyphen.case  Light    up 74
hyphen.case  Regular  up 74
hyphen.case  Bold     up 74
endash.case  Light    up 74
endash.case  Regular  up 74
endash.case  Bold     up 74
emdash.case  Light    up 74
emdash.case  Regular  up 74
emdash.case  Bold     up 74
```

Nine times 74. I expected three different numbers and went to check. In Plum the dashes get thicker from Light to Bold, 28 units, then 48, then 84, but they thicken around the same middle line, 270, and the capitals are 688 tall in all three masters. So the sum comes out the same each time. The script still works it out per master, because the next family won't be so regular.

Check with `bounds.py`: `hyphen.case` in the Regular should have a box from 56, 320 to 292, 368 and a width of 348. Then type `H`, `hyphen.case`, `H` in a text and look.

Run it from a Font window, as in chapter 49, and expect two steps in **Edit > Undo** for each master of each glyph. That's how the pen is built.

Mira sends the art director a line of capitals with the new dashes. The answer is a thumbs-up and a question: "How do I type those?" It's the same question the leader dots got. A `.case` glyph has no Unicode value of its own. It's meant to be swapped in by an OpenType feature when text is set in capitals, and features are Part 5. Mira writes "case feature" on a sticky note and puts it next to the screen.

## Move what's already there

Everything above made a **copy**. The pens always add: put a shifted hyphen into the hyphen's own layer and you have two hyphens, one on top of the other. Sometimes you want the original to move, and that takes another tool.

The fontlabapp package has one, built for its own panels. It takes the same six numbers a transform prints, as a plain tuple, and it moves the nodes in place as one Undo step. The listing below follows the package's source and was not run, so treat it as a sketch to try on the practice font and nowhere else:

```python
import fly.ap.contours.transform.model as transform_model
import fly.ap.contours.writer as outline_writer

matrix = (1, 0, 0, 1, 0, 12)      # the six numbers: shift up by 12
rows = transform_model.transform_changes(layer, matrix, False, "")
edits = [row.edit for row in rows if row.edit is not None]
outline_writer.apply_work([(glyph.fl, layer, edits)], "Shift up 12", facts,
                          transform_model.TransformEditor())
```

`facts` is what `history.scan_auto_facts(package)` returns, as in `set_width`. The tool leaves the advance width alone and it skips components, so a glyph built from other glyphs stays where it is. By the package's source it also refuses a glyph that automatic glyphs borrow, unless `allow_bases=True` is added to the call. Chapter 55 comes back to that keyword.

## What you learned

A transform is a rule that turns one point into another: `translate` shifts, `scale` multiplies, `skew` slants. A `TransformPen` stands between two pens and applies the rule to everything that passes, so reading an outline with `draw` and replaying it through a transform makes a changed copy. Scaling works from the origin, a negative scale mirrors and flips the direction, and angles are in radians, which `math.radians` makes from degrees. In a chain of rules the last one written acts first.

## Try it yourself

1. Mirror the hyphen in place. The rule is `Transform().translate(348, 0).scale(-1, 1)`, where 348 is the hyphen's width. Before you run it, read the chain from right to left and work out where the corner 56, 246 goes. Then check with `corners`. Why does a mirrored hyphen look the same as the hyphen, and what's different about it all the same?
2. Scale the hyphen to twice its size without letting it move away: the middle of the result should be where the middle of the original was, at 174, 270. You need a `scale(2)` and one `translate`. Work out the shift on paper first.
3. Make a slanted copy. Add an empty glyph `hyphen.slant` and change `raise_dashes.py` into a script that replays the hyphen through `skew(math.radians(12))` and a `RoundingPen`. Where does the `RoundingPen` go in the chain, and what would be lost if you rounded before slanting?

## Next

Ines wants the small caps to stop being boxes. Chapter 51 starts each of them as a copy of its capital, and shows the difference between copying a thing and giving it a second name.
