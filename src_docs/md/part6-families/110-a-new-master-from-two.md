---
this_file: src_docs/md/part6-families/110-a-new-master-from-two.md
---

# 110. A new master from two

Friday of week twenty-one. The art director wants to see the chapter numbers in the weight between Regular and Bold before she decides anything. She doesn't want a font. She wants eleven glyphs, the ten figures and the hyphen, drawn the way a Medium would draw them, so that "12" and "3-4" can go on a title page by Monday.

On Monday you did that sum yourself for one rectangle. Today FontLab does it for whole glyphs, curves and all, and puts the result where Mira can see it and change it: in a new layer of each glyph.

One limit before you start. The chapter's title says a master, and what you'll make is smaller. A master belongs to the whole font. I found the calls that add one, and I found nobody who uses them, so I won't hand them to you. What Fly's own tools do, and what this chapter does, is add an in-between layer to the glyphs you name. For eleven glyphs on a title page that's the right size anyway.

## What you need

- `Plum-practice` open in FontLab 9, saved, with Fly installed.
- `halfmoon.py` with `tell`.
- Chapter 106's sum and chapter 55's rule about borrowed glyphs.

I couldn't run the code in FontLab 9. The two calls that make and attach the layer are the ones Fly's Layer Manager uses, and I've followed its order. The output is from a stand-in.

## Step 1: Ask FontLab for the glyph in between

A glyph can be asked what it would look like at a place on the axis. The place is a location, built from the axis's short name and a number. Chapter 107 printed the short name: `wt`.

```python
import fly.ap.core.scripting as scripting
from fly import fl

package = scripting.current_package()
glyph = package.findName("hyphen")
layer = glyph.interpolateInstance(fl.flLocation({"wt": 500}), False)
print(layer.advanceWidth)
```

```text
348.0
```

The `False` says "don't round the coordinates". The layer that comes back has an outline and a width, like any other.

## Step 2: The mistake

So the hyphen has a Medium now. Count its layers:

```python
print([layer.name for layer in glyph.layers])
```

```text
['Bold', 'Regular', 'Light']
```

Three, as before. Run the two lines ten times and there are still three.

`interpolateInstance` makes a layer and gives it to you. It doesn't put it in the glyph. The layer is loose: your variable holds it, and nothing else in FontLab knows it exists. When the script ends, the variable goes and the layer goes with it.

You've met something like it in chapter 46. The `RecordingPen` there took every order and changed nothing in FontLab, because nothing connected it to a glyph. Making a thing and attaching it are two steps, and the second is the one that changes the font.

## Step 3: Give it a name FontLab can read

Before the layer is attached it needs a name, and the name matters more than usual.

Call it `Medium` and FontLab has a fourth layer that it treats as a loose sketch. Nothing says where on the axis it belongs. Call it `:wt=500` and FontLab reads the name as a place: this layer is the glyph at weight 500. That's an intermediate layer. When FontLab makes a weight between 400 and 700 it will pass through this drawing on the way, so if Mira thickens the hyphen here, every weight near 500 follows.

You could type the name yourself. Fly builds it, and checks the number while it does:

```python
import fly.ap.studios.layer_manager.intermediate as intermediate

values, name = intermediate.location_values(package, {"wt": 500})
print(values, name)
```

```text
{'wt': 500.0} :wt=500
```

Two answers come back, and you unpack them as in chapter 76. `values` is the location, cleaned up. `name` is the layer name that says the same thing.

## Step 4: Which glyphs can take one?

Not every glyph can. Fly's tool asks each glyph a list of questions before it writes, and gives the first reason that stops it, or an empty string:

```python
import fly.ap.core.history.glyphs as history

facts = history.scan_auto_facts(package)
for glyph_name in ["hyphen", "e", "eacute"]:
    glyph = package.findName(glyph_name)
    print(glyph_name, repr(intermediate.keep_reason(package, glyph, name, values, facts)))
```

```text
hyphen ''
e 'base of auto eacute, ecircumflex…'
eacute 'has auto layers'
```

The second and third lines are chapter 55's rule again. `e` is borrowed by glyphs that FontLab builds, and `eacute` is one of those glyphs. Chapter 55 said the book would pass `allow_bases=True` for a borrowed glyph. Not today. Fly's own tool doesn't offer that choice for new layers, and I won't go where it didn't. So the letters most words need can't be done by this script, which is one more reason the art director is getting figures.

