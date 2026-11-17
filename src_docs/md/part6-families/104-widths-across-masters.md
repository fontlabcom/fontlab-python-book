---
this_file: src_docs/md/part6-families/104-widths-across-masters.md
---

# 104. Widths across masters

Thursday of week twenty. The cookbook has a nutrition table at the back of every chapter: energy, fat, sugar, salt, and a row of totals in Bold. The typesetter asks one question before she builds it. If she sets the totals in Bold under figures in Regular, will the columns still line up?

In chapter 66 Mira made sure the figures of each weight share one width. That answers a narrower question, the one about a column set in a single weight. The typesetter is asking about two weights in one column, and nobody has looked at that.

Looking at it needs a table with two directions: glyphs down the side, masters across the top. You've built tables as lists of rows. Today's is a dictionary whose values are dictionaries, and most of the chapter is about reading one of those without getting lost.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The figures as chapter 66 left them.

I couldn't run the code in FontLab 9. The widths below are read from Plum's source file, with the four currency signs at the widths chapter 66 gave them. The widths of `period` and `hyphen` in step 3 are the shipped ones. If you've changed those, your numbers differ and the lesson doesn't.

## Step 1: One glyph in every master

Chapter 101's exercise used `masters_model.widths`. It takes a glyph and the list of masters and gives back pairs:

```python
import fly.ap.core.scripting as scripting
import fly.ap.masters.inspect.model as masters_model

package = scripting.current_package()
masters = masters_model.master_order(package)
pairs = masters_model.widths(package.findName("zero"), masters)
print(pairs)
row = dict(pairs)
print(row["Bold"])
```

```text
[('Light', 456.0), ('Regular', 490.0), ('Bold', 490.0)]
490.0
```

A list of pairs becomes a dictionary with `dict`, as in chapter 94. Now the width can be asked for by the master's name, which is the rule from chapter 101: by name, never by position.

The widths come back as numbers with a decimal point. They're whole numbers in Plum, and `:.0f` in an f-string prints them without the tail.

## Step 2: A dictionary of those

One such row per glyph, kept under the glyph's name:

```python
table = {}
for name in ["zero", "one", "two"]:
    table[name] = dict(masters_model.widths(package.findName(name), masters))

print(table["zero"])
print(table["zero"]["Light"])
```

```text
{'Light': 456.0, 'Regular': 490.0, 'Bold': 490.0}
456.0
```

Chapter 73 had a dictionary inside a dictionary, the orders for each master. The reading rule is the same. `table["zero"]` is the inner dictionary, one glyph's row. `table["zero"]["Light"]` goes into that row and takes one number out. Read the brackets from left to right, as you'd run a finger down the side of a table and then across.

Which key goes outside is your choice, and it decides what's cheap to ask. With the glyph outside, "all the widths of `zero`" is one lookup. "All the widths in Bold" isn't stored anywhere. You collect it with a loop:

```python
bold = [table[name]["Bold"] for name in table]
```

Had you built it the other way, master outside, the second question would be one lookup and the first a loop. Neither is wrong. Pick the one that matches the question you ask more often, and write a function for the other.

## Step 3: The mistake

Mira's first version filled the inner dictionary by hand, and to save a line she made the empty row once, before the loop:

```python
row = {}
table = {}
for name in ["zero", "period", "hyphen"]:
    for master, width in masters_model.widths(package.findName(name), masters):
        row[master] = width
    table[name] = row

for name in table:
    print(name, table[name])
```

```text
zero {'Light': 348.0, 'Regular': 348.0, 'Bold': 348.0}
period {'Light': 348.0, 'Regular': 348.0, 'Bold': 348.0}
hyphen {'Light': 348.0, 'Regular': 348.0, 'Bold': 348.0}
```

Three glyphs, all 348 wide in every weight. That's the hyphen's row, three times.

