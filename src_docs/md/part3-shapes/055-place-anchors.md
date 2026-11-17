---
this_file: src_docs/md/part3-shapes/055-place-anchors.md
---

# 55. Place the anchors

Friday. Yesterday's list ended with four names that bothered Mira all evening: `iacute`, `icircumflex`, `idieresis` and `igrave`. They stand on `dotlessi`, and `dotlessi` has no anchors. Somebody placed those four accents by hand, years ago.

It matters this week because of Prague. The Czech `í` is there already, but next week's script will build accented letters from anchors, and a letter without pegs will be skipped. Mira wants the `dotlessi` to carry pegs like its neighbors before she goes home.

She could click three anchors into three masters. That's nine clicks, each one placed by eye, and she'd rather the nine places came from a rule she can read. So today a script writes into the font again: nine anchors, in one step that **Edit > Undo** can take back.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `rich` and `box`.
- `list_anchors.py` from chapter 54, for the check at the end.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. What the writing tool hands back is read from its code.

## Step 1: Work out where `top` goes

Look at a neighbor first. The `n` has its `top` at 262 across and 478 up. The outline of the Regular `n` runs from 70 to 457, so its middle is 263.5. The peg sits near the middle of the letter, on the x-height. That's the rule to copy.

For the sideways position, `halfmoon.box` gives you the edges:

```python
import halfmoon
from fly import fl

font = fl.CurrentFont()
for master in ["Light", "Regular", "Bold"]:
    left, bottom, right, top = halfmoon.box(font, font["dotlessi"], master)
    print(master, (left + right) / 2, top)
```

```text
Light 97.0 474.0
Regular 111.0 478.0
Bold 126.0 482.0
```

The middles are what you'd expect from a stem that gets fatter. Now look at the last column. I printed the top of the box because it seemed the obvious height for the peg: the stem is flat on top, and that's where an accent should hover. But the three numbers differ. The Light stem stops four units short of 478, and the Bold one goes four units over.

Every other lowercase letter in Plum has its `top` at 478 in all three masters, whatever its outline does. The designer hung the accents from the x-height of the font, and didn't measure each letter. You met that number in chapter 43:

```python
from fly.tr.proxy.fl.objects.font import pFont

metrics = pFont().fontMetrics()
for master in ["Light", "Regular", "Bold"]:
    print(master, metrics.getXHeight(master))
```

```text
Light 478
Regular 478
Bold 478
```

As in chapter 43, each of those questions switches the font to the master it names, so the font is on the Bold when the loop ends. Switch back to the Regular in the Font window before you go on. The same holds for the whole script below.

So the place has two sources. Across comes from the letter's own outline, because that's where this letter is. Up comes from the font, because that's a line all the letters share. When you compute a position, ask of each number which of the two it is.

```python
def top_place(font, name, master):
    left, bottom, right, top = halfmoon.box(font, font[name], master)
    return round((left + right) / 2), metrics.getXHeight(master)


print(top_place(font, "dotlessi", "Regular"))
```

```text
(111, 478)
```

## Step 2: Ask the glyphs that are already there

In chapter 53 you tested a sum on a solved case. There are solved cases here too. The four accented `i` glyphs were placed by hand, and each placement says where its designer thought the peg was.

Yesterday the shift was the peg minus the loop. Turn that around: the peg is the loop plus the shift.

```python
import fly.ap.anchors.writer as anchors
import fly.ap.components.writer as parts
from fly.pens import layer_of


def layer_for(font, name, master):
    return layer_of(halfmoon.rich(font, font[name]).fl, master)


def peg_in(font, composite, family, master):
    accent = parts.components(layer_for(font, composite, master))[1]
    dx, dy = parts.offset(accent)
    loops = anchors.anchor_points(layer_for(font, parts.base_of(accent), master))
    lx, ly = loops["_" + family]
    return round(lx + dx), round(ly + dy)


for master in ["Light", "Regular", "Bold"]:
    mine = top_place(font, "dotlessi", master)
    print(master, mine, peg_in(font, "icircumflex", "top", master))
```

