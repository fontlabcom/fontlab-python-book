---
this_file: src_docs/md/part6-families/101-more-than-one-drawing.md
---

# 101. More than one drawing

Monday of week twenty. The publisher's art director has seen the cookbook set in Plum and writes two lines to Ines. The Regular is a little light for the ingredient lists, and the Bold is too heavy for them. Could there be something in between? And while Halfmoon is at it, a full range of weights for the rest of the series?

Ines says yes on the telephone and then asks Oskar how long it takes. Oskar looks at Mira.

Plum has three drawings of every glyph: a Light, a Regular and a Bold. FontLab calls them masters. Everything between them can be worked out from them, and that's what this part of the book is for. Before any of it, Mira notices something about her own scripts. Since chapter 40 they have begun with a line she typed by hand, `MASTERS = ["Light", "Regular", "Bold"]`. The scripts know about three masters because she told them. If a fourth arrives, every one of those lines is wrong, and nothing will say so.

Today's script asks the font instead.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.

I couldn't run the code in FontLab 9. I ran the script in plain Python against a stand-in with the glyphs this book has added. The layer order in step 3 is read from Plum's source file, where it's plain to see. What FontLab hands a script may be ordered differently, and step 3 is written so that it doesn't matter.

## Step 1: Ask the font for its masters

```python
import fly.ap.core.scripting as scripting
import fly.ap.masters.inspect.model as masters_model

package = scripting.current_package()
print(package.masters)
print(package.master)
masters = masters_model.master_order(package)
for master in masters:
    print(master, masters_model.location_text(package, master))
```

```text
['Light', 'Regular', 'Bold']
Regular
Light wght 300
Regular wght 400
Bold wght 700
```

`package.masters` is the list of master names, and `package.master`, without the s, is the one you're looking at now. Chapter 95 moved that marker about with `setMaster` and put it back.

`master_order` gives the same names sorted by weight, lightest first. For Plum the two lists agree. In a font where somebody added the Light last, they wouldn't, and a report in the order of creation is hard to read. `location_text` says where each master sits: `wght` is the weight axis and the number is the master's place on it. Chapter 107 is about those numbers. For today they're labels.

## Step 2: A master is a layer in every glyph

A master isn't a thing stored in one place. It's a name, and every glyph is expected to have a layer with that name. Chapter 96 asked a glyph for one:

```python
glyph = package.findName("a")
layer = glyph.findLayer("Bold")
print(layer.name, layer.advanceWidth)
```

`findLayer` gives the layer, or it gives nothing, and "nothing" comes in two forms: Python's `None`, or a hollow object whose `isNull` is true. Test for both, every time. A small function keeps the test in one place:

```python
def has_layer(glyph, master):
    layer = glyph.findLayer(master)
    return layer is not None and not layer.isNull
```

## Step 3: The mistake

A glyph also has a list of all its layers, `glyph.layers`. Mira has a list of three masters and a list of three layers, so she walks them side by side with `zip` from chapter 35:

```python
for master, layer in zip(package.masters, glyph.layers):
    print(master, layer.name)
```

```text
Light Bold
Regular Regular
Bold Light
```

The master called Light is paired with the layer called Bold. Had she printed widths, the table would have looked fine and been upside down, with the Bold's numbers under "Light".

```python
print([layer.name for layer in glyph.layers])
```

```text
['Bold', 'Regular', 'Light']
```

A glyph keeps its layers in the order they were stored, and nothing says this is the order of the masters. In Plum's file every glyph has them backwards. Two lists of the same length aren't two lists in the same order.

So the rule for this whole part: never take a layer by its position. Take the master's name and ask the glyph for the layer with that name.

The same goes for the masters themselves. `package.masters[0]` is whichever master was made first, and in another font that could be the Bold. When a script means the Light, it should say `"Light"`, or take the first name from `master_order`, which at least puts the lightest first.

## Step 4: A loop inside a loop

The question "does every glyph have a layer for every master?" has two "every" in it, and each one is a loop. Put the second inside the first, as chapter 71 did for the glyphs of every kerning class:

```python
from fly import fl

found = {master: 0 for master in masters}
for glyph in fl.CurrentFont().glyphs:
    fl_glyph = package.findName(glyph.name)
    for master in masters:
        if has_layer(fl_glyph, master):
            found[master] += 1
```

The outer loop takes a glyph. For that one glyph, the inner loop runs through all the masters. Then the outer loop takes the next glyph and the inner one starts again from the first master. With 274 glyphs and three masters, the line under the `if` is reached 822 times.

`found` is a dictionary with one counter per master, built with the comprehension from chapter 95. The inner loop adds to the counter that belongs to its master.

The indentation says which loop a line belongs to. `fl_glyph = ...` is done once per glyph. The `if` is done once per glyph and master. If you indent a line one level too deep, it runs three times as often, and Python won't complain.

## The whole script

