---
this_file: src_docs/md/part4-space/080-the-proof-comes-back-clean.md
---

# 80. The proof comes back clean

Friday of week fifteen. Nearly four weeks ago the publisher's typesetter wrote that the Bold looked gappy and she couldn't say where. Since then the Bold has had its right sides opened, its `J` mended, its figures lined up, its kerning sorted into classes, reviewed and turned down. A new set of fonts goes to her this afternoon.

Before it does, Mira wants one page that says the spacing is in order, and she wants to be able to make that page again in a month, after the next round of changes, without remembering what was on it. Each check on it exists already, somewhere in the last nineteen chapters. Today's script gathers them. It changes nothing in the font.

The new idea: a function can be put in a list like any other value.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The helper `tell` from chapter 39. The scripts below write it out again, so each one runs by itself.
- The font as chapter 79 left it.

I couldn't run the code in FontLab 9. The counts below were computed in plain Python from Plum's source file with this part's changes applied.

## Step 1: One check, one function

Every check in this part asked a question and collected the answers that were wrong. Give them all the same form: a function that takes the font and the kerning, and returns a list of problems as plain sentences. An empty list means the check passed.

Here is chapter 73's rule that kerning values are whole numbers, in that form:

```python
def check_whole(font, tables, classes):
    problems = []
    for master in tables:
        for (first, second), value in tables[master].items():
            if value != int(value):
                problems.append(f"{master}: {first} {second} is {value}")
    return problems
```

`tables` is the dictionary from chapter 76: master name to that master's pairs. `classes` is the same for the classes. This check doesn't use `font` or `classes` at all. It takes them anyway, so that every check can be called the same way, and you'll see in a moment why that's worth an unused parameter or two.

And here is chapter 61's word test:

```python
WORD = "minimum"
SPREAD_LIMIT = 16


def check_word(font, tables, classes):
    problems = []
    for master in MASTERS:
        gaps = [gap(font, a, b, master) for a, b in zip(WORD, WORD[1:])]
        if max(gaps) - min(gaps) > SPREAD_LIMIT:
            problems.append(f"{master}: gaps in {WORD} run from {min(gaps)} to {max(gaps)}")
    return problems
```

`gap` is the function from chapter 61: the right sidebearing of one letter plus the left sidebearing of the next.

## Step 2: A list of functions

You've passed a function to another function since chapter 36: `sorted(rows, key=by_width)` hands over `by_width` without brackets, and `sorted` calls it when it wants to. A function's name without brackets is the function itself, a value like a number or a string. So it can go in a list:

```python
CHECKS = [check_word, check_whole]

for check in CHECKS:
    problems = check(font, tables, classes)
    for line in problems:
        print(line)
```

Each time round the loop, `check` is a different function, and `check(font, tables, classes)` calls whichever one it is. That's why they all take the same three things. Adding a check to the audit is now one line in the list, and the loop never changes.

Run that with the two checks, and with the tables read as in chapter 76. It prints nothing at all. The Output panel stays empty.

## Step 3: What does silence mean?

Ines looks at the empty Output panel. "Is that good, or did it not run?"

It's a fair question and the script can't answer it. An audit that prints nothing when all is well prints the same nothing when `MASTERS` is empty, when the kerning failed to load, or when a check has a slip in it that makes it skip everything. This is the mistake to avoid in any checking script: silence that might mean "clean" and might mean "didn't look".

There are two cures and the audit needs both.

The first is to make each check say how much it looked at. A line that reads `whole values: 306 looked at, ok` can be believed. A line that reads `0 looked at, ok` tells you at once that something upstream is empty. So each check returns two things: a count and the list of problems. The full script below has every check in that form, with a `looked` counter beside the list.

The second is to see every check fail once. You did this in chapters 75 and 76 with made-up tables, and it's the same here, with the counting version of `check_whole`:

```python
fake = {"Light": {("A", "V"): -66.5, ("T", "o"): -40.0}}
print(check_whole(None, fake, None))
```

```text
(2, ['Light: A V is -66.5'])
```

