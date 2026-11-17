---
this_file: src_docs/md/part4-space/075-tiny-pairs.md
---

# 75. Pairs too small to matter

Friday of week fourteen. Yesterday's list had a far end, and the first exercise looked at it: pairs of 7 and 8 units.

Plum is drawn on 1,000 units to the em. Set at 10 points, a pair of 7 units moves a letter by seven hundredths of a point. Nobody sees that. Each such pair still costs a line in the kerning list, a moment of somebody's attention at every review, and a few bytes in every exported font.

Fonts that have been kerned by eye, or by an automatic tool, can carry hundreds of these. Plum has ten, which is enough to learn on and few enough to check by hand. Today you find them, decide which may go, and remove those. It's the first script in this part that deletes, so it starts as a dry run.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The helpers `ask` and `tell` from chapter 39. The scripts below write them out again, so each one runs by itself.
- The kerning as chapter 73 left it. Chapter 74 changed nothing.

I couldn't run the code in FontLab 9. The lists below are worked out from Plum's source file.

## Step 1: Find them

Fly's kerning toolkit has a function for this search. Give it the package, a list of masters and a threshold, and it gives back the pairs whose value is closer to zero than the threshold:

```python
import fly.ap.core.scripting as scripting
import fly.ap.kerning.edit.model as kerning_edit

package = scripting.current_package()
found = kerning_edit.small_pairs(package, ["Light", "Regular", "Bold"], 10)
for master in found:
    for first, second, value in found[master]:
        print(f"{master:<9}{first:<8}{second:<12}{value:>4.0f}")
```

`found` is a dictionary with a master's name as the key and a list of rows under it. Each row is two names and a value. The rows come sorted by size, smallest first, with the names to settle ties, which is the tuple key you wrote yesterday.

```text
Light    X       @R_O2          7
Light    t       quoteright     8
Regular  @L_A    @R_O2         -7
Regular  @L_A    Q             -7
Regular  @L_O    @R_A2         -7
Regular  @L_W    @R_uacute     -7
Regular  @L_W    u             -7
Regular  Q       @R_A2         -7
Regular  R       V             -8
Bold     R       V             -9
```

"Closer to zero" is strict: a pair of 10 or −10 is not on the list. The Regular has two of those, `P` before `a` and before the `á` family, and they stay.

This is a dry run in the plainest sense. The function reads and reports, and the font is as it was.

## Step 2: The list is not the plan

The same toolkit has `remove_run`, which would take these ten pairs out in what should be one Undo step. I'm not going to call it, and here's why.

Mira reads the first line and stops. `X` before the `O` family has 7 units in the Light. She looks the pair up with `pair_value.py`:

```text
X O
  Light        7   through a class
  Regular    -23   through a class
  Bold       -41   through a class
```

It runs from +7 through −23 to −41. The Light's 7 is one end of a pair that does real work in the other two weights. Take it out of the Light and the pair exists in two masters and is missing from the third. Chapter 73's first exercise called that a hazard, and it is one: a weight between the Light and the Regular is made by mixing the two, and a missing pair counts as 0 in the mixing. For this pair the result would hardly differ. But the kerning lists of the three masters would no longer hold the same pairs, and the next person to compare them would have to work out why.

So today's mistake is to take the search for the decision. `small_pairs` answers "which values are small in this master?" The question for the font is "which pairs are small in every master where they exist?" Only those are too small to matter.

Asking that takes a look sideways, at the same pair in the other masters:

```python
tables = {master: scripting.kerning_pairs(package, master) for master in ["Light", "Regular", "Bold"]}
values = [tables[master].get(("X", "@R_O2")) for master in tables]
print(values)
```

```text
[7.0, -23.0, -41.0]
```

The first line is a dictionary comprehension, as in chapter 37: it reads each master's kerning once and keeps the three dictionaries under their names. The second collects one pair's three values, with `None` where a master doesn't have it.

Now the test. A value is harmless if it's missing or small:

```python
def is_small(value):
    return value is None or abs(value) < 10


print(all([is_small(value) for value in values]))
```

```text
False
```

`all` is from chapter 44: true when every item in the list is true. For `X` before `O` only the first is, so the pair stays. For `R` before `V` the three values are `None`, −8 and −9, and all three pass.

The order inside `is_small` matters. `abs(None)` is a `TypeError`. Because `or` stops at the first true part, a missing value never reaches `abs`.

## Step 3: Remove with None

Chapter 73 showed how a pair is removed: an order with `None` for its value. The plan gives rows, and the rows become orders the same way as on Wednesday, a dictionary for each master:

```python
edits = {}
for master, first, second, value in drop:
    if master not in edits:
        edits[master] = {}
    edits[master][(first, second)] = None
```

All of them go to `write_kerning` in one batch, and so they make one Undo step.

## The whole script