```python
#FLM: Masters Report
# Lists the font's masters, then looks in every glyph for a layer
# for every master. Changes nothing.
from fly import fl, qt
import fly.ap.core.scripting as scripting
import fly.ap.masters.inspect.model as masters_model
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


# Chapter 39's tell, written out again so this script runs by itself.
def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)



def has_layer(glyph, master):
    layer = glyph.findLayer(master)
    return layer is not None and not layer.isNull


def main():
    package = scripting.current_package()
    if package is None:
        tell("Open a font first.")
        return
    masters = masters_model.master_order(package)
    for master in masters:
        mark = "*" if master == package.master else " "
        print(f"{mark} {master:<9}{masters_model.location_text(package, master)}")

    found = {master: 0 for master in masters}
    strangers = []
    reordered = 0
    count = 0
    for glyph in fl.CurrentFont().glyphs:
        count += 1
        fl_glyph = package.findName(glyph.name)
        for master in masters:
            if has_layer(fl_glyph, master):
                found[master] += 1
        names = [layer.name for layer in fl_glyph.layers]
        for name in names:
            if name not in masters:
                strangers.append(f"{glyph.name}: {name}")
        if [name for name in names if name in masters] != masters:
            reordered += 1

    print(f"{count} glyphs x {len(masters)} masters = {count * len(masters)} layers to find")
    for master in masters:
        print(f"{master:<9}{found[master]:>4} found, {count - found[master]} missing")
    print(f"{len(strangers)} layers that belong to no master")
    for line in strangers:
        print("   ", line)
    print(f"{reordered} glyphs keep their layers in another order")


main()
```

Save it as `masters_report.py`. On my stand-in it prints:

```text
  Light    wght 300
* Regular  wght 400
  Bold     wght 700
274 glyphs x 3 masters = 822 layers to find
Light     274 found, 0 missing
Regular   274 found, 0 missing
Bold      274 found, 0 missing
0 layers that belong to no master
205 glyphs keep their layers in another order
```

My count is for the font as Part 5 left it: Plum's 205 glyphs and the 69 the book has added. Yours depends on how many exercises you did. The three "missing" numbers should be 0 whatever it is. If one isn't, a glyph lacks a drawing in that weight, and nothing in this part will work for it until it has one.

Notes on the listing.

The star marks the master you're looking at. The script reads `package.master` and never changes it, so there's nothing to put back and no `finally`.

There are two inner loops under one outer loop. The first asks about masters, the second walks the glyph's own layers. A glyph can hold layers that aren't masters: a mask you traced from, a backup FontLab made. The script lists those as strangers. They do no harm, and you want to know they're there before a later script copies "every layer".

The last line compares two lists with `!=`. Two lists are equal when they hold the same things in the same order. The comprehension keeps only the layer names that are masters, so a stranger in the middle doesn't count as disorder.

My 205 is the number of glyphs that came with Plum. I've assumed that the glyphs you made with chapter 40's script keep the order in which that script made their layers. I haven't seen it. Whatever your number is, it does no damage: it only tells you how many glyphs would have fooled Mira's `zip`.

The script uses the font for the list of glyphs and the package for their layers, as chapter 96 did.

## Break it on purpose

After the loop that prints the masters, add the line `masters = masters + ["Medium"]`, and run.

```text
274 glyphs x 4 masters = 1096 layers to find
Light     274 found, 0 missing
Regular   274 found, 0 missing
Bold      274 found, 0 missing
Medium      0 found, 274 missing
```

That's what a typed list does when it disagrees with the font: the script looks for layers that don't exist. Here it says so, because `has_layer` tests what `findLayer` gave back. A script that went straight on to `layer.advanceWidth` would have stopped with an error on the first glyph, or worse, read a width from the hollow object. Take the line out.

## What the report doesn't say

It says each glyph has a layer for each master. It doesn't say the three drawings in those layers belong together. A Light `a` with two contours and a Bold `a` with three would both be "found". Whether the drawings match is tomorrow's question.

It also doesn't say that three masters are enough for the art director's range. They're the corners. What lies between them is worked out, and the working out starts in chapter 106.

And it reads one font. Oskar's old families were six files with one master each, and for those the question "does every weight have this glyph?" is asked across files, not across layers. Chapter 99 walked over open fonts, and chapter 113 will do it for a folder. Plum keeps its weights in one file, which is why a loop inside a loop is enough today.

## What you learned

A font's masters are names, read from `package.masters` or in weight order from `master_order`, and a script should ask for them and never type them. Each master is a layer of that name in every glyph, fetched with `findLayer` and tested for both `None` and `isNull`. A glyph's own list of layers follows no order you can count on, so layers are taken by name and never by position. A loop inside a loop asks a question about every pair, here every glyph with every master, and the indentation decides how often each line runs.

## Try it yourself

1. Print a table of advance widths: one row for each of `a`, `n`, `H`, `zero`, one column per master. Use `masters_model.widths(fl_glyph, masters)`, which returns pairs of master and width.
2. Go back to one script from Part 3 that starts with `MASTERS = [...]` and replace the typed list with the font's. What has to come first?
3. Add a third inner question: in how many glyphs is one master's layer empty while another's isn't? Chapter 96's bounding box is one way to tell.

## Next

Every glyph has its three layers. Chapter 102 asks whether the three drawings in them have the same skeleton, which they must before anything can be worked out between them.
