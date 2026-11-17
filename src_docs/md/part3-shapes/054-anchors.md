---
this_file: src_docs/md/part3-shapes/054-anchors.md
---

# 54. Anchors

Thursday. Mira prints yesterday's *koń* large, in all three weights, and pins the sheet next to the window. In the Light and the Regular she'd sign it off. In the Bold the acute over the `n` sits a little to the right of where the acute over the `o` sits. It's not much, but once she's seen it she can't look anywhere else.

She opens the Bold `n` to see whether the letter itself is lopsided, and notices something she has scrolled past for weeks: a few small marks in the glyph that aren't part of the outline. One sits on the x-height line, a little left of the middle. It has a name next to it: `acute`.

Whoever drew Plum had already written down where the acute goes on an `n`. Yesterday you and I worked that place out from the `o`, with some care, and got it nearly right. The answer was in the glyph the whole time.

Those marks are **anchors**. Today you read them, learn what the names mean, and check the whole font against them.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The `nacute` from chapter 53. If you skipped it, the last script still runs. It finds one glyph less to complain about.
- Nothing in the font changes today.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. So was every position and count.

## Step 1: Ask a layer for its anchors

An anchor is a named point in a layer. It has no outline and doesn't print. Fly reads all the anchors of a layer in one call:

```python
import fly.ap.anchors.writer as anchors
from fly import fl
from fly.pens import layer_of

font = fl.CurrentFont()
layer = layer_of(fl.flGlyph(font["n"], font), "Regular")
points = anchors.anchor_points(layer)
for name in sorted(points):
    print(name, points[name])
```

```text
acute (242.0, 478.0)
bottom (282.0, 0.0)
top (262.0, 478.0)
topLeft (100.0, 200.0)
```

`anchor_points` hands back a dictionary. The keys are the anchor names, and each value is a pair: across and up. You've had dictionaries with numbers in them and, since Tuesday, with lists. A pair as a value is no different. Ask for one anchor by its name, as you'd ask for any key:

```python
print(points["top"])
x, y = points["top"]
print(y)
```

```text
(262.0, 478.0)
478.0
```

Read the four anchors as notes the designer left on the letter. `top` says: an accent that sits centered above goes here, at 262 across, on the x-height. `bottom` says the same for an accent below, on the baseline. `acute` is 20 units to the left of `top`, and it's there for the accent that leans. `topLeft` you can ignore. It sits at a spot inside the letter where nobody would put anything, and I'd guess it was left over from an experiment.

## Step 2: The other half is on the accent

An anchor on a letter says where an accent should go. It doesn't say which part of the accent should land there. The accent has to answer that itself:

```python
layer = layer_of(fl.flGlyph(font["acute"], font), "Regular")
marks = anchors.anchor_points(layer)
for name in sorted(marks):
    print(name, marks[name])
```

```text
_acute (190.0, 478.0)
_acuteHigh (190.0, 478.0)
```

The names start with an underscore, and that's the whole convention. An anchor with a plain name sits on a letter. The anchor with the same name and an underscore in front sits on an accent. Think of a coat peg on the wall and the loop inside the collar of a coat. `acute` is the peg. `_acute` is the loop. Hang the coat, and the two are in the same place.

The acute's loop is at 190 across, which is near the lower tip of the stroke and nowhere near the middle of its box at 250. That's what the eye did yesterday, and what the box couldn't do.

So the shift is a subtraction: where the peg is, minus where the loop is.

```python
def shift_from_anchors(base_points, mark_points, family):
    bx, by = base_points[family]
    mx, my = mark_points["_" + family]
    return bx - mx, by - my


print(shift_from_anchors(points, marks, "acute"))
```

```text
(52.0, 0.0)
```

242 minus 190 is 52, and 478 minus 478 is 0. I've called the third input `family` because a peg and its loop belong together, and I needed one word for the pair. `"_" + family` builds the loop's name from the peg's name, the same string sum that built `nacute` yesterday.

Now ask for the wrong pair. The `n` has a `top` anchor too:

Run this line on its own, with the function already defined, and the line numbers will be the ones shown:

```python
print(shift_from_anchors(points, marks, "top"))
```

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<string>", line 3, in shift_from_anchors
KeyError: '_top'
```

The `n` has a peg called `top`. The acute has no loop called `_top`, so the dictionary has no such key. The acute hangs on `acute` pegs only. Other accents use `top`: the dieresis, the circumflex, the breve, the ring and the tilde all carry `_top`. A function that's going to be asked about every pair in a font shouldn't fall over at the first pair that doesn't match. Give it a way to say no:

```python
def shift_from_anchors(base_points, mark_points, family):
    if family not in base_points or "_" + family not in mark_points:
        return None
    bx, by = base_points[family]
    mx, my = mark_points["_" + family]
    return bx - mx, by - my
