---
this_file: src_docs/md/part6-families/105-copy-between-masters.md
---

# 105. Copy between masters

Friday of week twenty. A publisher of Latin dictionaries has asked whether Plum can set ǣ, the `ae` with a macron that marks a long vowel. It can't yet. The `ae` and the `AE` have an `acute` anchor and no `top`, so there's nowhere to hang the macron.

Mira placed a `top` on both glyphs before lunch. She did it in the Regular, because that's the master she had on screen, and went to eat.

So two glyphs now have an anchor in one master out of three. Chapter 102's check would call that a mismatch, and it would be right. Today's script finds anchors that exist in one master and are missing in another, and puts them there. The question is where "there" is, since the three drawings aren't the same width.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `tell`.
- Chapter 55 fresh in your mind: an edit is `("set", name, (x, y))`, and a row of work is a glyph, a layer and a list of edits.

I couldn't run the code in FontLab 9. I ran the arithmetic on the anchors and widths in Plum's source file, and the numbers below come from there.

## Step 1: Do what Mira did

Put the two anchors in. This is chapter 55's route, on two glyphs and one master. First the tools and the two places, which Mira read off the Glyph window:

```python
import fly.ap.anchors.writer as anchors
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
from fly.pens import layer_of

PLACES = {"ae": (377, 478), "AE": (426, 688)}
```

Then the work, one entry for each glyph, checked and written in one go:

```python
package = scripting.current_package()
facts = history.scan_auto_facts(package)
work = []
for name in PLACES:
    glyph = package.findName(name)
    layer = layer_of(glyph, "Regular")
    work.append((glyph, layer, [("set", "top", PLACES[name])]))
anchors.require_safe(work, facts)
done = anchors.apply_work(work, "Add top to ae and AE", facts)
print(done["anchors"], "anchors on", done["layers"], "layers.")
```

```text
2 anchors on 2 layers.
```

The x values are each glyph's `acute` plus 20, which is how Plum's other letters keep their `top` and `acute` apart. The heights are the x-height and the cap height.

`require_safe` lets these two through. Nothing in Plum is built from `ae` or `AE`, so chapter 55's refusal doesn't come up. I picked the story for that reason, and it comes back in Step 5.

## Step 2: The mistake

The plain idea: read the anchor in the Regular, write the same numbers in the Light.

Before trying it on Mira's anchors, try it on an anchor whose right answer you can look up. The `H` has a `top` in all three masters. Ask what the plain idea would have written:

```python
glyph = package.findName("H")
regular = layer_of(glyph, "Regular")
light = layer_of(glyph, "Light")
print(regular.advanceWidth, anchors.anchor_points(regular)["top"])
print(light.advanceWidth, anchors.anchor_points(light)["top"])
```

```text
672.0 (336.0, 688.0)
612.0 (306.0, 688.0)
```

The Regular keeps the anchor at 336. The Light keeps it at 306. Copy the 336 across and the macron sits 30 units to the right of where Plum's designer put it, on every `H` with an accent.

Nothing would have complained. The script would have printed a tidy count, the check from chapter 102 would have passed, and the fault would have turned up in a proof weeks later as accents that lean right in the Light.

Look at the four numbers again. 336 is half of 672. 306 is half of 612. The anchor is in the middle of the glyph in both masters. An x position has no meaning without the width it was measured in.

## Step 3: Scale it

Keep the anchor at the same share of the width. If it sits 336 units into 672, that's a share of 336/672. In a glyph 612 wide, the same share is:

```python
def scaled(x, source_width, target_width):
    return round(x * target_width / source_width)

print(scaled(336, 672, 612))
```

```text
306
```

Multiply first, divide last. `x / source_width * target_width` is the same sum on paper, and on a computer the early division leaves a long tail that the multiplication then stretches. You saw such a tail in chapter 68.

The y stays as it is. Plum's three masters share their x-height and cap height, so an anchor at 688 in one is at 688 in all.

One formula checked against one anchor is a hunch. Plum has plenty of anchors that exist in all masters, so the rule can be tested on the lot. I took the seventeen glyphs with anchors that are drawn by hand and aren't borrowed by anything, 43 anchors in all, and predicted each Light position from the Regular one:

