---
this_file: src_docs/md/part4-space/076-pairs-with-no-glyph.md
---

# 76. Pairs for glyphs that are gone

Monday of week fifteen. Ines wants the kerning in a spreadsheet by Wednesday, for a reviewer outside the studio. Before it goes, she asks a question she has learned to ask of every font that has been renamed, trimmed and extended for three months.

"Does the kerning mention anything that isn't there?"

Kerning is kept by name. A pair says `A` and `V`, and a class lists `A`, `Aacute`, `Aring`. Rename a glyph or delete it, and whatever still carries the old name points at nothing. Such a pair is called an orphan. It does no harm on screen. It may stop an export, which I haven't tried, or travel into a spreadsheet and come back as a question nobody can answer.

Today's script looks for three kinds of loose end and changes nothing.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `tell`.
- The kerning as chapter 75 left it: 101, 104 and 102 pairs.

I couldn't run the code in FontLab 9. The outputs below are worked out from Plum's source file. I also haven't seen what FontLab 9 does to kerning when you rename or delete a glyph in the Font window. It may tidy up after you. A check like this one is how you'd find out.

## Step 1: Two sets and a minus sign

You need two collections of names: the ones the kerning uses and the ones the font has. Chapter 25 introduced the set, a collection that holds each thing once, and chapter 40 built the second of these two:

```python
import fly.ap.core.scripting as scripting
from fly import fl

font = fl.CurrentFont()
package = scripting.current_package()
have = {glyph.name for glyph in font.glyphs}
pairs = scripting.kerning_pairs(package, "Regular")

used = set()
for first, second in pairs:
    used.add(first)
    used.add(second)
print(len(used))
```

```text
54
```

The 104 pairs of the Regular use 54 different names between them.

Now the question. Sets can be subtracted. `used - have` is a new set with everything that's in `used` and not in `have`:

```python
gone = sorted(used - have)
print(len(gone), gone[:4])
```

```text
18 ['@L_A', '@L_O', '@L_T', '@L_U']
```

That's called the difference of two sets. It replaces a loop with an `if` and a `not in` inside it, and it reads the way you'd say it: the used names, less the ones we have.

## Step 2: Eighteen false alarms

Eighteen names that aren't in the font would be bad news. Look at the four you can see. Each begins with `@`.

They're classes. A pair can name a class on either side, a class isn't a glyph, and so no class name will ever be in `have`. The check compared two lists that weren't lists of the same kind of thing.

It's the mistake to expect whenever you subtract one set from another. Before the minus sign, ask whether both sides hold the same kind of name. Here the fix is to split `used` in two, and check each half against its own list:

```python
glyph_names = {name for name in used if not name.startswith("@")}
class_names = {name[1:] for name in used if name.startswith("@")}
classes = scripting.kerning_classes(package, "Regular")

print(sorted(glyph_names - have))
print(sorted(class_names - set(classes)))
```

```text
[]
[]
```

Both are set comprehensions with a condition. The second takes the `@` off with `name[1:]`, as chapter 74 did, because the dictionary of classes has the names without it. `set(classes)` makes a set of a dictionary's keys.

Two empty lists. Every glyph a pair names is in the font, and so is every class.

## Step 3: Can the check find anything?

An empty result has two explanations. Either the font is clean, or the check can't see dirt. You've met the second kind already: a check that compared classes with glyphs would have cried wolf on every font, and one with the test the wrong way round would stay silent on every font.

So give the check something to find. Put the work into functions that take plain dictionaries and a set, and feed them a small kerning table you made up, with faults whose number you know:

```python
def orphans(pairs, classes, have):
    used = set()
    for first, second in pairs:
        used.add(first)
        used.add(second)
    glyph_names = {name for name in used if not name.startswith("@")}
    class_names = {name[1:] for name in used if name.startswith("@")}
    return sorted(glyph_names - have), sorted(class_names - set(classes))


def lost_members(classes, have):
    rows = []
    for name in sorted(classes):
        members, place = classes[name]
        gone = sorted(set(members) - have)
        if gone:
            rows.append((name, gone))
    return rows


test_have = {"A", "Aacute", "V"}
test_pairs = {("A", "V"): -60, ("A", "V.old"): -60, ("@L_A", "@R_gone"): -40}
test_classes = {"L_A": (["A", "Aacute", "Aring.old"], None)}

print(orphans(test_pairs, test_classes, test_have))
print(lost_members(test_classes, test_have))
```

```text
(['V.old'], ['R_gone'])
[('L_A', ['Aring.old'])]
```

Three faults went in and three came out: a pair for a glyph that isn't there, a pair for a class nobody made, and a class with a member that's gone. The second function is the third kind of loose end. It turns each class's member list into a set and subtracts the font from it.

Neither function touches FontLab. They take dictionaries and a set and give back lists, which is why a made-up table could stand in for a font. Whenever a check comes back empty, this is the way to learn whether to believe it.

## Step 4: Pairs that some masters lack

There's a fourth loose end, and chapter 75 circled it: a pair that exists in one master and not in the others. It's another difference of sets. The keys of the kerning dictionaries are the pairs, so collect all of them, then ask of each master which ones it lacks:

```python
tables = {master: scripting.kerning_pairs(package, master) for master in MASTERS}
everything = set()
for master in tables:
    everything = everything | set(tables[master])
```

The first line makes a dictionary with one kerning table for each master, under the master's name. It's a dictionary comprehension, the kind chapter 75 used: a list comprehension with a key and a colon in front. It needs `MASTERS = ["Light", "Regular", "Bold"]` above it.

The upright bar joins two sets into one that holds everything from both. That's called the union. After the loop, `everything` holds each pair that any master has, once.

