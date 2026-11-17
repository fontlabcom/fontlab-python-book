---
this_file: src_docs/md/part6-families/107-axes-and-instances.md
---

# 107. Axes and instances

Tuesday of week twenty-one. The art director liked the idea of a Medium so much that she talked to the publisher, and the publisher talked to somebody else. This morning's email has a list:

> Thin, ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black. Nine weights, please, for the rest of the series.

Mira reads it twice. "We have three."

She has three drawings. How many weights the font can make from them is another question, and the font holds part of the answer. Yesterday you typed 400 and 700 into a script because chapter 101 had printed them. Today you ask the font where its masters sit, what it calls the scale they sit on, and which weights it has already been told to produce. Then you hold the client's list against it.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `tell`.
- Yesterday's `share`, which turned a weight into a part of the way between two masters.

I couldn't run the code in FontLab 9. I ran it against a stand-in built from Plum's source file, and the output below comes from there.

## Step 1: The axis

A scale that a font's drawings vary along is an **axis**. Plum has one:

```python
import fly.ap.core.scripting as scripting

package = scripting.current_package()
axis = list(package.axes)[0]
print(axis.name, axis.tag, axis.shortName)
print(axis.minimal, axis.default, axis.maximum)
```

```text
weight wght wt
300.0 400.0 700.0
```

A font can have several axes, so `package.axes` is a collection, and `list` makes a plain list of it that the whole script can count. Chapter 106 took the first one straight off with `package.axes[0]`, which works as well.

Three names for one thing, and each has its user. `weight` is for people. `wght` is the tag that goes into the exported font, four characters like a feature tag, and it's the one a browser or a layout program asks for. `wt` is FontLab's own short name, the one its Python objects use as a key.

The lowest value is spelled `minimal`. You'd guess `minimum`, since its partner is `maximum`. I did, and the code I checked it against says otherwise.

## Step 2: Where a master sits

Each master has a **location**, its place on every axis the font has. With one axis that's one number:

```python
def on_axis(axis, location):
    return float(axis.valueWeight(location, 0.0))

for name in package.masters:
    print(name, on_axis(axis, package.location(name)))
```

```text
Light 300.0
Regular 400.0
Bold 700.0
```

`valueWeight` is an odd name for "the value of this location on this axis". The word weight in it has nothing to do with bold or light. It would be called the same on a width axis. The `0.0` is what to answer if the location says nothing about this axis.

Yesterday's `weight_of` got the same numbers by indexing the location with the short name. Both routes are in code I trust. I've moved to this one because it reads a location wherever it comes from, and in a minute one will come from somewhere else.

## Step 3: Small records

A master is now two facts that belong together: a name and a value. You've kept such pairs as tuples. Today there will be three facts for some rows, and `row[2]` says nothing to a reader. A small dictionary with the same keys in every row says what each thing is:

```python
def by_value(record):
    return record["value"]


def master_records(package, axis):
    records = []
    for name in package.masters:
        value = on_axis(axis, package.location(name))
        records.append({"name": name, "value": value})
    return sorted(records, key=by_value)
```

Chapter 104 kept a dictionary of dictionaries, a table you look things up in. This is the other common shape, a list of dictionaries: rows you walk through in order. Programmers call such a row a record.

The list is sorted by value, with a key function as in chapter 36. Chapter 101 said why: `package.masters` comes in the order the masters were made, and nothing says that's light to bold.

## Step 4: Instances

A master is a drawing. An **instance** is a weight the font is told to produce: a name and a location, and no drawing of its own. FontLab makes its outlines by yesterday's sum when you export. An instance can sit on a master, and then there's nothing to work out.

```python
def instance_records(package, axis):
    records = []
    for instance in package.instances:
        value = on_axis(axis, instance.location)
        records.append({"name": instance.name, "value": value,
                        "export": instance.exportable})
    return sorted(records, key=by_value)

print(instance_records(package, axis))
```

Here's where I have to be plain about what I don't know. Plum's source file doesn't list instances the way it lists masters. It has a note on the axis that names three places, Light, Regular and Bold, at 300, 400 and 700. Whether FontLab 9 hands those to Python as three instances, or as none, I can't tell from the file. So the script counts what it gets, and both answers are fine:

```text
[]
```

or three records. What you won't see either way is a Medium. Nobody has asked this font for one before.

## Step 5: Hold the list against it