| Rule | Right to the unit | Within 3 units |
| --- | --- | --- |
| Same x | 3 | 3 |
| Scaled x | 14 | 36 |

Scaling is much better and it isn't perfect. The seven it misses are of two kinds. `cedilla` sits at x 100 in every master, whatever the width: it's a parking place and no one moved it. `topRight` hangs at the right edge of a stem, and stems get thinner in the Light by more than the glyph gets narrower.

So the script's output is a first guess. For an anchor in the middle of a letter the numbers will be right or a unit off. For one that hangs on an edge, look.

## Step 4: Find what's missing

For one glyph and one pair of layers, the missing anchors are the names in the first that aren't in the second:

```python
def missing_edits(source, target):
    have = anchors.anchor_points(target)
    edits = []
    if source.advanceWidth == 0:
        return edits
    for name, (x, y) in anchors.anchor_points(source).items():
        if name not in have:
            new_x = scaled(x, source.advanceWidth, target.advanceWidth)
            edits.append(("set", name, (new_x, round(y))))
    return edits
```

`anchor_points` gives a dictionary from anchor name to a pair, and `for name, (x, y) in ... .items()` unpacks the pair on the way, as chapter 86 did with numbered pairs. The test on the width is there because `scaled` divides by it. A glyph of no width has no shares.

The function returns edits in chapter 55's form and touches nothing. It only ever adds. An anchor that's already in the target stays where its designer put it, even if the rule would put it elsewhere.

## Step 5: The glyphs it must leave alone

Chapter 55 met two kinds of glyph that Fly's anchor writer won't touch. A glyph that FontLab builds itself can't be edited at all. A glyph that such glyphs borrow can be edited only through your own commit with `allow_bases=True`.

A script that walks the whole font will meet both. If it hands one to `require_safe`, the whole batch is refused and nothing is written, the good rows included. So ask first, glyph by glyph:

```python
print(repr(history.refusal(facts, "ae", "geometry")))
print(repr(history.refusal(facts, "o", "geometry")))
print(repr(history.refusal(facts, "aacute", "geometry")))
```

```text
''
'base of auto oacute, ocircumflex…'
'has auto layers'
```

`refusal` answers with the reason as a string, and with an empty string when there's none. An empty string counts as false in an `if`, so `if history.refusal(...)` reads as "if there's a reason not to". The second line is my reading of Fly's code, which names the first two borrowers and then stops. Which two it names in your font I can't tell you.

The script sets such glyphs aside and names them at the end. For a borrowed glyph you then have a choice: place the anchor by hand in each master, or use chapter 55's commit. I left that out of today's script on purpose. Adding an anchor to `o` makes FontLab rebuild at least five glyphs, `oacute` to `otilde`, and that's a decision for a person with the glyph on screen.

## The whole script

```python
#FLM: Sync Masters
# Copies anchors that exist in the trusted master but are missing in
# another master. The x is scaled by the widths. Dry run by default.
import fly.ap.anchors.writer as anchors
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.masters.inspect.model as masters_model
import halfmoon
from fly import fl
from fly.pens import layer_of

TRUSTED = "Regular"
DRY_RUN = True


def scaled(x, source_width, target_width):
    return round(x * target_width / source_width)


def missing_edits(source, target):
    have = anchors.anchor_points(target)
    edits = []
    if source.advanceWidth == 0:
        return edits
    for name, (x, y) in anchors.anchor_points(source).items():
        if name not in have:
            new_x = scaled(x, source.advanceWidth, target.advanceWidth)
            edits.append(("set", name, (new_x, round(y))))
    return edits


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    others = [m for m in masters_model.master_order(package) if m != TRUSTED]
    facts = history.scan_auto_facts(package)
    work = []
    left_alone = []
    count = 0
    for font_glyph in font.glyphs:
        glyph = package.findName(font_glyph.name)
        source = layer_of(glyph, TRUSTED)
        for master in others:
            target = layer_of(glyph, master)
            edits = missing_edits(source, target)
            if not edits:
                continue
            if history.refusal(facts, glyph.name, "geometry"):
                if glyph.name not in left_alone:
                    left_alone.append(glyph.name)
                continue
            for kind, name, (x, y) in edits:
                print(f"{glyph.name} {master}: {name} at {x}, {y}")
            work.append((glyph, target, edits))
            count += len(edits)
    print(f"{count} anchors missing in {len(work)} layers.")
    if left_alone:
        print("Left alone, FontLab builds glyphs with them:")
        print(" ".join(left_alone))
    if DRY_RUN:
        print("Dry run. Nothing was changed.")
        return
    if not work:
        return
    anchors.require_safe(work, facts)
    done = anchors.apply_work(work, f"Copy anchors from {TRUSTED}", facts)
    print(f"{done['anchors']} anchors on {done['layers']} layers.")


main()
```