```text
Light (97, 478) (96, 478)
Regular (111, 478) (110, 478)
Bold (126, 478) (110, 478)
```

`peg_in` opens a built glyph, takes its second component, which is the accent, reads that accent's loop and adds the shift. I wrote `layer_for` because the line that fetches a layer by glyph name was about to appear four times.

In the Light and the Regular, the sum and the designer agree to within a unit. In the Bold they're 16 units apart. The Bold stem runs from 60 to 192, so its middle is at 126, and the circumflex sits over 110.

Mira opens the Bold `icircumflex` and zooms in. The hat sits left of the stem. Nobody had noticed, because nobody sets much Bold `î`. My guess is that the accent was placed when the Bold stem was thinner, and then the stem grew to the right. A hand-placed accent has no way to follow. That's the argument for anchors, and Plum made it against itself.

So for `top`, the sum wins. For `acute` and `grave`, Mira decides differently. In most of Plum those two pegs sit 20 units left and right of `top`. On the narrow `i` the designer spread them much wider, on purpose, so that the leaning accents clear the stem. She wants to keep that. `peg_in` can read both places out of `iacute` and `igrave`, and the script will write them down as they are.

## Step 3: Describe the edits

As with new glyphs on Wednesday, you describe the work first and hand it to a tool. An edit to an anchor is a tuple of three things: what to do, the anchor's name, and a value.

```python
edit = ("set", "top", (111, 478))
```

`"set"` means: put the anchor of this name at this place, and make one if there isn't one. The value is a pair, so this is a tuple with a tuple in it. Count the items: there are three, and the third has two.

Edits belong to a layer, and a layer belongs to a glyph. So one row of work is another tuple of three: the glyph, the layer, and a list of edits for that layer.

```python
rich = halfmoon.rich(font, font["dotlessi"])
layer = layer_of(rich.fl, "Regular")
work = [(rich.fl, layer, [edit])]
```

Now hand it over. The tool has two doors. `require_safe` looks at the work and refuses if anything in it can't be undone properly. `apply_work` does it. Before I show you both working, here's what happens when the edit has the wrong shape. Suppose you'd written the place as two loose numbers:

```python
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting

facts = history.scan_auto_facts(scripting.current_package())
bad = ("set", "top", 111, 478)
anchors.require_safe([(rich.fl, layer, [bad])], facts)
```

```text
Traceback (most recent call last):
  ...
ValueError: too many values to unpack (expected 3)
```

You've written `dx, dy = ...` often enough. The tool does the same thing with your edit: it takes it apart into three names. Your tuple had four items, and Python won't guess which two belong together. The message doesn't mention anchors, because the tool never got as far as thinking about anchors. When a tool wants tuples of a certain shape, count the commas outside the inner parentheses.

Nothing was written. `require_safe` runs before anything touches the font, which is the reason to call it first.

## Step 4: Write them

With the edit in its right shape, go through the first door:

```python
anchors.require_safe(work, facts)
```

```text
ValueError: FontLab cannot undo edits to these glyphs: dotlessi: base of auto iacute, icircumflex…. Choose other glyphs.
```

The shape is right now, and the tool still says no. You met the words `base of auto` in chapter 30's table of reasons. Four glyphs borrow `dotlessi`: `iacute`, `icircumflex`, `idieresis` and `igrave`. FontLab builds those four itself, from a recipe, and builds them again whenever a glyph they borrow changes. The refusal names the first two and leaves the rest to the three dots.

