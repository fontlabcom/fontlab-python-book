---
this_file: src_docs/md/part4-space/067-find-the-odd-one.md
---

# 67. Find the odd one out

Tuesday of week thirteen. Yesterday's price list had a fault nobody had seen in years: one sign whose width didn't match its neighbors'. Mira wonders aloud how many more of those Plum is carrying. On Thursday she left herself a note, "Bold right side: wait", because the Bold's models were themselves in doubt. If the `n` is wrong, there's no use copying it.

So today's question is put differently. It isn't "does this letter match its model?" It's "which letter in this group doesn't look like the rest of the group?" Nobody has to be the model. The group votes.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The helper `tell` from chapter 39. The scripts below write it out again, so each one runs by itself.

Today's script reads and prints. It changes nothing. I couldn't run it in FontLab 9; the numbers come from Plum's source file, with the changes of chapters 62 and 63 worked in. If you did the exercises of those chapters, a few of your lines will differ, and I'll say where.

## Step 1: A group and its numbers

Start with six capitals whose right side is a straight stem. Read their right sidebearings in the Bold:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

font = fl.CurrentFont()
names = ["H", "I", "J", "M", "N", "U"]
values = [pGlyph(font, font[name]).getRSB("Bold") for name in names]
print(values)
```

```text
[40, 40, -24, 52, 42, 36]
```

You can see the odd one. Five numbers live near 40 and one is far below zero. (If you gave the Bold `H` 60 a side in chapter 62, your first number is 60, and you have two odd ones.)

You can see it at a glance with six numbers on one line. The script has to see it in nine groups and three masters without you, so it needs a rule. The rule has two parts: what's usual for the group, and how far from usual is too far.

## Step 2: The average, and why it lets you down

The first idea everyone has for "usual" is the average: add them up and divide by how many there are.

```python
usual = sum(values) / len(values)
print(usual)
```

```text
31.0
```

`sum` adds up a list, as it did in chapter 37. Now say that a letter is odd when it's more than 8 units from the usual value, in either direction. `abs` from chapter 36 takes the direction away:

```python
for name, value in zip(names, values):
    if abs(value - usual) > 8:
        print(name, value)