Save it as `sync_masters.py` and run it:

```text
AE Light: top at 414, 688
AE Bold: top at 426, 688
ae Light: top at 372, 478
ae Bold: top at 377, 478
4 anchors missing in 4 layers.
Dry run. Nothing was changed.
```

In the Bold the numbers equal the Regular's, because those two glyphs are as wide in the Bold as in the Regular. In the Light, `AE` is 829 wide against 852, and 426 × 829 / 852 is 414.5. `round` gives 414: a half goes to the even neighbor, as chapter 53 found.

Read the list, then set `DRY_RUN = False` and run. The last line becomes `4 anchors on 4 layers.`, and **Edit > Undo** should take all four back in one step, named `Copy anchors from Regular`. Set `DRY_RUN` back to `True` and run again:

```text
0 anchors missing in 0 layers.
Dry run. Nothing was changed.
```

Notes on the listing.

`TRUSTED` is a name you type, where chapter 103 took the master on screen. Mira's habit decided it: she places anchors in the Regular. A constant at the top says so to whoever reads the script next.

All the work goes to `apply_work` in one list, so the whole run is one Undo step. Chapter 103 made one step for each contour. Either is defensible. Here the edits are small and alike, and one step is easier to take back.

`require_safe` is still called, though the loop has already set the refused glyphs aside. It also checks things `refusal` doesn't, such as two anchors with one name. And if my loop has a hole, I'd like to hear about it before anything is written.

## Break it on purpose

Go to the Light of `o`, select the `top` anchor and delete it. Run the dry run:

```text
0 anchors missing in 0 layers.
Left alone, FontLab builds glyphs with them:
o
Dry run. Nothing was changed.
```

The script saw the gap and declined to fill it. Now undo your deletion with **Edit > Undo**, and run once more to see the last two lines go.

If you'd like to see what the script was avoiding, take the `if history.refusal` block out, delete the anchor again and run with `DRY_RUN = False`. By Fly's code you get a `ValueError` that begins `FontLab cannot undo edits to these glyphs` and nothing is written. Put the block back, and the anchor.

## What about guides and metrics?

Oskar's notes list three things that drift between masters: anchors, guides and the font's own measurements.

Plum's glyphs carry no guides, so there's nothing to copy, and I found no way to write the font's guides from Python with Undo. The font's measurements, ascender and the rest, have their own route, the one chapter 96 used, and they don't scale by a glyph's width. The script stays with anchors.

## What you learned

A position copied between masters has to be scaled by the two widths, and you multiply before you divide. A rule can be tested on the data you already trust before it writes anything new. A function that returns a reason as a string, empty for none, can be used as a yes or no. A script that walks a whole font should set aside what it may not touch and say so, since one refused glyph stops the batch.

## Try it yourself

1. Run the dry run with `TRUSTED = "Light"`. With Mira's anchors copied, it should find nothing. Delete the `top` from the Regular of `AE`, run again, and compare the number it offers with 426, where the anchor was. It says 425. Where did the unit go?
2. In the Bold, the `acute` of `ae` sits at 376, which is 19 to the right of the Regular's 357, though the widths are equal. The scaling rule can't know that. Write `beside(layer, source, name, model)` that places a missing anchor as far from the target's `model` anchor as it is in the source: for `top` with `acute` as model, 20 to the right. It should give 372, 396 and 415 for the Light `ae`, the Bold `ae` and the Light `AE`.
3. Make the script report anchors that exist in both masters and sit more than 10 units from where the rule would put them. Change nothing. On Plum as shipped, which anchor names fill the list?

## Next

The art director's weight between Regular and Bold is still waiting. Chapter 106 works out by hand what "halfway between" two drawings means, one number at a time.