The client's nine weights, with the numbers custom gives them:

```python
WANTED = [
    ("Thin", 100),
    ("ExtraLight", 200),
    ("Light", 300),
    ("Regular", 400),
    ("Medium", 500),
    ("SemiBold", 600),
    ("Bold", 700),
    ("ExtraBold", 800),
    ("Black", 900),
]
```

For each, find the two masters it lies between and say how far along. `zip(masters, masters[1:])` pairs each master with the next one, the trick from chapter 61:

```python
def place(value, masters):
    if value < masters[0]["value"]:
        return f"below {masters[0]['name']}, no drawing to lean on"
    if value > masters[-1]["value"]:
        return f"above {masters[-1]['name']}, no drawing to lean on"
    for low, high in zip(masters, masters[1:]):
        if low["value"] < value < high["value"]:
            t = (value - low["value"]) / (high["value"] - low["value"])
            return f"{low['name']} to {high['name']}, t {t:.3f}"

masters = master_records(package, axis)
for name, value in WANTED:
    print(f"{name:<12}{value:>5}  {place(value, masters)}")
```

```text
Thin          100  below Light, no drawing to lean on
ExtraLight    200  below Light, no drawing to lean on
Light         300  None
Regular       400  None
Medium        500  Regular to Bold, t 0.333
SemiBold      600  Regular to Bold, t 0.667
Bold          700  None
ExtraBold     800  above Bold, no drawing to lean on
Black         900  above Bold, no drawing to lean on
```

Three lines say `None`, and they're the three weights the font is surest of.

`low < value < high` is true for a value strictly between the two. 400 is not strictly between 300 and 400, nor between 400 and 700. It's on the fence, and the test leaves the fence out on both sides. So the loop ends without a `return`, the function runs off its end, and a function that does that hands back `None`, as chapter 16 found.

You could change one `<` to `<=`. Then 400 would be "Light to Regular, t 1.000", which is true and unhelpful. The better answer is to say what it is, first. These lines go at the top of `place`, before the others:

```python
def place(value, masters):
    for master in masters:
        if master["value"] == value:
            return f"is the {master['name']} master"
```

When a function sorts things into cases, write down what happens at the borders before you write the middle. The middle is rarely where it goes wrong.

## The whole script

```python
#FLM: List Instances
# Reads the weight axis, the masters on it and the font's instances,
# and says where each wanted weight falls. Changes nothing.
import fly.ap.core.scripting as scripting
import halfmoon
from fly import fl

WANTED = [
    ("Thin", 100),
    ("ExtraLight", 200),
    ("Light", 300),
    ("Regular", 400),
    ("Medium", 500),
    ("SemiBold", 600),
    ("Bold", 700),
    ("ExtraBold", 800),
    ("Black", 900),
]


def by_value(record):
    return record["value"]


def on_axis(axis, location):
    return float(axis.valueWeight(location, 0.0))


def master_records(package, axis):
    records = []
    for name in package.masters:
        value = on_axis(axis, package.location(name))
        records.append({"name": name, "value": value})
    return sorted(records, key=by_value)


def instance_records(package, axis):
    records = []
    for instance in package.instances:
        value = on_axis(axis, instance.location)
        records.append({"name": instance.name, "value": value,
                        "export": instance.exportable})
    return sorted(records, key=by_value)


def place(value, masters):
    for master in masters:
        if master["value"] == value:
            return f"is the {master['name']} master"
    if value < masters[0]["value"]:
        return f"below {masters[0]['name']}, no drawing to lean on"
    if value > masters[-1]["value"]:
        return f"above {masters[-1]['name']}, no drawing to lean on"
    for low, high in zip(masters, masters[1:]):
        if low["value"] < value < high["value"]:
            t = (value - low["value"]) / (high["value"] - low["value"])
            return f"{low['name']} to {high['name']}, t {t:.3f}"


def main():
    if fl.CurrentFont() is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    axes = list(package.axes)
    if not axes:
        print("This font has no axis. It is one drawing.")
        return
    axis = axes[0]
    print(f"Axis {axis.name} ({axis.tag}, short name {axis.shortName}): "
          f"{axis.minimal:g} to {axis.maximum:g}, default {axis.default:g}")
    masters = master_records(package, axis)
    print(f"{len(masters)} masters:")
    for record in masters:
        print(f"  {record['name']:<12}{record['value']:>5g}")
    instances = instance_records(package, axis)
    print(f"{len(instances)} instances:")
    for record in instances:
        mark = "" if record["export"] else "  (not exported)"
        print(f"  {record['name']:<12}{record['value']:>5g}{mark}")
    have = [record["value"] for record in instances]
    print(f"{len(WANTED)} weights wanted:")
    for name, value in WANTED:
        listed = "listed" if value in have else "not listed"
        print(f"  {name:<12}{value:>5}  {listed:<11} {place(value, masters)}")


main()
```

