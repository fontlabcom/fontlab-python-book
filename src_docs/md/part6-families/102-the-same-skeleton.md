---
this_file: src_docs/md/part6-families/102-the-same-skeleton.md
---

# 102. The same skeleton

Tuesday of week twenty. Oskar tells a story from his second year at Halfmoon. A client asked for a Medium of a family that had a Regular and a Bold. The program worked it out in a second, and every glyph was there except the `g`, which wasn't a letter any more. One loop was folded through the other. It took him an afternoon to find out why. In the Bold, somebody had tidied the ear of the `g` and removed one node.

"Halfway between twenty nodes and nineteen," he says, "there's nothing."

A weight between two masters is made node by node: the first node of the Light with the first node of the Bold, the second with the second. That only works when both drawings have the same contours, each contour has the same number of nodes, and a node that's a handle in one is a handle in the other. Type designers call such drawings compatible. Yesterday's report said every glyph has three layers. Today's asks whether the three drawings in them share a skeleton.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py`.

I couldn't run the code in FontLab 9. I worked out the outputs in plain Python from Plum's source file, for the 205 glyphs Plum came with. I can't know what you drew in the glyphs you added in Part 3, so for those your run is the first one anybody has made.

## Step 1: One glyph's skeleton

```python
import fly.ap.core.scripting as scripting
import fly.ap.masters.inspect.model as masters_model

package = scripting.current_package()
masters = masters_model.master_order(package)
glyph = package.findName("a")
signatures, ok, problems = masters_model.check_glyph(glyph, masters)
print(ok, problems)
print(signatures["Regular"])
```

```text
True []
(('ooohhohhoohhohhoohhohhohhohho', 'ohhohhoohhoo'), ('acute', 'bottom', 'grave', 'ogonek', 'top'), ())
```

`check_glyph` returns three things, and you unpack them as in chapter 42. `ok` is `True` or `False`. `problems` is a list of words, empty when all is well. `signatures` is a dictionary with one entry per master.

Look at the entry for the Regular. It's a tuple of three tuples: the contours, the names of the anchors, and the names of the components. The `a` has two contours, the outside and the bowl, and each is written as a string. An `o` is a node on the outline and an `h` is a handle, the two kinds you counted in chapter 42. The outside has 29 letters and the bowl has 12.

Nothing in the signature says where a node is. Coordinates are what differs between a Light and a Bold, so they're left out, and what remains is the skeleton. Two masters are compatible when their signatures are equal, and Python compares tuples with `==`: the same things in the same order, all the way down.

## Step 2: The mistake

Before Mira found `check_glyph`, she'd have used what she had. Chapter 42's `node_counts` gives the number of nodes in a layer, and two layers with the same count look like a match. Try that idea on two made-up skeletons:

```python
light = ("oooo", "oohhohho")
bold = ("oooooo", "oohhoh")
print(sum([len(contour) for contour in light]))
print(sum([len(contour) for contour in bold]))
print(light == bold)
```

```text
12
12
False
```

Both have twelve nodes. In the Light they're shared out four and eight, in the Bold six and six. A check on totals passes these two, and nothing can be made between them. Somebody who removes a node in one place and adds one in another, on a tired afternoon, produces this pair.

A total throws away the structure, and the structure is what you wanted to compare. Compare the whole thing.

## Step 3: Say where

`check_glyph` says `contours` when the contours differ. That sends you to the right glyph and leaves you counting nodes on screen. A small function can find the first place where two skeletons part:

```python
def first_difference(a, b):
    if len(a) != len(b):
        return f"{len(a)} contours and {len(b)}"
    for number, (one, other) in enumerate(zip(a, b), 1):
        if one == other:
            continue
        if len(one) != len(other):
            return f"contour {number}: {len(one)} nodes and {len(other)}"
        for place, (x, y) in enumerate(zip(one, other), 1):
            if x != y:
                return f"contour {number}: node {place} is {x} and {y}"
    return ""
```

It asks three questions, from coarse to fine, and returns at the first one that finds something. Are there as many contours? If so, take them in pairs. Is this pair the same length? If so, take the letters in pairs.

`zip` pairs the contours of one master with those of the other, and `enumerate(..., 1)` from chapter 57 numbers the pairs from one. The loop line unpacks both at once: `number` gets the count and `(one, other)` gets the pair. The parentheses are needed, because each turn hands over a number and a pair, and the pair is opened inside.

Yesterday `zip` was the mistake, and today it's the tool. The difference is what you know about the two lists. Yesterday nothing said the two lists were in the same order. Here the order is the very thing being tested: the first contour of one master is supposed to be the first contour of the other.

```python
print(first_difference(light, bold))
```

```text
contour 1: 4 nodes and 6
```

## The whole script