There's one `row`. `table[name] = row` doesn't copy it. It puts the same dictionary under a second name, and a third. Each turn of the loop then writes over the numbers in that one dictionary, and at the end all three names lead to whatever the last glyph left there.

```python
print(table["zero"] is table["hyphen"])
```

```text
True
```

`is` asks whether two names lead to the same object, which is a harder test than `==`. You've used it with `None` since chapter 8, where there's only one `None` to lead to.

The repair is to make a new dictionary on every turn. Move `row = {}` inside the outer loop, or do what step 2 did: `dict(...)` builds a fresh one each time it's called. It's a quiet fault, because every row looks like a proper row. On the figures alone Mira wouldn't have seen it at all, since their rows really are alike. She saw it because she'd put a period in the test.

## Step 4: Turn the table round

Step 3 left you with a table of three hyphens. Build step 2's table again before you go on, and then, to ask "does this master keep its figures on one width?", collect the names under each width:

```python
table = {}
for name in ["zero", "one", "two"]:
    table[name] = dict(masters_model.widths(package.findName(name), masters))


def by_width(table, master):
    found = {}
    for name in table:
        width = table[name][master]
        if width not in found:
            found[width] = []
        found[width].append(name)
    return found


print(by_width(table, "Regular"))
```

```text
{490.0: ['zero', 'one', 'two']}
```

It's the grouping from chapter 100: a dictionary of lists, with a new empty list made when a key is first seen, inside the loop, where it belongs. If the result has one key, the master is tabular. If it has two, the shorter list holds the culprits.

## The whole script

```python
#FLM: Master Widths
# Prints the widths of the tabular glyphs in every master and says
# whether each master keeps them on one width. Changes nothing.
import fly.ap.core.scripting as scripting
import fly.ap.masters.inspect.model as masters_model
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


# Chapter 39's tell, written out again so this script runs by itself.
def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


TABULAR = ["zero", "one", "two", "three", "four",
           "five", "six", "seven", "eight", "nine",
           "dollar", "Euro", "sterling", "yen"]


def width_table(package, names, masters):
    table = {}
    for name in names:
        glyph = package.findName(name)
        if glyph is None:
            continue
        table[name] = dict(masters_model.widths(glyph, masters))
    return table


def by_width(table, master):
    found = {}
    for name in table:
        width = table[name][master]
        if width not in found:
            found[width] = []
        found[width].append(name)
    return found


def usual_width(found):
    best = None
    for width in found:
        if best is None or len(found[width]) > len(found[best]):
            best = width
    return best


def main():
    package = scripting.current_package()
    if package is None:
        tell("Open a font first.")
        return
    masters = masters_model.master_order(package)
    table = width_table(package, TABULAR, masters)

    print(f"{'':<10}" + "".join([f"{master:>9}" for master in masters]))
    for name in table:
        print(f"{name:<10}" + "".join([f"{table[name][m]:>9.0f}" for m in masters]))

    problems = 0
    usual = {}
    for master in masters:
        found = by_width(table, master)
        usual[master] = usual_width(found)
        if len(found) == 1:
            print(f"{master}: one width, {usual[master]:.0f}")
            continue
        for width in found:
            if width != usual[master]:
                problems += len(found[width])
                print(f"{master}: {' '.join(found[width])} at {width:.0f}, the rest at {usual[master]:.0f}")

    sharing = {}
    for master in masters:
        if usual[master] not in sharing:
            sharing[usual[master]] = []
        sharing[usual[master]].append(master)
    for width in sharing:
        print(f"{width:.0f}: {' and '.join(sharing[width])}")
    print(f"{len(table)} glyphs in {len(masters)} masters, {problems} off the column.")


main()
```

Save it as `master_widths.py`. It prints:

```text
              Light  Regular     Bold
zero            456      490      490
one             456      490      490
two             456      490      490
three           456      490      490
four            456      490      490
five            456      490      490
six             456      490      490
seven           456      490      490
eight           456      490      490
nine            456      490      490
dollar          456      490      490
Euro            456      490      490
sterling        456      490      490
yen             456      490      490
Light: one width, 456
Regular: one width, 490
Bold: one width, 490
456: Light
490: Regular and Bold
14 glyphs in 3 masters, 0 off the column.
```

