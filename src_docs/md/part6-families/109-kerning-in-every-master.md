---
this_file: src_docs/md/part6-families/109-kerning-in-every-master.md
---

# 109. Kerning in every master

Thursday of week twenty-one. The Latin dictionary sent a page of test words, and `ae` turns up after capitals more than anyone expected: Tae, Vae, Kae. Mira kerned `T ae` and `V ae` on Tuesday, in the Regular. Ines, checking the bold headwords on Wednesday, kerned `K ae`, in the Bold.

Neither told the other. So the font now has two pairs that exist in one master, and a third that exists in another, and chapter 80's audit, which was clean in week fifteen, isn't any more.

A pair that's missing in a master isn't an error to FontLab. It's a pair with no kerning. In a font between two masters, it's worse: chapter 106's sum has a number at one end and nothing at the other.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- Chapter 73's way of writing pairs, and chapter 76's sets.

I couldn't run the code in FontLab 9. I ran the script on the kerning this book has built up since chapter 69, with Fly's own planning function doing the planning, and the output below comes from there.

## Step 1: Do what they did

Three pairs, two masters, one order, in chapter 73's form:

```python
import fly.ap.core.scripting as scripting
import fly.ap.kerning.batch as kerning_batch

package = scripting.current_package()
edits = {
    "Regular": {("T", "ae"): -48, ("V", "ae"): -36},
    "Bold": {("K", "ae"): -20},
}
kerning_batch.write_kerning(package, edits, "Kern ae after capitals")
```

`ae` is in no kerning class, so these are plain pairs between two glyphs.

## Step 2: The mistake

Which pairs does the Bold lack? Chapter 76 gave you the tool. A dictionary's keys make a set, and one set minus another is what the first has and the second hasn't:

```python
regular = scripting.kerning_pairs(package, "Regular")
bold = scripting.kerning_pairs(package, "Bold")
print(sorted(set(regular) - set(bold)))
```

```text
[('T', 'ae'), ('V', 'ae')]
```

Two pairs. Copy them to the Bold and the job looks finished.

It isn't, and the line can't tell you so. `a - b` answers one question: what does `a` have that `b` lacks? Ines's `K ae` is in the Bold and not in the Regular. Seen from the Regular it doesn't exist. Subtraction has a direction.

```python
print(sorted(set(bold) - set(regular)))
```

```text
[('K', 'ae')]
```

With two masters you could remember to ask both ways. With three you'd ask six times, and with the nine weights the client wants, seventy-two. Ask one question instead: which pairs exist anywhere, and for each, where is it missing?

## Step 3: Every pair, every master

Chapter 76 built the set of all pairs with `|`, which joins two sets. Do that, then walk it:

```python
def gaps(tables):
    everywhere = set()
    for master in tables:
        everywhere = everywhere | set(tables[master])
    rows = []
    for pair in sorted(everywhere):
        absent = [master for master in tables if pair not in tables[master]]
        if absent:
            rows.append((pair, absent))
    return rows
```

`tables` is a dictionary from master name to that master's pairs, as in chapter 75. Each row is a pair and the list of masters that lack it. A pair that's everywhere gets an empty list and isn't a row.

```python
masters = ["Light", "Regular", "Bold"]
tables = {m: scripting.kerning_pairs(package, m) for m in masters}
for pair, absent in gaps(tables):
    print(pair, absent)
```

```text
('K', 'ae') ['Light', 'Regular']
('T', 'ae') ['Light', 'Bold']
('V', 'ae') ['Light', 'Bold']
```

All three, and each says where it's missing. The direction is gone, because no master was the one doing the asking.

## Step 4: What value goes in?

Finding a gap is counting. Filling it means inventing a number, and that needs more care.

The plain answer: take the Regular's value. But chapter 79 turned every pair in the Bold down to 85 percent, because the Bold's letters sit closer. A new pair copied at full strength would be the one pair in the Bold that missed that decision.

Fly's copying function takes a percentage for that reason. `copy_plan` works out the edits without making them:

```python
import fly.ap.kerning.edit.model as kerning_edit

plan = kerning_edit.copy_plan(tables["Regular"], tables["Bold"], "missing", 85)
print(plan)
```

```text
{('T', 'ae'): -41, ('V', 'ae'): -31}
```

The word `"missing"` is the mode: add what the target lacks and leave everything else alone. There are two more. `"matching"` overwrites pairs both masters have and adds none. `"replace"` makes the target a copy of the source, and that deletes pairs the source doesn't have. Under `"replace"`, Ines's `K ae` would be gone from the Bold. Today's script never says that word.