```

## Step 3: Test it on a case you know

Yesterday's lesson was to try a sum on a solved case before trusting it. The `oacute` is solved: its acute is shifted by 50 in the Regular. So ask the anchors of `o`:

```python
def points_of(font, name, master):
    return anchors.anchor_points(layer_of(fl.flGlyph(font[name], font), master))


print(shift_from_anchors(points_of(font, "o", "Regular"), marks, "acute"))
print(shift_from_anchors(points_of(font, "O", "Regular"), marks, "acute"))
```

```text
(50.0, 0.0)
(144.0, 210.0)
```

The first line is 50, to the unit. And look at the second. On Tuesday the accents over capitals all had 210 in their shift, and I said somebody had typed that number 34 times. Nobody did. The capital `O` has its `acute` anchor at the cap height, 688. The acute has its loop at 478. Subtract, and 210 comes out. The same accent glyph lands on a lowercase letter and on a capital, and each letter says how high.

A table of shifts would need one number for every pair. With anchors, every letter says once where it takes accents and every accent says once where it's held. A new accent with one `_top` anchor fits every letter in the font that has a `top`.

## Step 4: What the anchors say about yesterday

Now the question that started the morning. Ask the `n` in all three masters:

```python
for master in ["Light", "Regular", "Bold"]:
    shift = shift_from_anchors(
        points_of(font, "n", master), points_of(font, "acute", master), "acute"
    )
    print(master, shift)
```

```text
Light (40.0, 0.0)
Regular (52.0, 0.0)
Bold (62.0, 0.0)
```

Yesterday's script gave 42, 54 and 72. Two units off in the Light and the Regular, which nobody will ever see. Ten units off in the Bold, which Mira saw from across the room.

Where did the ten come from? In the Bold, the designer pushed the acute over the `o` to the right, to suit the heavy round shape under it. That push was a decision about the `o`. Yesterday's script took the acute's place from the `o` and carried the push over to the `n`, which has a straight stem and a shoulder and didn't want it. I said yesterday that borrowing from a model works while the letters are alike. In the Bold, `o` and `n` weren't alike enough.

Leave your `nacute` as it is for now. Chapter 56 builds accented letters from anchors, and it will put this one right along with the rest.

## Step 5: Ask the whole font

Two questions remain, and both are loops you can write. Which anchor names does Plum use, and how often? And do the 85 built glyphs from Tuesday agree with the anchors, or did the designer shift some accents by hand afterwards?

The first is a tally, as in chapter 22. The second needs one more idea. An accent can have more than one loop, and a letter more than one peg that fits. The acute has `_acute` and `_acuteHigh`, and the `u` has pegs for both. So for one pair of glyphs there can be several shifts that the anchors allow. I collect them all and then ask whether the shift in the glyph is one of them:

```python
def possible_shifts(base_points, mark_points):
    shifts = []
    for family, (bx, by) in base_points.items():
        if "_" + family in mark_points:
            mx, my = mark_points["_" + family]
            shifts.append((bx - mx, by - my))
    return shifts
```

Look at the `for` line. `items()` gives a key and a value on each turn, as in chapter 22, and here the value is a pair. The parentheses around `bx, by` take that pair apart on the spot. Without them you'd write `for family, point in ...` and then `bx, by = point` on the next line. Both are fine.

Then the test is one word you've known since chapter 9:

```python
print((50.0, 0.0) in [(50.0, 0.0), (50.0, 100.0)])
```

```text
True
```

`in` compares a pair with each pair in the list, and two pairs are equal when both their numbers are.

## The whole script

Here is `list_anchors.py`:

```python
# Counts the anchor names in the font, then checks every glyph built from a
# base and one accent: does the accent's shift match what the anchors say?
# Reads only.
import fly.ap.anchors.writer as anchors
import fly.ap.components.writer as parts
from fly import fl
from fly.pens import layer_of

MASTER = "Regular"
TOP = 5


def possible_shifts(base_points, mark_points):
    shifts = []
    for family, (bx, by) in base_points.items():
        if "_" + family in mark_points:
            mx, my = mark_points["_" + family]
            shifts.append((bx - mx, by - my))
    return shifts