## The whole script

```python
#FLM: Orphan Pairs
# Reports kerning that points at nothing: pairs for missing glyphs or classes,
# class members that are gone, and pairs that some masters lack.
import halfmoon
import fly.ap.core.scripting as scripting
from fly import fl

MASTERS = ["Light", "Regular", "Bold"]


def orphans(pairs, classes, have):
    used = set()
    for first, second in pairs:
        used.add(first)
        used.add(second)
    glyph_names = {name for name in used if not name.startswith("@")}
    class_names = {name[1:] for name in used if name.startswith("@")}
    return sorted(glyph_names - have), sorted(class_names - set(classes))


def lost_members(classes, have):
    rows = []
    for name in sorted(classes):
        members, place = classes[name]
        gone = sorted(set(members) - have)
        if gone:
            rows.append((name, gone))
    return rows


def uneven(tables):
    everything = set()
    for master in MASTERS:
        everything = everything | set(tables[master])
    rows = []
    for pair in sorted(everything):
        missing = [master for master in MASTERS if pair not in tables[master]]
        if missing:
            rows.append((pair, missing))
    return len(everything), rows


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    have = {glyph.name for glyph in font.glyphs}
    tables = {}
    for master in MASTERS:
        pairs = scripting.kerning_pairs(package, master)
        classes = scripting.kerning_classes(package, master)
        tables[master] = pairs
        glyphs, groups = orphans(pairs, classes, have)
        members = lost_members(classes, have)
        print(f"{master}: {len(pairs)} pairs, {len(glyphs)} missing glyphs, "
              f"{len(groups)} missing classes, {len(members)} classes with lost members.")
        for name in glyphs:
            print(f"  no glyph {name}")
        for name in groups:
            print(f"  no class @{name}")
        for name, gone in members:
            print(f"  @{name} lists {', '.join(gone)}")

    total, rows = uneven(tables)
    print(f"{total} different pairs, {len(rows)} not in every master.")
    for (first, second), missing in rows:
        print(f"  {first:<14}{second:<12}not in {', '.join(missing)}")


main()
```

Save it as `orphan_pairs.py`. On the practice font it should print:

```text
Light: 101 pairs, 0 missing glyphs, 0 missing classes, 0 classes with lost members.
Regular: 104 pairs, 0 missing glyphs, 0 missing classes, 0 classes with lost members.
Bold: 102 pairs, 0 missing glyphs, 0 missing classes, 0 classes with lost members.
104 different pairs, 3 not in every master.
  P             @R_aacute   not in Light, Bold
  P             a           not in Light, Bold
  questiondown  exclamdown  not in Light
```

Notes on the listing.

The long `print` is split over two lines inside its brackets. Two f-strings that stand next to each other with nothing between them are joined into one, so this is a single string. It's a way to keep a long line readable.

`uneven` returns a count and a list, and `main` unpacks them. The pairs come out in the order of `sorted`, which compares tuples part by part, as in chapter 74. `@` sorts before the small letters, so the class pair comes first.

`missing` is a comprehension over the masters that keeps the names of those without the pair. An empty list means the pair is everywhere, and `if missing:` skips it.

## What the report says

Plum has no orphans. Three months of renaming and nothing points at a missing glyph. Ines says that's the first font this year she could say that of, and takes the three lines at the bottom to Mira.

`P` before `a`, and before the `á` family, is −10 in the Regular and absent from the other two. Chapter 75 kept those two because −10 is not less than 10. They're small, they're in one master, and nobody remembers making them. `questiondown` before `exclamdown` is 11 in the Regular and 28 in the Bold, and the Light has none.

Mira's answer is that all three are hers to settle, and that a script shouldn't. A pair missing from a master is either an oversight, to be filled in with `set_pair.py`, or a leftover, to be removed from the masters that have it. The report can't tell which. It goes on her list.

## If you do find an orphan

Suppose the report had named one. You'd want to remove the pair, and chapter 73's tool for that is an order with `None`.

As far as I can read Fly's source, that won't work here. `write_kerning` checks every pair in its orders before it writes, and one of the checks is that each glyph exists. A pair that names a missing glyph fails it, even when the order is to remove the pair. The whole batch is refused with a message that begins `Unknown glyph`.

That refusal is sensible for writing and unhelpful for cleaning. I haven't tried it in FontLab 9, and I haven't found another route in Fly. Until I have, remove an orphan by hand: open the Kerning panel, find the pair and delete it there. If it's a class member that's gone, open the Classes panel and take the name out of the class. Then run the report again.

## What you learned

Kerning is kept by name, and a name can outlive its glyph. `a - b` gives the things in set `a` that aren't in set `b`, `a | b` gives everything in either, and `set(d)` makes a set of a dictionary's keys. Before you subtract, check that both sets hold the same kind of thing: class names begin with `@` and are never glyph names. An empty result needs a test, so write the check as a function of plain dictionaries and sets and run it on made-up data with known faults.

## Try it yourself

1. Add a fourth fault to the made-up table: a class `"R_V"` with the members `["V", "W.old"]`. Predict the output of `lost_members` and run it.
2. Sets have a third sign, `&`, for the things that are in both. Use it to count the pairs that all three masters share. You should get 101, which is 104 less the three in the report.
3. Print the names that have kerning in the Regular and none in the Light: the difference of the two masters' `used` sets. You should get two names. Which pairs brought them in?

## Next

The kerning is consistent enough to show. Before the spreadsheet, the reviewer needs something to look at: lines of text where every pair sits between letters that are known to be spaced right. Chapter 77 builds that proof text out of the kerning list.