Fly's code says why it's wary. When FontLab rebuilds those glyphs, Undo brings back `dotlessi`, and it may not bring back the anchors and locks of the rebuilt ones. So Fly's rule for a borrowed glyph is "not unless a person agreed". The anchor tool has no way to hear you agree, and on another glyph, one that nothing automatic borrows, its second door `apply_work(work, title, facts)` would do the whole job. `history.commit` from chapter 29 can hear you, through the keyword `allow_bases=True`. Mira agrees: pegs on `dotlessi` are the point of the afternoon. She saves the font first, and so should you.

The anchor tool lends the two halves of its second door. `prepare` turns the edits into steps, and `write` carries them out:

```python
steps = anchors.prepare(layer, [edit])

def change():
    anchors.write(layer, steps)

history.commit("Add top anchor", [layer], [rich.fl], change,
               operation="geometry", facts=facts, allow_bases=True)
print(len(steps))
```

```text
1
```

It's the pattern of chapter 29 and of `set_width`: a small function with the change in it, handed to `commit`. Open the Regular `dotlessi` and there should be a `top` mark over the stem. Then look at `iacute`. FontLab should have built it again, and it should look as it did. Then choose **Edit > Undo**: the mark should be gone, and `iacute` should still look as it did. All of that is untested, which is why it says "should". Try it before you go on.

From here on, the book passes `allow_bases=True` wherever a script changes a glyph that automatic glyphs borrow, and the rule is the same each time: save first, and look at one borrower afterward. A glyph that FontLab builds itself is another matter. No keyword opens that one, and a script that meets one reports it and leaves it alone.

Now run the lines from `steps = ...` again, without the Undo. On Wednesday a second run was refused, because a glyph can't be made twice. This time nothing complains and the count is the same:

```text
1
```

`"set"` on an anchor that exists moves it to the place you gave. It's already there, so it moves nowhere. A script that you can run twice with the same result as once is a comfortable thing to own. You can run it again after you've fixed a number, and it puts every anchor where the new number says.

## The whole script

Here is `add_top_anchors.py`:

```python
# Gives dotlessi the anchors its neighbors have. top is worked out from the
# stem and the x-height. acute and grave are read from the two glyphs where
# the designer placed those accents by hand.
# One Undo step.
import fly.ap.anchors.writer as anchors
import fly.ap.components.writer as parts
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import halfmoon
from fly import fl
from fly.pens import layer_of
from fly.tr.proxy.fl.objects.font import pFont

MASTERS = ["Light", "Regular", "Bold"]
TARGET = "dotlessi"
BY_HAND = {"acute": "iacute", "grave": "igrave"}


def layer_for(font, name, master):
    return layer_of(halfmoon.rich(font, font[name]).fl, master)


def top_place(font, name, master, height):
    left, bottom, right, top = halfmoon.box(font, font[name], master)
    return round((left + right) / 2), height


def peg_in(font, composite, family, master):
    accent = parts.components(layer_for(font, composite, master))[1]
    dx, dy = parts.offset(accent)
    loops = anchors.anchor_points(layer_for(font, parts.base_of(accent), master))
    lx, ly = loops["_" + family]
    return round(lx + dx), round(ly + dy)


def main():
    font = fl.CurrentFont()
    metrics = pFont().fontMetrics()
    rich = halfmoon.rich(font, font[TARGET])

    work = []
    for master in MASTERS:
        edits = [("set", "top", top_place(font, TARGET, master, metrics.getXHeight(master)))]
        for family, composite in BY_HAND.items():
            edits.append(("set", family, peg_in(font, composite, family, master)))
        work.append((rich.fl, layer_of(rich.fl, master), edits))
        for operation, name, place in edits:
            print(f"{master:<9}{name:<7}{place[0]:>4}{place[1]:>5}")

    # dotlessi is borrowed by automatic glyphs: see Step 4. Save first.
    planned = [(layer, anchors.prepare(layer, edits)) for glyph, layer, edits in work]

    def change():
        for layer, steps in planned:
            anchors.write(layer, steps)

    facts = history.scan_auto_facts(scripting.current_package())
    layers = [layer for layer, steps in planned]
    history.commit(f"Add anchors to {TARGET}", layers, [rich.fl], change,
                   operation="geometry", facts=facts, allow_bases=True)
    count = sum([len(steps) for layer, steps in planned])
    print(f"{count} anchors on {len(layers)} layers.")


main()
```

