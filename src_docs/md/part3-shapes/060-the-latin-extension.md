---
this_file: src_docs/md/part3-shapes/060-the-latin-extension.md
---

# 60. The Latin extension, delivered

Friday afternoon of week eleven, nine days after the publisher's letter. In Mira's own Plum the caron and the ogonek are drawn, in all three masters. She'd like to send the Czech and Polish letters off before she goes home.

Your `Plum-practice` doesn't have her drawings. So this chapter does what a studio does when a drawing is late: it makes stand-ins. A caron is close to a circumflex turned over. A dot accent is one dot of the dieresis, set in the middle. Neither is as good as what Mira drew, and both are good enough to build with and to replace later. The ogonek can't be made from anything in the font. It stays on the list, and you'll see the report say so.

There's no new font work in this chapter and very little new Python. You'll take pieces from the last twenty chapters and put them in a row.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, and the Font window in front.
- `halfmoon.py` with `box`, `box_of`, `contours_of` and `circle`.
- `build_accents.py` from chapter 57 and your `accents.txt`, with the three bad lines put right as in exercise 1 of that chapter: `rr` corrected to `r`, a `#` in front of the `ľ` line, and `dotlessi` as the base for `ĩ`. Run `build_accents.py` once more before you start, and say yes, so that it has nothing left to build.

This chapter adds glyphs. Work on the practice copy. The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. The pen results come from running the pens in plain Python.

## Step 1: Turn the builder into a module

Today's script needs the builder from chapter 57 as its last stage. Copying 150 lines into a second file would give you two builders to keep in step, and chapter 33 showed the way out: put the functions in a module.

Save `build_accents.py` under a second name, `accentkit.py`, in the same folder. In `accentkit.py`, delete the last line, the one that says `main()`. Now the file defines everything and does nothing, which is what a module should do when it's imported.

Then replace the whole content of `build_accents.py` with this:

```python
#FLM: Build Accented Letters
import accentkit

accentkit.main()
```

Run it. It should behave as it did this morning: it asks for the recipe file, prints its rows and finds nothing to build. The script is three lines long now, and the work lives in one place.

## Step 2: A caron from a circumflex

Chapter 50 flipped a hyphen left to right with `Transform().scale(-1, 1)`. To flip top to bottom, the minus goes to the second number. A bare `scale(1, -1)` would throw the accent below the baseline, since it turns every height into its negative. To flip the accent in place, add its bottom and its top and move up by that much:

```python
import halfmoon
from fly import fl
from fly.pens import RecordingPen, Transform, TransformPen, layer_of
from fly.pens.fontlab import draw

font = fl.CurrentFont()
left, bottom, right, top = halfmoon.box(font, font["circumflex"], "Regular")
flip = Transform().translate(0, bottom + top).scale(1, -1)
print(bottom, top, flip.transformPoint((250, 614)))
```

```text
539.0 655.0 (250.0, 580.0)
```

The circumflex in the Regular stands between 539 and 655. Its inner point, at 614, lands at 580: as far above the bottom as it used to be below the top.

Record the circumflex and replay it through the flip, as chapter 51 did with the small caps:

```python
source = layer_of(halfmoon.rich(font, font["circumflex"]).fl, "Regular")
recording = RecordingPen()
draw(source, recording)
flipped = RecordingPen()
recording.replay(TransformPen(flipped, flip))
print(flipped.value[:3])
```

```text
[('moveTo', ((134.0, 655.0),)), ('lineTo', ((197.0, 655.0),)), ('lineTo', ((250.0, 580.0),))]
```

It looks right. It isn't. Chapter 50 said it in one sentence that slips the mind: a mirror image runs the other way round. The circumflex ran counter-clockwise, so this caron runs clockwise. Drawn into a glyph it would look fine on its own. On top of a `c` it could punch a white hole where the two overlap, and `check_direction.py` from chapter 45 would name it.

The pens have a filter for this. `ReverseContourPen` passes on every contour it gets with the direction turned around:

```python
from fly.pens import ReverseContourPen

flipped = RecordingPen()
recording.replay(TransformPen(ReverseContourPen(flipped), flip))
print(flipped.value[:3])
```

```text
[('moveTo', ((134.0, 655.0),)), ('lineTo', ((221.0, 539.0),)), ('lineTo', ((280.0, 539.0),))]
```

The same points, walked the other way. Read the pens from the outside in: the drawing is flipped first, then reversed, then recorded. Whenever you mirror an outline once, reverse it once.

## Step 3: A dot from the dieresis

The dot accent, as on the `ż`, needs a dot of the right size at the right height. The dieresis has two. Take the box of one of them, with `box_of` from chapter 45:

```python
dot = halfmoon.contours_of(font, font["dieresis"], "Regular")[0]
left, bottom, right, top = halfmoon.box_of(dot.nodes())
radius = round((right - left) / 2)
height = round((bottom + top) / 2)
print(radius, height)
```