```python
#FLM: Compatibility Check
# Compares the structure of every glyph across the masters.
# Changes nothing.
import halfmoon
from fly import fl
import fly.ap.core.scripting as scripting
import fly.ap.masters.inspect.model as masters_model


def first_difference(a, b):
    if len(a) != len(b):
        return f"{len(a)} contours and {len(b)}"
    for number, (one, other) in enumerate(zip(a, b), 1):
        if one == other:
            continue
        if len(one) != len(other):
            return f"contour {number}: {len(one)} nodes and {len(other)}"
        for place, (x, y) in enumerate(zip(one, other), 1):
            if x != y:
                return f"contour {number}: node {place} is {x} and {y}"
    return ""


def explain(signatures, masters):
    lines = []
    real = [m for m in masters if signatures.get(m) is not None]
    for master in real[1:]:
        text = first_difference(signatures[real[0]][0], signatures[master][0])
        if text:
            lines.append(f"{real[0]} and {master}: {text}")
    if len({signatures[m][1] for m in real}) > 1:
        for master in real:
            names = " ".join(signatures[master][1]) or "none"
            lines.append(f"{master} anchors: {names}")
    return lines


def main():
    package = scripting.current_package()
    if package is None:
        halfmoon.tell("Open a font first.")
        return
    masters = masters_model.master_order(package)
    checked = 0
    automatic = 0
    bad = 0
    for glyph in fl.CurrentFont().glyphs:
        fl_glyph = package.findName(glyph.name)
        signatures, ok, problems = masters_model.check_glyph(fl_glyph, masters)
        if signatures and all([signatures[m] is None for m in signatures]):
            automatic += 1
            continue
        checked += 1
        if ok:
            continue
        bad += 1
        print(f"{glyph.name}: {', '.join(problems)}")
        for line in explain(signatures, masters):
            print("   ", line)
    print(f"{checked} glyphs compared in {len(masters)} masters, {bad} don't match.")
    print(f"{automatic} glyphs are built automatically and were left out.")


main()
```

Save it as `compat_check.py`. On Plum as it came:

```text
132 glyphs compared in 3 masters, 0 don't match.
73 glyphs are built automatically and were left out.
```

Plum is clean. Your font has more glyphs, and I'd expect the ones you drew with a script to match as well, because one loop drew the same shape in every master. A glyph you drew by hand in one master only is the likely place for a line of complaint.

Notes on the listing.

Seventy-three of Plum's accented letters are assembled by FontLab from their parts, and for those `check_glyph` puts `None` where a signature would be. There's nothing to compare, since FontLab rebuilds them whenever the parts change. The script counts them and says so, in keeping with chapter 80: a glyph that wasn't checked isn't a glyph that passed. `all` from chapter 44 asks whether every entry is `None`. It also answers `True` for an empty list, so `signatures and` comes first: a glyph with no master layer at all has an empty dictionary, and it should be compared and reported, not counted as automatic.

`explain` compares each master with the first one that has a signature. It doesn't compare every pair, and it doesn't have to. If the Light matches the Regular and the Light matches the Bold, the Regular matches the Bold.

For anchors the script prints the names in each master, since a missing anchor is found faster by reading three short lines than by any arithmetic. The set in `len({...}) > 1` holds the different anchor tuples, and more than one of them means the masters disagree. That's the trick `check_glyph` uses itself.

Twelve of Plum's glyphs are put together from other glyphs by hand and not by FontLab. For those the first part of the signature is empty and the third part holds the names of the pieces, in order. An `aacute` that is `a` plus `acute` in two masters and `a` plus `grave` in the third would come back with the word `components`. The pieces themselves are checked under their own names, so a fault in the `a` is reported once, at the `a`, and not again for every letter built on it.

A string is compared the way a tuple is, one place after another, which is why the inner loop can `zip` two strings and walk their letters as chapter 7 walked a name.

`signatures.get(master)` is the careful way to ask a dictionary, from chapter 22. If a glyph lacks a layer, the master isn't in the dictionary at all, and `get` answers `None` where square brackets would stop the script.

## Break it on purpose

Open `n` in the Glyph window, switch to the Bold, click one node on a straight part of the stem and press Delete. Then open `A`, switch to the Light, and delete its anchors. Run the script.

```text
A: anchors
    Light anchors: none
    Regular anchors: acute bottom grave ogonek top
    Bold anchors: acute bottom grave ogonek top
n: contours
    Light and Bold: contour 1: 20 nodes and 19
132 glyphs compared in 3 masters, 2 don't match.
73 glyphs are built automatically and were left out.
```

If you deleted a node on a curve, its handles went with it and your second number is smaller. Now undo both changes with **Edit > Undo** in each glyph, and run again until the count is back to 0. Don't go on with a damaged `n`. Tomorrow needs it whole.

## What the check doesn't see

Two skeletons can be equal and the glyph can still come out wrong. The signature of a square is `oooo` wherever its first node is. If the Light starts at the bottom left and the Bold starts at the top right, the check passes, and the shape between them turns inside out on the way. The same goes for two contours of equal build stored in a different order, such as the two dots of a dieresis.

Fly's own note on its comparison says as much: it isn't a certificate for export, and coordinates are outside it. FontLab also has a test of its own, `isCompatible`, on layers. It takes a second argument called `strong`, and I couldn't find out what that adds, so this book doesn't use it.

## What you learned

Masters can be mixed only when their drawings are compatible: the same contours, the same number of nodes in each, the same kinds of node in the same places. `check_glyph` reduces each master's layer to a signature, a tuple of tuples and strings, and comparing two signatures with `==` compares their whole structure in one step. A total can agree where the structure doesn't, so compare the structure and then report the first place it differs. An equal skeleton is necessary and not sufficient, because the check ignores where each contour starts.

## Try it yourself

1. Print `masters_model.summary(signatures["Regular"])` for `a`. It returns four counts. Which is which?
2. Change `explain` so that it also reports components, in the way it reports anchors. Test it on a made-up `signatures` dictionary before you trust it.
3. Write the two made-up skeletons that `first_difference` can't tell apart although the drawings would twist. What would the function need to be given to see it?

## Next

Chapter 103 looks at where each contour starts, which today's check passes over, and moves a start point with a little arithmetic on positions.
