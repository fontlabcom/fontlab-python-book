---
this_file: src_docs/md/part6-families/114-check-before-you-ship.md
---

# 114. Check before you ship

Thursday of week twenty-two. Oskar puts a sheet of paper on Mira's desk. It isn't the old sheet of chores. This one is headed "Quince, 2019" and it has four lines:

- A glyph in the Bold had one node too few. The in-between weights came out as scribble.
- The seven was narrower than the other figures. Price lists didn't line up.
- A kerning pair was missing in one master. The gap opened as the weight went up.
- We sent a corrected font with the old version number. The client kept using the old one.

"Everything on there went out of the door," he says. "Each one cost a week."

You've already written a script for most of those lines. Chapter 100 put five checks of a single font into one list, and Part 6 has taught you what goes wrong between masters. Today the two meet: one script, nine checks, run before every export.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, and `halfmoon.py`.
- `preflight.py` from chapter 100.
- The `exports` folder from chapters 111 and 112.

I couldn't run the code in FontLab 9. I ran the script in plain Python against a stand-in for the reader's font, with the kerning this book has made and the two export folders from this week.

## Step 1: Borrow the old checks

Chapter 100's five checks are good and you don't want a second copy of them. A copy is two things to mend when one changes. Since chapter 33 you've borrowed from `halfmoon.py` with `import`. `preflight.py` is a Python file too, and it has a list named `CHECKS`.

Python has to be able to find it. Move `preflight.py` out of the Scripts folder and into the folder where `halfmoon.py` lives. It'll leave FontLab's menu, and that's all right, because today's script does its job and more.

Then, in a new script:

```python
import preflight

print(len(preflight.CHECKS))
```

## Step 2: The mistake

Run those two lines:

```text
Glyph names   274 looked at   ok
Unicode       235 looked at   ok
Features       35 looked at   ok
Font Info       5 looked at   ok
Metrics         8 looked at   ok
5 checks, 0 problems, 0 did not run.
Version 1.001: ready for the hand tests.
5
```

You asked for a list and got a whole report, and then the list.

`import` doesn't fetch names from a file. It runs the file, top to bottom, and keeps whatever names exist at the end. For `halfmoon.py` you never saw the difference, since that file holds only `def` lines and constants, and running a `def` makes a function without calling it. But the last line of `preflight.py` is `main()`. Running the file runs the report.

Here it's a nuisance. In a script whose last line changes the font, it would be worse: importing the file would change the font.

Chapter 33 showed the cure in a side note and said you could leave it alone for now. Now you need it. Open `preflight.py` and change the last line from this:

```python
main()
```

to this:

```python
if __name__ == "__main__":
    main()
```

Python gives every file it runs a name, kept in `__name__`. A file that was imported gets its own name, `"preflight"`. The file you ran directly gets the name `"__main__"`. So the two lines say: call `main` if somebody ran this file, and not if somebody borrowed from it.

FontLab remembers a module once it's imported, as chapter 33 found, so the old `preflight` is still in its memory. For this one run, put chapter 33's reload under the import:

```python
import importlib

import preflight

importlib.reload(preflight)
print(len(preflight.CHECKS))
```

```text
5
```

One caution. I'm certain of how `__name__` works in Python. I haven't seen what name FontLab gives a script when you run it from the Scripting panel or the menu. If it isn't `"__main__"`, a guarded script run on its own would do nothing at all, silently. That's why today's script, which you run yourself, ends in a plain `main()`. Guard the files you import from. Leave the ones you run.

## Step 3: Four checks for the family

Each check keeps chapter 100's shape. It takes the font and the package, changes nothing, and returns a count of what it looked at and a list of sentences.

Oskar's first line is chapter 102. `masters_model.check_glyph` compares one glyph's contours, anchors and components across the masters:

```python
def check_masters(font, package):
    masters = masters_model.master_order(package)
    looked = 0
    problems = []
    for glyph in font.glyphs:
        fl_glyph = package.findName(glyph.name)
        signatures, ok, found = masters_model.check_glyph(fl_glyph, masters)
        if all([signatures[m] is None for m in signatures]):
            continue
        looked += 1
        if not ok:
            problems.append(f"{glyph.name}: {', '.join(found)} differ between masters")
    return looked, problems
```