def main():
    font = fl.CurrentFont()
    layers = {}
    points = {}
    for glyph in font.glyphs:
        layers[glyph.name] = layer_of(fl.flGlyph(glyph, font), MASTER)
        points[glyph.name] = anchors.anchor_points(layers[glyph.name])

    tally = {}
    carriers = 0
    for name in points:
        if points[name]:
            carriers += 1
        for anchor in points[name]:
            tally[anchor] = tally.get(anchor, 0) + 1

    def how_often(anchor):
        return tally[anchor]

    for anchor in sorted(tally, key=how_often, reverse=True)[:TOP]:
        print(f"{anchor:<10}{tally[anchor]:>4}")
    print(f"{carriers} glyphs carry anchors, under {len(tally)} names.")
    print()

    agree = 0
    differ = 0
    no_pair = []
    for name in layers:
        found = parts.components(layers[name])
        if len(found) != 2:
            continue
        base = parts.base_of(found[0])
        mark = parts.base_of(found[1])
        shifts = possible_shifts(points[base], points[mark])
        dx, dy = parts.offset(found[1])
        if not shifts:
            no_pair.append(name)
        elif (dx, dy) in shifts:
            agree += 1
        else:
            differ += 1
            wanted = ", ".join([f"{round(x)} {round(y)}" for x, y in shifts])
            print(f"{name:<12}glyph says {round(dx)} {round(dy)}, anchors say {wanted}")
    print(f"Agree with their anchors: {agree}. Differ: {differ}.")
    print(f"{len(no_pair)} have no matching pair: {' '.join(no_pair)}")


main()
```

```text
top         99
acute       97
bottom      85
grave       74
ogonek      56
116 glyphs carry anchors, under 18 names.

nacute      glyph says 54 0, anchors say 52 0
Agree with their anchors: 67. Differ: 1.
14 have no matching pair: IJ iacute icircumflex idieresis igrave ij colon quotedbl semicolon guillemotleft guillemotright quotedblbase quotedblleft quotedblright
```

The order of the 14 names follows your font and may differ from mine.

The script reads every layer and every set of anchors once, at the top, and keeps them in two dictionaries. After that, asking for the anchors of a base or an accent is a lookup by name.

Now read the result, because it says three things about Plum.

Sixty-seven glyphs agree, and none of the designer's glyphs differs. Every accent in the font sits where the anchors put it. Whoever built Plum didn't place accents by hand. They placed anchors, and a tool placed the accents. The one glyph that differs is the one you and I made yesterday without asking.

Fourteen have no matching pair. Ten of those aren't accented letters at all: the colon, the quotation marks and the like are one glyph borrowed two or three times, the `IJ` and `ij` are two letters side by side, and nobody hangs a period on a period. The other four are worth a frown. `iacute`, `icircumflex`, `idieresis` and `igrave` are built on `dotlessi`, the `i` without its dot, and `dotlessi` has no anchors. Those four were placed by hand. If Mira ever changes the `dotlessi`, their accents will stay where they were.

And look at the fifth line of the tally. Fifty-six glyphs have an anchor called `ogonek`. The ogonek is the little hook under the Polish `ą` and `ę`. Plum has no ogonek glyph. Somebody planned for Polish, set a peg for the hook on 56 letters, and never drew the hook. Mira writes "ogonek" under "caron" on her drawing list, and feels a little less alone with the email from Warsaw.

## What you learned

An anchor is a named point in a layer, and `anchors.anchor_points(layer)` gives them as a dictionary from name to position. A plain name is a place on a letter, and the same name with an underscore is the matching place on an accent. The shift for a component is the first minus the second, and it carries the height as well as the sideways position. A dictionary can hold pairs, a `for` line can take a pair apart in place, and a font's own anchors are a better source than a sum, when the font has them.

## Try it yourself

1. Yesterday's first exercise built `Nacute` with `O` as the model. Ask the anchors for `N` and the acute in all three masters. In which master does the model disagree most, and by how many units? Is it the same master as for the lowercase?
2. The Czech `ů` is a `u` with a ring, and Plum has both. Call `possible_shifts` for `u` and `ring` in the Regular, and you get one answer, so the letter can be built. Now call it for `u` and `acute`. You get two. Print the anchors of `u`, find the peg that makes the second one, and say what you think the designer wanted it for.
3. Change the script so that it also counts built glyphs whose base has anchors while the glyph itself has none. A new glyph such as `nacute` starts with no anchors of its own. Why might an accented letter want pegs of its own? Think of a letter that carries two accents, one on top of the other.

## Next

Four letters stand on a `dotlessi` that has no anchors, and every new accent Mira draws will need a loop. Chapter 55 writes anchors into glyphs: where to put them, how to work the place out, and how to do it as one step you can undo.