85 percent of −48 is −40.8, and the plan says −41. Fly rounds to whole units, as it did in chapter 79.

Now the caution. I checked how well one master predicts another, on the 102 pairs that all three already have. The Light's value is within 5 units of the Regular's for 41 of them, and more than 20 units away for 12. The Bold, against 85 percent of the Regular, does no better: 34 close, 19 far. Kerning doesn't scale the way an anchor's position did in chapter 105. `T a` is −86 in the Light and −87 in the Bold, with −80 between them.

Why not? An anchor sits on the drawing, so when the drawing stretches, the anchor goes with it. A kerning value answers the white shapes that two letters make together, and those change with weight in their own way. A bolder `T` has a thicker bar and a thicker stem, and the gap under the bar doesn't shrink by any fixed share. Whoever kerned the three masters looked at each one.

So a copied value is a place to start. It beats a missing pair, since the font between masters now has two ends to work from. Somebody still has to look at "Tae" in the Bold.

## The whole script

```python
#FLM: Kerning Masters
# Finds kerning pairs that are in some masters and not in others, and
# copies the ones missing from the trusted master. Dry run by default.
import fly.ap.core.scripting as scripting
import fly.ap.kerning.edit.model as kerning_edit
import fly.ap.masters.inspect.model as masters_model
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


# Chapter 39's tell, written out again so this script runs by itself.
def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


TRUSTED = "Regular"
PERCENT = {"Light": 100, "Bold": 85}
DRY_RUN = True


def gaps(tables):
    everywhere = set()
    for master in tables:
        everywhere = everywhere | set(tables[master])
    rows = []
    for pair in sorted(everywhere):
        absent = [master for master in tables if pair not in tables[master]]
        if absent:
            rows.append((pair, absent))
    return rows


def show(pair, tables):
    cells = []
    for master in tables:
        value = tables[master].get(pair)
        cells.append("-" if value is None else f"{value:g}")
    first, second = pair
    return f"{first:<14}{second:<14}" + "".join([f"{c:>9}" for c in cells])


def main():
    if fl.CurrentFont() is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    masters = masters_model.master_order(package)
    tables = {m: scripting.kerning_pairs(package, m) for m in masters}
    rows = gaps(tables)
    print(f"{'':<28}" + "".join([f"{m:>9}" for m in masters]))
    for pair, absent in rows:
        print(show(pair, tables))
    print(f"Pairs not in every master: {len(rows)}.")
    orphans = [pair for pair, absent in rows if TRUSTED in absent]
    if orphans:
        print(f"Not in {TRUSTED}, and yours to settle: {len(orphans)}.")
    source = tables[TRUSTED]
    for master in masters:
        if master == TRUSTED:
            continue
        percent = PERCENT.get(master, 100)
        edits = kerning_edit.copy_plan(source, tables[master], "missing", percent)
        for pair in sorted(edits):
            print(f"{master}: {pair[0]} {pair[1]} would get {edits[pair]}")
        if DRY_RUN or not edits:
            continue
        counts = kerning_edit.copy_run(
            package, TRUSTED, [master], "missing", percent,
            undo_name=f"Copy missing kerning to {master}")
        print(f"{master}: added {counts[master][0]}.")
    if DRY_RUN:
        print("Dry run. Nothing was changed.")


main()
```

Save it as `kerning_masters.py` and run it:

```text
                                Light  Regular     Bold
K             ae                    -        -      -20
T             ae                    -      -48        -
V             ae                    -      -36        -
Pairs not in every master: 3.
Not in Regular, and yours to settle: 1.
Light: T ae would get -48
Light: V ae would get -36
Bold: T ae would get -41
Bold: V ae would get -31
Dry run. Nothing was changed.
```

Notes on the listing.

`show` prints a dash where a master has no pair. `tables[master].get(pair)` gives `None` for a missing key, and the test is `is None`, since a pair kerned at 0 would count as false and print as a dash too.

`PERCENT` records the house's decisions, one per master. `PERCENT.get(master, 100)` means a master nobody has an opinion about gets the value unchanged. When the Medium becomes a master of its own one day, the script still runs.

`copy_run` does the work `copy_plan` described, and gives back a dictionary from master to three counts: added, changed, removed. Under `"missing"` the last two are always 0, so the script prints the first. The script calls it once for each master because each has its own percentage. That's one Undo step per master, named for it.