The `continue` skips the glyphs FontLab builds itself, as chapter 102 did. Chapter 102 also printed where the difference was. A check gives one line a glyph, and `compat_check.py` is still there when you want the detail.

His second line is chapter 104, cut down to the ten figures. A set holds each width once, so a set with more than one member means the figures disagree:

```python
def check_figures(font, package):
    masters = masters_model.master_order(package)
    problems = []
    for master in masters:
        widths = set()
        for name in TABULAR:
            glyph = package.findName(name)
            widths.add(dict(masters_model.widths(glyph, masters))[master])
        if len(widths) > 1:
            text = " and ".join([f"{w:.0f}" for w in sorted(widths)])
            problems.append(f"{master}: figures are {text} wide")
    return len(TABULAR), problems
```

His third is chapter 109's `gaps`, returning sentences. The fourth is new, and it's the one Halfmoon paid most for. Chapter 111 named each export folder with the version at the end. So the disk already knows which versions have gone out:

```python
def check_new_version(font, package):
    info = package.info
    ending = f"-v{info.versionMajor}.{info.versionMinor:03d}"
    exports = Path(font.path).parent / "exports"
    problems = []
    if exports.exists():
        for folder in sorted(exports.iterdir()):
            if folder.name.endswith(ending) and list(folder.rglob("*.*")):
                problems.append(f"{folder.name} already holds files")
    return 1, problems
```

`list(folder.rglob("*.*"))` is every file under the folder with a dot in its name. An empty list counts as false, so an empty folder for this version is no problem. A folder with fonts in it is.

## The whole script

```python
#FLM: Ship Check
# Everything that went wrong last time, as checks: the five from
# preflight.py and four for the family. Read-only. Changes nothing.
from pathlib import Path

import fly.ap.core.scripting as scripting
import fly.ap.masters.inspect.model as masters_model
import halfmoon
import preflight
from fly import fl

TABULAR = ["zero", "one", "two", "three", "four",
           "five", "six", "seven", "eight", "nine"]


def check_masters(font, package):
    masters = masters_model.master_order(package)
    looked = 0
    problems = []
    for glyph in font.glyphs:
        fl_glyph = package.findName(glyph.name)
        signatures, ok, found = masters_model.check_glyph(fl_glyph, masters)
        if all([signatures[m] is None for m in signatures]):
            continue
        looked += 1
        if not ok:
            problems.append(f"{glyph.name}: {', '.join(found)} differ between masters")
    return looked, problems


def check_figures(font, package):
    masters = masters_model.master_order(package)
    problems = []
    for master in masters:
        widths = set()
        for name in TABULAR:
            glyph = package.findName(name)
            widths.add(dict(masters_model.widths(glyph, masters))[master])
        if len(widths) > 1:
            text = " and ".join([f"{w:.0f}" for w in sorted(widths)])
            problems.append(f"{master}: figures are {text} wide")
    return len(TABULAR), problems


def check_kerning(font, package):
    masters = masters_model.master_order(package)
    tables = {m: scripting.kerning_pairs(package, m) for m in masters}
    everywhere = set()
    for master in masters:
        everywhere = everywhere | set(tables[master])
    problems = []
    for first, second in sorted(everywhere):
        absent = [m for m in masters if (first, second) not in tables[m]]
        if absent:
            problems.append(f"{first} {second}: no pair in {', '.join(absent)}")
    return len(everywhere), problems


def check_new_version(font, package):
    info = package.info
    ending = f"-v{info.versionMajor}.{info.versionMinor:03d}"
    exports = Path(font.path).parent / "exports"
    problems = []
    if exports.exists():
        for folder in sorted(exports.iterdir()):
            if folder.name.endswith(ending) and list(folder.rglob("*.*")):
                problems.append(f"{folder.name} already holds files")
    return 1, problems


CHECKS = preflight.CHECKS + [
    ("Masters", check_masters),
    ("Figures", check_figures),
    ("Kerning", check_kerning),
    ("New version", check_new_version),
]


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    total = 0
    broken = 0
    for label, check in CHECKS:
        try:
            looked, problems = check(font, package)
        except Exception as problem:
            broken += 1
            print(f"{label:<13}DID NOT RUN: {type(problem).__name__}: {problem}")
            continue
        total += len(problems)
        verdict = f"{len(problems)} problems" if problems else "ok"
        print(f"{label:<13}{looked:>4} looked at   {verdict}")
        for line in problems:
            print("   ", line)
    print(f"{len(CHECKS)} checks, {total} problems, {broken} did not run.")
    print("Ready to export." if total == 0 and broken == 0 else "Not ready.")


main()
```