Two values looked at, one problem, and it's the one you planted. The function never touches its first and third arguments, so `None` will do for them.

## The whole script

```python
#FLM: Spacing Audit
# Runs the spacing and kerning checks of Part 4 and prints one line for each.
# Changes nothing.
import fly.ap.core.scripting as scripting
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box
from fly.tr.proxy.fl.objects.glyph import pGlyph

TITLE = "Halfmoon"

MASTERS = ["Light", "Regular", "Bold"]
WORD = "minimum"
SPREAD_LIMIT = 16
SAME_WIDTH = ["zero", "one", "two", "three", "four", "five", "six", "seven",
              "eight", "nine", "dollar", "Euro", "sterling", "yen"]
DEEPEST = -120


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def gap(font, first, second, master):
    return pGlyph(font, font[first]).getRSB(master) + pGlyph(font, font[second]).getLSB(master)


def check_word(font, tables, classes):
    problems = []
    looked = 0
    for master in MASTERS:
        gaps = [gap(font, a, b, master) for a, b in zip(WORD, WORD[1:])]
        looked = looked + len(gaps)
        if max(gaps) - min(gaps) > SPREAD_LIMIT:
            problems.append(f"{master}: gaps in {WORD} run from {min(gaps)} to {max(gaps)}")
    return looked, problems


def check_same_width(font, tables, classes):
    problems = []
    looked = 0
    for master in MASTERS:
        widths = [pGlyph(font, font[name]).getAdvance(master) for name in SAME_WIDTH]
        looked = looked + len(widths)
        if len(set(widths)) != 1:
            problems.append(f"{master}: figure widths are {sorted(set(widths))}")
    return looked, problems


def check_whole(font, tables, classes):
    problems = []
    looked = 0
    for master in tables:
        for (first, second), value in tables[master].items():
            looked = looked + 1
            if value != int(value):
                problems.append(f"{master}: {first} {second} is {value}")
    return looked, problems


def check_deep(font, tables, classes):
    problems = []
    looked = 0
    for master in tables:
        for (first, second), value in tables[master].items():
            looked = looked + 1
            if value < DEEPEST:
                problems.append(f"{master}: {first} {second} is {value:.0f}")
    return looked, problems


def check_names(font, tables, classes):
    have = {glyph.name for glyph in font.glyphs}
    problems = []
    looked = 0
    for master in tables:
        for pair in tables[master]:
            looked = looked + 1
            for side in pair:
                if side.startswith("@"):
                    if side[1:] not in classes[master]:
                        problems.append(f"{master}: no class {side}")
                elif side not in have:
                    problems.append(f"{master}: no glyph {side}")
    return looked, problems


def check_same_pairs(font, tables, classes):
    everything = set()
    for master in tables:
        everything = everything | set(tables[master])
    problems = []
    for first, second in sorted(everything):
        missing = [master for master in tables if (first, second) not in tables[master]]
        if missing:
            problems.append(f"{first} {second} is not in {', '.join(missing)}")
    return len(everything), problems


CHECKS = [
    ("word spacing", check_word),
    ("figure widths", check_same_width),
    ("whole values", check_whole),
    ("deepest pair", check_deep),
    ("names in pairs", check_names),
    ("same pairs", check_same_pairs),
]


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    tables = {master: scripting.kerning_pairs(package, master) for master in MASTERS}
    classes = {master: scripting.kerning_classes(package, master) for master in MASTERS}

    total = 0
    for label, check in CHECKS:
        looked, problems = check(font, tables, classes)
        total = total + len(problems)
        verdict = "ok"
        if problems:
            verdict = f"{len(problems)} problems"
        print(f"{label:<16}{looked:>4} looked at   {verdict}")
        for line in problems:
            print("   ", line)
    print(f"{len(CHECKS)} checks, {total} problems.")


main()
```

Save it as `spacing_audit.py`. On the font as chapter 79 left it, it should print:

```text
word spacing      18 looked at   ok
figure widths     42 looked at   ok
whole values     306 looked at   ok
deepest pair     306 looked at   ok
names in pairs   306 looked at   ok
same pairs       102 looked at   ok
6 checks, 0 problems.
```

Seven lines, and every one says how much stood behind its "ok": 18 gaps, 42 widths, 306 kerning values, 102 different pairs.

Notes on the listing.

`CHECKS` is a list of tuples, a label and a function, and the loop unpacks each as `for label, check in CHECKS`. The label is what a person reads. The function is what the script calls.

`CHECKS` stands after the functions it names. Python reads a file from the top, and a name must exist before a line can use it. Inside a function's body that doesn't matter until the function is called, which is why `main` can sit anywhere. In a line at the left margin it matters at once.

Every check loops over `tables` or `MASTERS` and counts as it goes. The count costs one line and it's what makes the "ok" worth reading.

`check_names` is chapter 76's orphan check, written to give sentences. `for side in pair` walks the two names of a pair, since a tuple can be looped over like a list.

`check_same_pairs` counts different pairs, not values, so its number is 102 where the others say 306.

The limits at the top are opinions, and they're Mira's. A spread of 16 in `minimum` is what she accepts: the Light and the Regular both come to 14, and the Bold to 8. −120 is deeper than any pair Plum has now. A limit belongs in a constant with a name, where the next person can find it and disagree.

## Break it on purpose

You've seen one check fail on a made-up table. See the audit fail on the font. Change `DEEPEST` to −110 and run it again:

```text
deepest pair     306 looked at   18 problems
    Light: quoteright @R_eacute is -112
    Light: quoteright @R_oacute is -112
```

and sixteen more lines like them, nine in the Light and nine in the Regular, then `6 checks, 18 problems.` All eighteen are the apostrophe before a round letter, at −112. The Bold has none, since yesterday took its deepest pairs to −105. Mira knows these pairs and wants them as they are, so the limit goes back to −120. That's an honest way to deal with a known exception: the limit is moved in plain sight, and the next pair that goes deeper will still be caught.

## What the audit doesn't say

Read the seven lines again and notice what they claim. The gaps in one word are even. Fourteen glyphs share a width. The kerning is tidy, consistent and within a limit. None of that says the font is well spaced. A font could pass every line and look dreadful, if the limits were met by values that are wrong together.

The audit says something narrower and still worth having: nothing has slipped since a person last looked. The looking was done by Mira over four weeks and by Tobias with a pencil. The script holds what they decided, so that a careless edit in week twenty shows up as a line that isn't "ok".

Mira pastes the seven lines into the mail that goes with the fonts.

The typesetter's answer comes on Monday. "Headings are fine now. The whole thing sits better, I can't say why." Ines reads it twice. She can say why, to the unit: the Bold's right sides are four fifths of the Regular's, and its kerning is 85 per cent of what it was.

## What you learned

A function's name without brackets is the function, and it can be stored in a list or a tuple and called later. Give a family of checks the same parameters and the same kind of result, and one loop can run them all. A check that reports nothing when it passes can't be told from a check that didn't run, so return how much was looked at and see every check fail once before you trust its "ok". An audit shows that nothing has slipped since a person judged the font, and it doesn't do the judging.

## Try it yourself

1. Add a check `check_strength` that reports a master whose kerning strength, as chapter 79 measured it, is more than 1.05 times the Regular's. It should look at three numbers. It should report the Light, at about 1.06. Is that a problem, or a limit to discuss with Mira?
2. Plant a fault in the font: give the Bold `sterling` ten more units of width with `set_sb.py` or by hand. Run the audit, read the line, then undo.
3. Chapter 64's follower report is missing from the audit. Write `check_followers` using the `LEFT` families: a problem is a follower whose left sidebearing differs from its model's by more than 3. Decide what "looked at" should count.

## Next

The letters are drawn and the space between them is set. Part 5 is about words: the names of glyphs, the names of fonts, and the text that scripts read and write. It starts with an export that complains about a glyph called `uni0041.alt2 copy`.