The script reads the tables once, at the top, and never again. After a real run, `tables` is out of date: it still shows the gaps that were filled a moment ago. That's harmless here, since the script ends. It's the reason the check is a second run and not a line at the bottom. A script that reported on its own work from numbers it read beforehand would be telling you what it meant to do.

`K ae` is counted and left. It isn't in the trusted master, so the script has nothing to copy from, and it won't guess which way the truth runs. Mira might agree with Ines and kern it in the Regular. She might decide the Bold doesn't need it. The line `yours to settle` puts it in front of her.

## Break it on purpose

Set `DRY_RUN = False` and run. Two lines join the output:

```text
Light: added 2.
Bold: added 2.
```

Set it back and run again:

```text
                                Light  Regular     Bold
K             ae                    -        -      -20
Pairs not in every master: 1.
Not in Regular, and yours to settle: 1.
Dry run. Nothing was changed.
```

Now the breaking. Change `"missing"` to `"replace"` in the `copy_plan` line only, and leave the dry run on. The Scripting panel fills up. Here are the first lines, and one from the middle:

```text
Light: @L_A @R_C would get -13
Light: @L_A @R_O2 would get -24
Light: @L_A @R_U2 would get -20
```

```text
Bold: K ae would get None
```

I count 156 lines where a moment ago there were none: 72 in the Light and 84 in the Bold. `"replace"` makes the target a copy of the source, so every pair whose value differs is rewritten. The Light's `@L_A @R_C` is −32, a number somebody chose by looking at the Light, and the plan would flatten it to the Regular's −13. Chapter 79's work on the Bold would go the same way, turned to 85 percent of the Regular whatever it was before.

And one line among the 156 says `None`. That's how the plan says "delete". Ines's pair, the one the script said it would leave for Mira, would be removed by a script whose comment says it copies.

One word did all of that. The dry run is the reason you read about it in a panel and didn't find it in a proof a week later. Put `"missing"` back and run once more, to see the short output return.

A typing slip in the mode is caught sooner. By Fly's code, `"mising"` raises `ValueError: Unknown copy mode: mising`, and nothing is planned at all.

## Settle the last one

Mira sets `KAE` in the Bold and looks at it with and without Ines's pair. Ines was right. The arm of the `K` and the bowl of the `a` leave a hole, and it's there in the Regular too. So the pair belongs in the trusted master, and this is chapter 73's call once more:

```python
import fly.ap.core.scripting as scripting
import fly.ap.kerning.batch as kerning_batch

package = scripting.current_package()
edits = {"Regular": {("K", "ae"): -24}}
kerning_batch.write_kerning(package, edits, "Kern K ae")
```

Now the script has something to copy from. Run it, still as a dry run:

```text
                                Light  Regular     Bold
K             ae                    -      -24      -20
Pairs not in every master: 1.
Light: K ae would get -24
Dry run. Nothing was changed.
```

The `yours to settle` line has gone, because the pair is in the Regular now. The Bold isn't mentioned: it has a value, Ines's −20, and `"missing"` leaves a value alone. Set `DRY_RUN = False` and run, then set it back and run again:

```text
Light: added 1.
```

```text
                                Light  Regular     Bold
Pairs not in every master: 0.
Dry run. Nothing was changed.
```

An empty table under the header is what a finished job looks like here. Each master now holds 105 pairs, the same 105, and later chapters count on that number. If you skip this section, your Light and your Regular hold 104 and chapter 114 will say so.

## What you learned

Set subtraction has a direction, so to compare several masters you build the set of everything and ask of each item where it's missing. Finding a gap is certain and filling it is a guess, which is why the script reports every gap and fills only from the master you named. A copied kerning value should follow the decisions already made for its master, here 85 percent in the Bold, and it still needs an eye. A plan you can print before it runs will show you a wrong mode while it's still harmless.

## Try it yourself

1. Undo the last section's three steps with **Edit > Undo** until `K ae` is only in the Bold again. Then settle it the other way: take the pair out of the Bold, with `None` as the value in chapter 73's `write_kerning`. Run the script and count the pairs. Redo your way back to 105 before you go on.
2. Add a third column to each gap row: the master with the value of the largest size, the one furthest from 0. `max` with a key function does it, and chapter 36 has the pattern.
3. `gaps` tells you a pair is missing. Write `far_apart(tables, limit)` for pairs that every master has, where the largest and smallest values differ by more than `limit`. With a limit of 40, how many of your 105 pairs does it list, and would you call them faults?

## Next

The font can say where a Medium sits and has kerning at both ends of the road. Chapter 110 draws one: a new layer made from two masters, glyph by glyph.