```python
#FLM: Drop Tiny Pairs
# Lists kerning pairs smaller than THRESHOLD. A pair is removed only if it is
# small or missing in every master. With DRY_RUN = True it only prints.
import fly.ap.core.scripting as scripting
import fly.ap.kerning.batch as kerning_batch
import fly.ap.kerning.edit.model as kerning_edit
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"

MASTERS = ["Light", "Regular", "Bold"]
THRESHOLD = 10
DRY_RUN = True


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes


def is_small(value):
    return value is None or abs(value) < THRESHOLD


def elsewhere(tables, master, first, second):
    parts = []
    for other in MASTERS:
        value = tables[other].get((first, second))
        if other != master and value is not None:
            parts.append(f"{other} {value:.0f}")
    return ", ".join(parts)


def plan(package):
    tables = {master: scripting.kerning_pairs(package, master) for master in MASTERS}
    found = kerning_edit.small_pairs(package, MASTERS, THRESHOLD)
    drop = []
    keep = []
    for master in MASTERS:
        for first, second, value in found[master]:
            values = [tables[other].get((first, second)) for other in MASTERS]
            row = (master, first, second, value)
            if all([is_small(other) for other in values]):
                drop.append(row)
            else:
                keep.append(row + (elsewhere(tables, master, first, second),))
    return drop, keep


def main():
    if fl.CurrentFont() is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    drop, keep = plan(package)
    for master, first, second, value, why in keep:
        print(f"keep  {master:<9}{first:<8}{second:<12}{value:>4.0f}   {why}")
    for master, first, second, value in drop:
        print(f"drop  {master:<9}{first:<8}{second:<12}{value:>4.0f}")
    print(f"{len(keep) + len(drop)} small pairs found, {len(drop)} to remove.")
    if DRY_RUN or not drop:
        return
    if not ask(f"Remove {len(drop)} kerning pairs?"):
        return

    edits = {}
    for master, first, second, value in drop:
        if master not in edits:
            edits[master] = {}
        edits[master][(first, second)] = None
    kerning_batch.write_kerning(package, edits, "Drop tiny pairs")
    drop, keep = plan(package)
    print(f"Done. {len(drop)} to remove.")


main()
```

Save it as `drop_tiny_pairs.py` and run it as it stands:

```text
keep  Light    X       @R_O2          7   Regular -23, Bold -41
keep  Light    t       quoteright     8   Regular 14, Bold 15
keep  Regular  @L_A    @R_O2         -7   Light -32, Bold -32
keep  Regular  @L_A    Q             -7   Light -24, Bold -32
keep  Regular  @L_O    @R_A2         -7   Light -26, Bold -26
keep  Regular  Q       @R_A2         -7   Light -24, Bold -32
drop  Regular  @L_W    @R_uacute     -7
drop  Regular  @L_W    u             -7
drop  Regular  R       V             -8
drop  Bold     R       V             -9
10 small pairs found, 4 to remove.
```

Ten were found, and six of them have a bigger relative in another master. Four lines may go: three pairs, one of which lives in two masters.

Read the four before you go on. `W` before `u` at −7 in the Regular only, and the same from the class of `W` to the class of `ú`. `R` before `V` at −8 and −9. Mira sets `Wu` and `RV` with kerning on and off and can't tell which is which.

Then change `DRY_RUN` to `False`, run again, and click Yes:

```text
Done. 0 to remove.
```

The Regular now has 104 pairs and the Bold 102. One Undo should bring the four back. I haven't seen it in FontLab 9.

Notes on the listing.

`DRY_RUN` is the switch from chapter 31. A script that deletes should ship with the switch on. The person who turns it off has read the list at least once.

`elsewhere` builds the reason for a kept line: the values in the other masters. It's there for the reader of the report. A line that says only "keep" makes you look the pair up, and with the other values printed you don't have to.

`row + (elsewhere(...),)` joins two tuples. The comma inside the second pair of brackets is what makes it a tuple of one. Without it, the brackets would be ordinary brackets around a string, and adding a string to a tuple is a `TypeError`.

`plan` returns two lists, as `plan` did in chapter 62. The last lines of `main` run it again after the write and count what's left, so "Done" is followed by a number that was measured after the change.

## Two cautions

The rule "small in every master" is safe for Plum. It isn't the whole of the matter in every font.

First, a small pair can be an exception. Suppose a class pair says −60, and one member of the class has its own pair of −5 because for that glyph the −60 was far too much. The −5 is small. Remove it and that glyph gets the class's −60, which nobody wanted. None of today's four is such a pair: `R` belongs to no class, and the two `W` pairs are class pairs themselves. In a font with more exceptions, look each dropped pair up with `pair_value.py` before and after. A value that went from small to large is one of these.

Second, the threshold is a judgement. Ten units is 1 per cent of the em. For a text face used at 9 to 12 points that's below what the eye resolves. For a display face set at 200 points, ten units is 2 points, and somebody put them there on purpose. Change `THRESHOLD` to suit the design.

## What the kept lines say

The six kept lines are worth a second look, and Mira gives them one.

Four of them are the same story. The `A` family before the `O` family, the `A` family before `Q`, and both the other way round: −7 in the Regular, and between −24 and −32 in the Light and the Bold. A middle weight with a quarter of the kerning of its neighbors isn't a design. Someone stopped halfway. She writes "AO, OA, AQ, QA: Regular, finish" on her list, under `L T` and `T w` from yesterday.

The script was looking for pairs to delete and found four that want to be bigger.

## What you learned

`kerning_edit.small_pairs(package, masters, threshold)` lists, for each master, the pairs whose value is closer to zero than the threshold. A pair that's small in one master may be large in the next, so collect its values across the masters with `get`, test for `None` before calling `abs`, and test them together with `all`. A script that deletes starts with `DRY_RUN = True` and prints what it would keep, and why, beside what it would drop. Before removing a small pair that belongs to a single glyph, check that a class pair doesn't take its place.

## Try it yourself

1. Set `DRY_RUN = True` again and `THRESHOLD = 12`. The plan should find sixteen small pairs. How many may go now, and which two are new on the drop list? Don't remove them: put the threshold back to 10 when you've looked.
2. Change `is_small` so that a missing value doesn't count as small. Which of the four pairs would still be dropped? Is that a better rule or a worse one for a font with three masters?
3. Write the four orders for Mira's note, with −20 as a first guess for each, and put them into `EDITS` in `set_pair.py`. Read the plan, and don't click Yes: the values want her eye first.

## Next

Chapter 72 added glyphs to classes. What about the other direction: a class that lists a glyph the font no longer has, or a pair that names a class nobody made? Chapter 76 looks for kerning that points at nothing.