```text
Light    top      97  478
Light    acute    43  478
Light    grave   164  478
Regular  top     111  478
Regular  acute    51  478
Regular  grave   183  478
Bold     top     126  478
Bold     acute    40  478
Bold     grave   180  478
9 anchors on 3 layers.
```

The comprehension that fills `planned` prepares every layer's steps before `commit` is called, because the new anchors have to exist before FontLab starts recording. `top_place` gets the height handed in now, so that it doesn't reach for a `metrics` box outside itself. The loop that prints takes each edit apart into three names, as the tool does. And `BY_HAND` is a small dictionary that says which glyph to ask for which peg. If Mira changes her mind about the acute, that's the line she changes.

Look at the Bold rows. The `acute` peg is at 40 and the `grave` at 180, which puts them 70 either side of 110, the old middle. The `top` is at 126, the new one. The script wrote down what the designer did, and what the designer did was 16 units off. Mira adds a line to her list: "Bold í and ì: look at them." A script can keep a decision, and it can't tell you whether the decision was good.

## Check the work

Run `list_anchors.py` from yesterday. It reads the Regular:

```text
top        100
acute       98
bottom      85
grave       75
ogonek      56
117 glyphs carry anchors, under 18 names.

icircumflex glyph says -140 0, anchors say -139 0
idieresis   glyph says -139 0, anchors say -137 0
nacute      glyph says 54 0, anchors say 52 0
Agree with their anchors: 69. Differ: 3.
10 have no matching pair: IJ ij colon quotedbl semicolon guillemotleft guillemotright quotedblbase quotedblleft quotedblright
```

Three tallies went up by one. The four `i` glyphs have left the last line. `iacute` and `igrave` agree with their anchors, as they must, because the anchors were read from them. `icircumflex` and `idieresis` differ by a unit or two, because their peg came from the sum. Those two are automatic glyphs, so no script of ours will move them. Whether FontLab moves them itself when it next builds them, now that `dotlessi` has a `top` peg, is something to watch for: in the Bold they are 16 units off.

Ten glyphs remain without a pair, and all ten are punctuation or ligatures. That list is clean.

## What you learned

Anchors are written from a description: rows of glyph, layer and a list of edits, where an edit is `("set", name, (x, y))`, checked first by `anchors.require_safe`, which changes nothing. A glyph that automatic glyphs borrow is refused unless your own `history.commit` says `allow_bases=True` around `anchors.prepare` and `anchors.write`, after you've saved. A computed position can take one number from the glyph's own outline and the other from a line of the font. A solved case can be read backward to find what its maker assumed, and a tuple can hold a tuple, and a tool that takes it apart will complain about the count if you flatten it.

## Try it yourself

1. Change `MASTER` in `list_anchors.py` to `"Bold"` and run it. How far apart are the glyph and the anchors for `icircumflex`? Open the glyph and look at the gap the number describes.
2. Which one-letter glyphs have no `top` anchor? Write a loop over `font.glyphs` that prints every name of length 1 whose Regular anchors lack `top`. I get 21. Then look at the Czech and Polish lists from chapter 25. Does either language need an accent above any of the 21?
3. An edit can take an anchor away: `("remove", "top", None)`. Write a short script that removes `top` from the Regular `dotlessi`, run it, and then run `add_top_anchors.py` again. Did you end up where you were? Compare that with choosing **Edit > Undo** twice. Which would you rather explain to a colleague?

## Next

Plum's letters have pegs, its accents have loops, and you can make a glyph from a description. Chapter 56 puts the three together: a text file of recipes, one line for each letter, and a script that builds the lot.