The other reasons you may meet: `layer already exists`, `master outlines are incompatible` (chapter 102's subject), and `location already exists on` followed by a layer's name.

## The whole script

```python
#FLM: Blend Master
# Adds an in-between layer to a list of glyphs, at one place on the
# weight axis. FontLab does the sum. Dry run by default.
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.studios.layer_manager.intermediate as intermediate
import halfmoon
from fly import fl

GLYPHS = ["zero", "one", "two", "three", "four", "five", "six", "seven",
          "eight", "nine", "hyphen"]
WEIGHT = 500
DRY_RUN = True


def has_layer(glyph, name):
    layer = glyph.findLayer(name)
    return layer is not None and not layer.isNull


def interpolated(glyph, values, name):
    layer = glyph.interpolateInstance(fl.flLocation(values), False)
    if layer is None or layer.isNull or layer.autoLayer:
        return None
    layer.name = name
    return layer


def main():
    if fl.CurrentFont() is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    axis = package.axes[0]
    values, name = intermediate.location_values(package, {axis.shortName: WEIGHT})
    facts = history.scan_auto_facts(package)
    ready = []
    for glyph_name in GLYPHS:
        glyph = package.findName(glyph_name)
        if glyph is None:
            print(f"{glyph_name}: no such glyph")
            continue
        why = intermediate.keep_reason(package, glyph, name, values, facts)
        if why:
            print(f"{glyph_name}: left alone, {why}")
            continue
        ready.append(glyph)
    print(f"Ready for a layer named {name}: {len(ready)} of {len(GLYPHS)}.")
    if DRY_RUN:
        print("Dry run. Nothing was changed.")
        return
    prepared = []
    for glyph in ready:
        layer = interpolated(glyph, values, name)
        if layer is None:
            print(f"{glyph.name}: FontLab could not interpolate it")
            continue
        prepared.append((glyph, layer))
    if not prepared:
        return

    def change():
        for glyph, layer in prepared:
            glyph.addLayer(layer)

    glyphs = [glyph for glyph, layer in prepared]
    history.commit(f"Add {name} layers", [], glyphs, change,
                   operation="geometry", facts=facts)
    added = [glyph for glyph in glyphs if has_layer(glyph, name)]
    print(f"Layers added: {len(added)}.")


main()
```

Save it as `blend_master.py` and run it:

```text
Ready for a layer named :wt=500: 11 of 11.
Dry run. Nothing was changed.
```

Save the font, set `DRY_RUN = False` and run again:

```text
Ready for a layer named :wt=500: 11 of 11.
Layers added: 11.
```

**Edit > Undo** should offer `Add :wt=500 layers`, one step for all eleven.

Notes on the listing.

The script works in two passes. The first makes all the loose layers and attaches nothing. The second, inside `change`, attaches them. If FontLab can't interpolate the seventh glyph, you learn it before the font has been touched, and the other ten still go in as one step.

`interpolated` returns `None` in three cases: FontLab gave nothing, gave an empty layer, or gave an automatic one. A function that returns either a thing or `None` is the pattern of chapter 16, and the caller tests for it.

The commit's second slot, the list of layers, is empty. That slot is for layers that already exist and are about to change, and here none of them does. The new ones are named by the glyphs that receive them.

`has_layer` is chapter 101's function, with the layer's name in place of a master's. The last line counts what's in the font after the write. It doesn't count what the script meant to add.

## After the run: did FontLab do Monday's sum?

Chapter 106 said the hyphen at 500 runs from 240 to 300. Ask the new layer:

```python
import fly.ap.masters.interpolation.model as interpolation

glyph = package.findName("hyphen")
print(interpolation.outline(glyph.findLayer(":wt=500")))
```

If FontLab's sum is the one you did by hand, you'll see this:

```text
[[(56.0, 240.0, True), (292.0, 240.0, True), (292.0, 300.0, True), (56.0, 300.0, True)]]
```

That's a prediction. I haven't seen the line, and if yours differs I'd like to know by how much. A difference of a fraction would be the rounding you switched off. A difference of whole units would mean FontLab's road from Regular to Bold isn't the straight one of chapter 106, and that would be worth a letter to the people who make it.

## Break it on purpose

Leave `DRY_RUN = False` and run the script a second time:

```text
zero: left alone, layer already exists
one: left alone, layer already exists
two: left alone, layer already exists
```

and so on down to the hyphen, ending with

```text
Ready for a layer named :wt=500: 0 of 11.
```

Nothing was added twice, because the question was asked again and the font's answer had changed.

Now ask for a weight nobody drew toward. Set `WEIGHT = 800`:

```text
ValueError: weight: choose a finite coordinate inside the design range.
```

The script stops at `location_values`, before any glyph is looked at. The design range is the axis's own, 300 to 700 in Plum. Chapter 106 turned a hyphen inside out by going outside it, and Fly won't build a layer there.

Set `WEIGHT` back to 500 and `DRY_RUN` back to `True`.

## What Mira does with it

She opens `two` in the **Glyph window**, picks the layer `:wt=500` in the **Layers & Masters** panel, and looks. The interpolation is a fair first drawing. The place where the curve of the 2 meets its foot is heavier than she'd like, and she pulls two nodes. That's the use of an in-between layer: the arithmetic does most of it, and a person corrects where the arithmetic is dull.

She should keep one thing in mind, and so should you. The eleven glyphs now have a say at 500 that the font's other glyphs don't. A whole font exported at Medium would mix corrected figures with letters that are pure arithmetic. For a title page that's fine. For a released Medium, it's the start of a job that somebody has to finish or undo.

## What you learned

`interpolateInstance` makes a loose layer at a location, and `addLayer` inside a commit is what puts it in the glyph. A layer named in the form `:wt=500` is an intermediate layer, a drawing FontLab passes through between masters, while any other name is a sketch. Fly's `keep_reason` gives the first reason a glyph can't take such a layer, and borrowed and automatic glyphs are among those it keeps. Asking the questions again on every run is what makes a second run harmless.

## Try it yourself

1. Add `"e"`, `"eacute"` and `"Zero"` to `GLYPHS` and do a dry run. You should get three lines of explanation and `11 of 14`. Which of the three is a typing mistake, and how does the script tell it from the other two?
2. Make the script count the reasons. Collect each `why` in a dictionary from reason to number, as in chapter 22, and print it at the end.
3. Print, for each ready glyph, the width FontLab's loose layer has and the width chapter 106's `lerp` gives from the Regular and Bold widths. For the figures both should be 490. Try `WEIGHT = 350` and see whether they still agree.

## Next

The figures can go on the title page once there's a font file to set them with. Chapter 111 is about getting one font out of FontLab and into a folder, and about how much of that a script can do.