Save it as `ship_check.py` and run it:

```text
Glyph names   274 looked at   ok
Unicode       235 looked at   ok
Features       35 looked at   ok
Font Info       5 looked at   ok
Metrics         8 looked at   ok
Masters       201 looked at   ok
Figures        10 looked at   ok
Kerning       105 looked at   ok
New version     1 looked at   2 problems
    2026-12-07-v1.001 already holds files
    2026-12-08-v1.001 already holds files
9 checks, 2 problems, 0 did not run.
Not ready.
```

Your counts depend on what you kept from each chapter's exercises, and your folder names carry your own dates.

Eight checks pass, and the ninth has caught Halfmoon about to repeat the fourth line of Oskar's sheet. Version 1.001 went to the typesetter on Monday and to the publisher on Tuesday. Since then the font has been open on Mira's desk every day. She doesn't think she changed anything in it, and she can't show that she didn't. Anything exported today as 1.001 could be a different font under the same number, and nobody would know.

The mending is chapter 97's. Run `bump_version.py` for real, then run the check again:

```text
New version     1 looked at   ok
9 checks, 0 problems, 0 did not run.
Ready to export.
```

Notes on the listing.

`preflight.CHECKS + [...]` joins two lists into a new one. The five old checks come first, so the report reads from the single font outward to the family. `preflight.CHECKS` itself isn't changed.

`main` is chapter 100's loop, almost word for word, and that's the reward for giving every check one shape. The loop doesn't know there are nine, or which file each came from.

The "looked at" column matters as much as the verdict. Masters says 201, which is the 274 glyphs less the 73 that FontLab builds itself. Had it said 0, the `ok` beside it would mean nothing, because a check that examined nothing can't find a problem. Read the count before you believe the word. If a number drops sharply between one Thursday and the next, something upstream of the check has changed, and that's worth five minutes even when every line says `ok`.

The last check knows less than it seems to. It reads one folder, `exports`, beside the font file. A font that somebody exported to the desktop and sent by email left no folder there, and the check will pass. It proves that this version number hasn't been used in the place where Halfmoon keeps its exports. That's a narrower claim than "nobody has this version", and it holds only as long as everyone exports through chapter 111's script.

No check here repairs anything. A check that mends things as it goes is a script you can't run on a whim. This one changes nothing, so the answer to "should I run it?" is always yes.

## Break it on purpose

A check that has only ever said `ok` hasn't been tested. Give each new one a fault to find, on a saved font.

Open the Bold `e`, delete one node on a straight stretch, and in the Bold's kerning delete the pair `T` `ae`. Then set the Bold `seven` to a width of 480. Run:

```text
Masters       201 looked at   1 problems
    e: contours differ between masters
Figures        10 looked at   1 problems
    Bold: figures are 480 and 490 wide
Kerning       105 looked at   1 problems
    T ae: no pair in Bold
New version     1 looked at   ok
9 checks, 3 problems, 0 did not run.
Not ready.
```

Three faults in, three sentences out, and each says where to look. Those are the first three lines of the Quince sheet, caught on a Thursday afternoon and not by a client. Close the font without saving and open it again.

## What you learned

`import` runs the whole file, so a file you borrow from must not do its work at the top level, and `if __name__ == "__main__":` keeps a file's last line for the times it's run directly. Lists join with `+`, so one script can take another's list of checks and add its own. A check for a mistake that already happened once is the cheapest check to justify, and the names of last week's export folders are a record a script can read. Checks that change nothing can be run at any moment, and each one should be seen to fail before you trust it to pass.

## Try it yourself

1. Add the four signs from chapter 104 to a second list and check that they match the figures' width in each master.
2. Write `check_instances`, using chapter 107's `instance_records`: a problem for every instance whose weight lies outside the masters.
3. Oskar adds a fifth line to the sheet: "The Light had no copyright line." Which existing check already covers it, and how would you prove that without reading the code?

## Next

The font passes, and it has a new number. The client wants something no check can give: a sheet of paper with every glyph on it. Chapter 115 writes that sheet as a web page that uses the exported font.