```

```text
H 40
I 40
J -24
M 52
N 42
```

Five odd ones out of six. That's this chapter's mistake, and there's no error message to announce it. The script ran, and what it says is nonsense: when nearly everybody is odd, the yardstick is.

Look at what happened. The `J` is so far off that it dragged the average down to 31, a value no letter in the group has or is near. Measured from there, the honest letters look wrong. The average asks every number for its opinion and weighs the loudest one most. For finding a fault, that's the wrong way round: the faulty number is the one you least want to have a say.

## Step 3: The one in the middle

There's a steadier kind of usual. Put the numbers in order and take the one in the middle:

```python
ordered = sorted(values)
print(ordered)
print(ordered[len(ordered) // 2])
```

```text
[-24, 36, 40, 40, 42, 52]
40
```

`sorted` you've had since chapter 10, and `//` halves the length without leaving the whole numbers. Six things halve to 3, and position 3, counting from 0, holds 40.

The `J` is still in the list. But it sits at the far end, and the far end has no say about the middle. It could be −24 or −2,400 and the middle would still be 40. Statisticians call this value the median. I'll call it the middle one.

With an even count there are two numbers in the middle, here both 40, and the line takes the upper of the two. A statistician would take the point halfway between them. For this job a value that some letter really has is the better answer, so the line stays as it is.

Wrap it up and try again:

```python
def middle(values):
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


usual = middle(values)
for name, value in zip(names, values):
    if abs(value - usual) > 8:
        print(name, value, f"{value - usual:+}")
```

```text
J -24 -64
M 52 +12
```

Two, and both deserve a look. The `J` is 64 units short. The `M` has 12 more than its neighbors, which may be a decision and may be a leftover. The script can't tell you which. It can tell you where to look.

## Step 4: How far is too far

The 8 in that test is a choice, and it's yours to make. Call it the tolerance and try three values on the whole font, all groups and masters:

| Tolerance | Letters reported |
| --- | --- |
| 4 | 19 |
| 6 | 11 |
| 8 | 6 |

At 4 you get 19 lines, and most of them are things a designer did on purpose: the Light `N`, 6 units less than the `H`, because its diagonal lets light in. At 8 you get six, and you can look at six before lunch. There's no right value. Start high, deal with what you find, and lower it when the list is empty and you still have appetite.

Since it's a choice, it goes at the top of the script, in capitals, with the other things you might change.

## Step 5: Groups as data

Each group needs three things: a label for the report, a side, and the names. That's a tuple, and the groups together are a list of tuples, as the rows of chapter 35 were:

```python
GROUPS = [
    ("cap stems", "left", "BDEFHIKLMNPRU"),
    ("cap rounds", "left", "CGOQ"),
    ("cap stems", "right", "HIJMNU"),
]

for label, side, names in GROUPS:
    print(label, side, list(names))
```

```text
cap stems left ['B', 'D', 'E', 'F', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'R', 'U']
cap rounds left ['C', 'G', 'O', 'Q']
cap stems right ['H', 'I', 'J', 'M', 'N', 'U']
```

A small saving is at work here. The names are single letters, so I wrote each group as one string, and `list` cut it into its characters. A string is a row of characters, and a `for` loop walks along it one at a time, as it did with a word in chapter 11; `list` collects what such a walk would meet. It works only while every glyph name is one character long. The day you want `germandbls` in a group, that group becomes a proper list with quotes and commas, and the rest of the script won't notice the difference.

The families of chapter 64 said "these follow that one". These groups say less: "these belong together". That's why a dictionary with a model as its key was right there and a plain list is right here.

## The whole script

```python
#FLM: Sidebearing Outliers
# Reports letters whose sidebearing is far from the middle value of their group.
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box
from fly.tr.proxy.fl.objects.glyph import pGlyph

TITLE = "Halfmoon"

MASTERS = ["Light", "Regular", "Bold"]
TOLERANCE = 8
GROUPS = [
    ("cap stems", "left", "BDEFHIKLMNPRU"),
    ("cap rounds", "left", "CGOQ"),
    ("cap stems", "right", "HIJMNU"),
    ("cap rounds", "right", "DOQ"),
    ("small stems", "left", "bhklmnpr"),
    ("small rounds", "left", "cdegoq"),
    ("small stems", "right", "ahmn"),
    ("small l", "right", "dglqu"),
    ("small rounds", "right", "bop"),
]


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def middle(values):
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def side_value(font, name, side, master):
    rich = pGlyph(font, font[name])
    return rich.getLSB(master) if side == "left" else rich.getRSB(master)


def odd_ones(font, master, side, names):
    values = [side_value(font, name, side, master) for name in names]
    usual = middle(values)
    found = []
    for name, value in zip(names, values):
        if abs(value - usual) > TOLERANCE:
            found.append((name, value, usual))
    return found


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    count = 0
    for master in MASTERS:
        for label, side, names in GROUPS:
            names = [name for name in names if font[name] is not None]
            if len(names) < 3:
                print(f"{label} {side}: too few letters to compare.")
                continue
            for name, value, usual in odd_ones(font, master, side, names):
                count += 1
                print(f"{master:<9}{label:<13}{side:<6}{name:<3}{value:>4}   usual {usual:>3}  ({value - usual:+})")
    print(f"{count} to look at, tolerance {TOLERANCE}.")


main()
```

Save it as `sb_outliers.py`. On the practice font it prints:

```text
Light    cap stems    left  U    78   usual  88  (-10)
Bold     cap stems    left  L    66   usual  56  (+10)
Bold     cap stems    right J   -24   usual  40  (-64)
Bold     cap stems    right M    52   usual  40  (+12)
Bold     cap rounds   right D    17   usual   0  (+17)
Bold     small stems  right a    41   usual  32  (+9)
6 to look at, tolerance 8.
```

Three things in the script are worth a second look.

`side_value` picks the getter with the short `if` of chapter 37: one value if the side is `"left"`, the other if it isn't. Anything that isn't `"left"` counts as right, including a typing slip like `"rihgt"`. In a list of nine groups that you can read at a glance I've let that stand.

The line that filters `names` keeps the script alive in a font that lacks a letter, and the test under it refuses to judge a group of fewer than three. Two numbers have no middle worth the name: whichever of the two is the larger gets called usual, and the other one gets the blame.

`continue` is the word from chapter 44. It ends this turn of the inner loop and goes on to the next group.

## Reading the report

Six lines, and the report has done what a report can do. The rest is looking.

**Bold `J`, −24.** A fault. The Regular `J` has 68 on its right and the Light has 80. In the Bold the stem grew fat and the width stayed at 239, so the black hangs 24 units out of its own box and into the next letter. This is the odd one of the chapter's title.

**Bold `D`, +17.** Read this one twice, because the report has it backwards. The usual value for the Bold round capitals is 0: the `O` has −6 and the `Q` has 0. A round letter with nothing on its right is the Bold's trouble again. The `D` with its 17 is the nearest of the three to healthy. The group voted, and the group was wrong.

That's the limit of the method and you should know it by heart. The middle one protects you from one bad number among good ones. It can't protect you when most of a group has gone the same wrong way, because then the wrong way is the usual way. A check like this finds letters that differ. Whether the different one is the sick one or the only well one takes a person.

**Bold `a`, +9, `M`, +12 and `L`, +10, Light `U`, −10.** Mira opens each in the Glyph window. The `a` and the `M` she leaves: the Bold `a` has a tail that wants the room. The `L` she can't explain, and the `U` neither. Both go on her list with a question mark.

Then she mends the `J` with a tool she already has. In `set_sb.py` from chapter 62 she sets:

```python
GLYPH = "J"
MASTER = "Bold"
LEFT = None
RIGHT = 40
```

The width goes from 239 to 303 and nothing moves, since the right side is the width's business alone. The script's `Borrowed by:` line names `IJ`, which borrows the `J` as `ij` borrowed the `j`. Its width will want the same 64 units. She writes "IJ, Bold" under "ij, Bold" on the list.

One fault found and mended, two questions, and one whole group, the Bold rounds, shown to be wrong together. That last one isn't a job for a tolerance. It's a job for tomorrow.

## What you learned

To find the odd one in a group you need a usual value and a tolerance, and `abs` measures the distance between them without direction. The average is a poor usual value, because one wild number drags it away; the middle of the sorted list stays put, and `sorted(values)[len(values) // 2]` finds it. A script can run without any error and still report nonsense, and "nearly everything is flagged" is the sign. The method finds what differs from the group, so it says nothing when a whole group is wrong.

## Try it yourself

1. Set `TOLERANCE = 6` and run the script. You should get 11 lines. Two of the new ones are the Regular `O` and `Q` on the left, both 36 against a usual 44. Print the four values of that group and say why "usual 44" is an accident of where the middle fell. What would you change in the group, and not in `middle`, to make the report fair?
2. Python has the statisticians' median ready-made: `import statistics`, then `statistics.median(values)`. Put it into `middle` and run the script at tolerance 8 again. The Bold round capitals have three members, so nothing changes there. For an even count it returns the point halfway between the two middle values, as a float, so 61 can come back as 61.0 or as a number ending in .5. Which groups have an even count, and does any line of the report change?
3. Add a group for the diagonals, `("diagonals", "right", "AVWXYvwxy")`, and run it. The list gets long. Diagonals don't share a sidebearing the way stems do. Take the group out again, and write one sentence in a comment above `GROUPS` saying what a letter must have in common with the others before it may join one.

## Next

Every count this week has ended with the same note on Mira's list: the whole Bold is tight on the right. Chapter 68 stops mending it letter by letter and opens up all of it at once, by adding to every right sidebearing with one script.