```text
46 581
```

A radius of 46, with its center 581 units up. `halfmoon.circle` from chapter 48 draws it, and the center goes to x 250, the middle of an accent glyph 500 units wide. In the Light the numbers are 27 and 592, in the Bold 63 and 592.

## Step 4: Loops for the new accents

An accent without a loop can't be hung on anything, as chapter 54 showed. The circumflex has its `_top` loop at 250, 478 in every master. The caron is the same shape turned over, and the dot sits on the same middle line, so both get a copy of that loop. The edit is the kind chapter 55 wrote: `("set", "_top", (250, 478))`.

## Step 5: The stages in a row

Here is the plan for the afternoon, as a list:

1. Make two empty glyphs, `caron` and `dotaccent`, 500 wide, with their Unicode values.
2. Draw the flipped circumflex into one and the dot into the other.
3. Give each a `_top` loop.
4. Hand over to the builder.

Each line is a function you could write from an earlier chapter, and `main` calls them in that order. Each stage also has to cope with a second run. If `caron` is in the font already, stage 1 leaves it off its list, and stages 2 and 3 work only on that list. Stage 2 also skips a layer that has an outline, for the day a run is interrupted halfway. Mira will run this on her own Plum, where her drawn caron is waiting, and the script mustn't draw a stand-in on top of it.

## The whole script

```python
#FLM: Extend Latin
# Makes stand-in caron and dotaccent glyphs if the font has none, gives
# them _top anchors, then builds the accented letters from the recipe file.
import accentkit
import fly.ap.anchors.writer as anchors
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.glyphs.creation as creation
import halfmoon
from fly import fl
from fly.pens import FlPen, RecordingPen, ReverseContourPen, Transform, TransformPen
from fly.pens.fontlab import draw

MASTERS = ["Light", "Regular", "Bold"]
WIDTH = 500
MIDDLE = 250
MODEL = "circumflex"
STAND_INS = {"caron": 0x02C7, "dotaccent": 0x02D9}


def draw_caron(font, master):
    left, bottom, right, top = halfmoon.box(font, font[MODEL], master)
    flip = Transform().translate(0, bottom + top).scale(1, -1)
    recording = RecordingPen()
    draw(accentkit.layer_for(font, MODEL, master), recording)
    layer = accentkit.layer_for(font, "caron", master)
    with FlPen(layer, notify="Draw stand-in caron") as pen:
        recording.replay(TransformPen(ReverseContourPen(pen), flip))


def draw_dot(font, master):
    dot = halfmoon.contours_of(font, font["dieresis"], master)[0]
    left, bottom, right, top = halfmoon.box_of(dot.nodes())
    radius = round((right - left) / 2)
    height = round((bottom + top) / 2)
    layer = accentkit.layer_for(font, "dotaccent", master)
    with FlPen(layer, notify="Draw stand-in dot") as pen:
        halfmoon.circle(pen, MIDDLE, height, radius)


def loop_rows(font, names):
    rows = []
    for name in names:
        rich = halfmoon.rich(font, font[name])
        for master in MASTERS:
            model = accentkit.layer_for(font, MODEL, master)
            place = anchors.anchor_points(model)["_top"]
            layer = accentkit.layer_for(font, name, master)
            rows.append((rich.fl, layer, [("set", "_top", place)]))
    return rows


def make_stand_ins(font, package):
    have = {glyph.name for glyph in font.glyphs}
    missing = [name for name in STAND_INS if name not in have]
    if not missing:
        print("caron and dotaccent are in the font. No stand-ins made.")
        return
    specs = []
    for name in missing:
        layers = tuple([(master, WIDTH) for master in MASTERS])
        specs.append(creation.NewGlyph(name=name, layers=layers, unicodes=(STAND_INS[name],)))
    facts = history.scan_auto_facts(package)
    creation.create_glyphs(package, specs, "Add stand-in accents", facts)

    for name in missing:
        for master in MASTERS:
            if halfmoon.contours_of(font, font[name], master):
                continue
            if name == "caron":
                draw_caron(font, master)
            else:
                draw_dot(font, master)

    work = loop_rows(font, missing)
    facts = history.scan_auto_facts(package)
    anchors.require_safe(work, facts)
    anchors.apply_work(work, "Add loops to stand-in accents", facts)
    print(f"Stand-ins made: {', '.join(missing)}.")


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    if font[MODEL] is None or font["dieresis"] is None:
        halfmoon.tell("This font has no circumflex or no dieresis to copy from.")
        return
    make_stand_ins(font, scripting.current_package())
    accentkit.main()


main()
```

`0x02C7` is a number written in base 16, the way Unicode charts print it. It's the same number as 711. Python takes either. With the `0x` form you can copy a value from a chart without doing sums.