Notes on the listing.

`width_table` skips a name the font doesn't have. `findName` gives `None` for those, and a missing yen shouldn't stop a report about figures.

`usual_width` finds the width that most glyphs have. It's the widest-glyph loop from chapter 18, which keeps the best one seen so far, with the length of a list as the thing compared. The script needs it so that, when a master has two widths, it can name the few glyphs that left the column and not the many that stayed.

The header line starts with `f"{'':<10}"`, an empty string padded to ten places. It's there so the master names stand over their columns. Inside an f-string written with double quotes, the empty string has to use single ones.

The last block turns the result round once more: masters collected under their usual width. That's the line the typesetter wanted.

The script trusts chapter 101. `masters_model.widths` gives `None` for a master whose layer is missing, and `:>9.0f` can't format `None`: the script would stop with a `TypeError` in the middle of the table. I left it that way on purpose. Run `masters_report.py` first, and if it says a layer is missing, that's the thing to repair before you ask about widths.

The dictionaries keep the order in which things went in, so the rows come out in the order of `TABULAR` and the columns in the order of `masters`. Nothing is sorted, because the order you typed is the order a person expects to read figures in.

## What the answer is

Regular and Bold share 490. A Bold total sits under Regular figures digit for digit, and the table holds. The Light is narrower, 456, so a column that mixes Light with either of the others will drift by 34 units a digit. Oskar's answer to the typesetter is two sentences: totals in Bold are safe, and don't mix Light into a column of figures.

Whether the Light ought to be 490 as well is a design question. Its figures are thinner and would look lost in so much room, which is likely why Sora Sagano drew them narrower. The script lays the numbers out, and a person reads them and decides. Nobody changes anything today.

There's a second thing in that output, for the art director's in-between weight. Whatever lies between Regular and Bold lies between 490 and 490. A weight worked out from those two will have figures 490 wide without anybody arranging it. Chapter 106 shows why.

## Break it on purpose

In the Glyph window, switch to the Bold master, open `seven` and type 480 into its width field. Run the script. Under the table it prints:

```text
Light: one width, 456
Regular: one width, 490
Bold: seven at 480, the rest at 490
456: Light
490: Regular and Bold
14 glyphs in 3 masters, 1 off the column.
```

The table above those lines shows 480 in the Bold column too, and in fourteen rows of near-identical numbers you'd likely read past it. The sentence under the table is why the script doesn't stop at printing. Undo the change and run again until the last line says 0.

## What the report doesn't say

It compares advance widths. A figure can have the right width and sit off-center in it, which was chapter 66's subject. It also covers only the glyphs in `TABULAR`. Your fraction figures from chapter 92 aren't in the list, and neither is the space a typesetter uses to pad a column.

## What you learned

A dictionary of dictionaries holds a table with two directions, and `table[glyph][master]` reads it one bracket at a time from the left. The key you put outside decides which question is a single lookup, and a short function turns the table round for the other question. Assigning a dictionary doesn't copy it, so a row made once outside the loop becomes one row under many names, which `is` will confirm. Each master of Plum keeps its figures on one width, Regular and Bold share theirs, and the Light doesn't.

## Try it yourself

1. Add the ten `.numr` and ten `.dnom` glyphs from chapter 92 as a second group and report it separately. What do you expect of glyphs made empty by chapter 40's script?
2. Write `by_master(table)` that returns the same numbers with the master as the outer key. Check one number both ways.
3. For every glyph in the font, count how many have the same width in Regular and Bold. On shipped Plum it was all 205. Chapter 68 changed that in your font: by how many?

## Next

The masters agree where they should. Chapter 105 copies things from one master to the others: anchors that were placed in the Regular and are wanted in all three.