Save it as `list_instances.py` and run it:

```text
Axis weight (wght, short name wt): 300 to 700, default 400
3 masters:
  Light         300
  Regular       400
  Bold          700
0 instances:
9 weights wanted:
  Thin          100  not listed  below Light, no drawing to lean on
  ExtraLight    200  not listed  below Light, no drawing to lean on
  Light         300  not listed  is the Light master
  Regular       400  not listed  is the Regular master
  Medium        500  not listed  Regular to Bold, t 0.333
  SemiBold      600  not listed  Regular to Bold, t 0.667
  Bold          700  not listed  is the Bold master
  ExtraBold     800  not listed  above Bold, no drawing to lean on
  Black         900  not listed  above Bold, no drawing to lean on
```

If your FontLab lists three instances, three lines in the last block say `listed`.

Notes on the listing.

`:g` in a format prints a number the short way: `300.0` as `300`, and `412.5` as `412.5`. The values arrive as floats and none of them needs its `.0`.

`"" if record["export"] else "  (not exported)"` is the one-line `if` from chapter 40. An instance can be switched off for export and kept in the list, and the report should say so.

The script looks at the first axis and no further. A font with weight and width would need `place` to think in two directions at once, and Plum doesn't ask that of us.

## Break it on purpose

Take the `sorted` out of `master_records`, so it ends `return records`. Run it. On Plum you may see no change at all: if `package.masters` happens to come light to bold, the unsorted list is the sorted one.

Then make it fail on purpose. Put `records.reverse()` before the `return` and run again. The first lines are:

```text
  Thin          100  not listed  below Bold, no drawing to lean on
  ExtraLight    200  not listed  below Bold, no drawing to lean on
  Light         300  not listed  is the Light master
  Regular       400  not listed  is the Regular master
  Medium        500  not listed  below Bold, no drawing to lean on
```

Medium is "below Bold" and has lost its neighbors. `place` reads `masters[0]` as the lightest and trusts the list to be in order. It never checks. The `sorted` in `master_records` is the only thing that puts the list in order, and it looked like a nicety.

Put the `sorted` back and take the `reverse` out.

## What Mira writes back

The report answers the email better than a yes would.

Five of the nine are safe. Three are drawings, and Medium and SemiBold lie between two drawings, a third and two thirds of the way from Regular to Bold.

Four are outside. Thin and ExtraLight are lighter than anything Mira has drawn, ExtraBold and Black are heavier, and yesterday's hyphen showed what the sum does out there. A Thin at 100 is twice as far below the Light as the Light is below the Regular.

So she writes: five weights now. The other four need a new drawing at each end, a Thin and a Black, and those are weeks of work, not a script.

## What you learned

An axis has a name for people, a tag for the exported font and a short name for FontLab's objects, and a master's location says where it sits on that axis. An instance is a named place on the axis with no drawing of its own. A list of small dictionaries with the same keys keeps facts that belong together in rows you can sort and walk. A function that sorts values into cases needs its borders decided first, because a value that sits on a border falls through tests written for the middle.

## Try it yourself

1. Add a `"share"` key to each wanted weight's row: build a list of records from `WANTED` with `name`, `value` and the `t` from yesterday's `share`, or `None` when the weight is a master or outside. Print only the rows where it isn't `None`.
2. The client's second thought: "and a Book, a little heavier than Regular". Add `("Book", 450)` to `WANTED`, keep the list in order of weight with `sorted` and a key function for tuples, and read where it falls. It should say `Regular to Bold, t 0.167`.
3. Print `axis.designMin` and `axis.designMax` next to `minimal` and `maximum`. In Plum I expect the same numbers. A font can show its users one scale and draw on another, and you should know the two exist before you meet a font where they differ.

## Next

Five weights are within reach and the font lists none of them, or three. Chapter 108 turns the table of wanted weights into a plan for instances, and looks hard at the last step, the one that writes them into the font.