Run it, choose `accents.txt`, and the Output panel shows this. I've left out the 17 rows that say `fine` or `auto`.

```text
Stand-ins made: caron, dotaccent.
37 recipes read.
Zdotaccent   new   Z + dotaccent: -7 210, 16 210, 16 210
zdotaccent   new   z + dotaccent: -60 0, -52 0, -22 0
Ccaron       new   C + caron: 48 210, 61 210, 61 210
ccaron       new   c + caron: -44 0, -35 0, -35 0
Dcaron       new   D + caron: 73 210, 83 210, 83 210
Ecaron       new   E + caron: -29 210, -7 210, -7 210
ecaron       new   e + caron: -24 0, -15 0, 3 0
Ncaron       new   N + caron: 52 210, 79 210, 79 210
ncaron       new   n + caron: 0 0, 12 0, 12 0
Rcaron       new   R + caron: -7 210, 12 210, 12 210
rcaron       new   r + caron: -115 0, -90 0, -90 0
Scaron       new   S + caron: -22 210, -2 210, -2 210
scaron       new   s + caron: -74 0, -65 0, -35 0
Tcaron       new   T + caron: -21 210, -1 210, -1 210
Zcaron       new   Z + caron: -7 210, 16 210, 16 210
zcaron       new   z + caron: -60 0, -52 0, -22 0
16 to build, 0 to move, 13 fine as they are, 4 automatic.

4 recipes need a look:
  line  5  Aogonek: no glyph named ogonek for the accent
  line  6  aogonek: no glyph named ogonek for the accent
  line  9  Eogonek: no glyph named ogonek for the accent
  line 10  eogonek: no glyph named ogonek for the accent

Accents to draw, and the recipes waiting for each:
  ogonek       4
```

Say yes, and sixteen letters appear at the end of the Font window. Your rows may come in another order if your file does. The `Zcaron` and the `Zdotaccent` have the same shifts, as they should: both accents hang from the same peg by the same loop.

Run the script a second time. The first line now says that no stand-ins were made, and the builder finds 29 recipes fine, four automatic and nothing to build.

## What the afternoon produced

The Edit menu has a good many new Undo steps: one for the two empty accents, one for each of the six layers drawn, one for the loops and one for the sixteen letters. To take the afternoon back you'd undo them all, newest first. It's simpler to close the practice font without saving.

Count what this part has put into the practice font from recipes and accents: `nacute` in chapter 53, nine letters in chapter 56, three in chapter 57, two stand-in accents and sixteen letters today. Thirty-one glyphs. The last sixteen took about as long as reading this page.

Run `inventory.py` from chapter 20 as well. Its glyph count is up by 18 since this morning, and none of the new glyphs is empty.

Czech is complete, apart from the `ď` and the `ť`, whose caron has a different form that Mira has to draw. Polish lacks four letters with an ogonek and the `Ł` and `ł`, which are drawn letters. The report names the four, and Mira knows about the others. In her own Plum, with her ogonek in place, the same script and the same file report nothing to look at.

She sends the fonts to the publisher at ten to five.

Before she goes, Mira crosses out one more line on Oskar's sheet: *Rebuild the accented letters from the base letters and the accents.* That makes seven of eleven. The next one down reads *Make the left sidebearing of the d, q and g match the o*, and nobody in the studio has wanted to touch the spacing since Oskar left.

## What you learned

A script that has grown useful becomes a module: move its functions to a file that does nothing on import, and keep a three-line script that calls it. A long job is a row of stages, each a function that copes with being run again. Flipping an outline reverses its direction, and `ReverseContourPen` turns it back. A stand-in built with anchors can be replaced by a better drawing later without touching the letters that use it, and a number can be written in base 16 with `0x` in front.

## Try it yourself

1. Run `check_direction.py` from chapter 45. It should have nothing to say about `caron` or `ccaron`. Then take `ReverseContourPen` out of `draw_caron`, delete the `caron` glyph and the fourteen letters that use it by hand, run `extend_latin.py` again, and run the check once more. What does it report? Put the pen back afterwards.
2. Open `ccaron` and `ecircumflex` side by side in the Bold. The stand-in caron is as wide as the circumflex. A drawn caron is usually a little narrower and steeper. Write down two things you'd tell Mira to change, and notice that she can change them in one glyph.
3. Add `"macron": 0x00AF` to `STAND_INS` and write `draw_macron`: a rectangle with `halfmoon.rect` from chapter 46, as wide as the circumflex's box and as thick as the hyphen. Add `Ā Amacron A macron` and `ā amacron a macron` to the recipe file. You'll have to change the `if` and `else` in `make_stand_ins` into a ladder with `elif`.

## Next

Part 3 ends here. The font has its letters, and each one has a width that somebody chose by eye, years ago. Chapter 61 opens Part 4 with the question Oskar's sheet has been asking all along: how much white is there on each side of a letter, and how do you read it with a script?
