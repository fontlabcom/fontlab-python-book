---
this_file: src_docs/md/part4-space/061-the-space-around.md
---

# 61. The space around a letter

Monday of week twelve. The Czech and Polish fonts went out on Friday, and the publisher's typesetter has written back already. The new letters are fine. The Bold isn't. "It looks gappy," she writes. "Chapter headings mostly. I can't tell you where, it's the whole line."

Mira sets a line of Bold and looks at it for a while. She agrees, and she can't say where either. Ines asks the question that starts this part of the book: "Can the script see it?"

It can. A script can't judge how a line looks, but it can measure the white between every two letters, and a line looks gappy when those whites aren't alike. Part 3 was about the black shapes. Part 4 is about the space between them, and this chapter measures it.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The helpers `box`, `tell` and `ask_text` from chapters 39 and 43. The scripts below write them out again, so each one runs by itself.

Nothing in this chapter changes the font. I couldn't run it in FontLab 9. The numbers come from Plum's source file.

## Step 1: Three numbers, in every master

You met the three numbers in chapter 35. A glyph stands in a box as wide as its advance width. The gap from the left edge of the box to the leftmost point of the shape is the left sidebearing, LSB for short. The gap on the other side is the right sidebearing, RSB.

In chapter 35 you asked for them like this, and got the numbers of whichever master was showing:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

font = fl.CurrentFont()
rich = pGlyph(font, font["n"])
print(rich.getLSB(), rich.getAdvance(), rich.getRSB())
```

```text
70 523 66
```

The typesetter's complaint is about the Bold, so you need to choose the master. Each of the three questions takes a master's name between its parentheses:

```python
for master in ["Light", "Regular", "Bold"]:
    print(master, rich.getLSB(master), rich.getAdvance(master), rich.getRSB(master))
```

```text
Light 84 499 80
Regular 70 523 66
Bold 56 523 32
```

Read the three rows before going on, since the whole chapter is in them. In the Light and the Regular, the `n` has a little more room on the left than on the right: 84 and 80, 70 and 66. That's usual. The left side of an `n` is a straight stem and the right side is the foot of an arch, and designers give them nearly the same space.

In the Bold the numbers are 56 and 32. The right side has little more than half of what the left has. And look at the middle column. The Bold `n` is 523 wide, the same as the Regular.

## Step 2: Check the sum

Three numbers that describe one box ought to add up. The width is the left sidebearing, plus the black part, plus the right sidebearing. `box` from chapter 43 gives the black part. Here it is again, so these lines run by themselves:

```python
def box(font, glyph, master="Regular"):
    nodes = pGlyph(font, glyph).nodes(master)
    if not nodes:
        return None
    xs = [node.x for node in nodes]
    ys = [node.y for node in nodes]
    return min(xs), min(ys), max(xs), max(ys)


left, bottom, right, top = box(font, font["n"], "Bold")
black = right - left
print(left, black, rich.getLSB("Bold") + black + rich.getRSB("Bold"))
```

```text
56.0 435.0 523.0
```

It adds up, and it tells you something else. The left sidebearing is the same number as the left edge of the box, 56. It has to be: a glyph's box starts at 0, so the distance from 0 to the shape is where the shape starts. The right sidebearing is what's left over on the other side.

The black part of the Bold `n` is 435 units wide. In the Regular it's 387. So the letter grew by 48 units and its box grew by nothing. The stems had to get fatter somewhere, and they got fatter into the sidebearings, more on the right than on the left.

Mira nods at this. The Bold was made in a hurry, years ago, for one book jacket. Somebody thickened the Regular and never went back to the widths.

## Step 3: The mistake

Here's a line that looks as if it does the same job with less typing. Chapter 11 used `glyph.width`, so:

```python
glyph = font["n"]
for master in ["Light", "Regular", "Bold"]:
    black = glyph.width - rich.getLSB(master) - rich.getRSB(master)
    print(master, black)
```

```text
Light 359.0
Regular 387.0
Bold 435.0
```

No error, and two right answers out of three. The Light `n` is 335 units of black, and this says 359.

`glyph.width` has no place for a master's name. It answers for the master that's showing in the Font window, which is the Regular here: 523. The loop took the Regular's width and subtracted the Light's sidebearings from it. For the Regular that's right. For the Bold it's right by luck, since the two widths happen to be equal. For the Light it's 24 units off, and nothing in the output says so.

The rule for the rest of this part: when a line names a master, every number on that line must come from that master. Use `rich.getAdvance(master)`, and keep `glyph.width` for quick looks at the master on screen.

## Step 4: The white between two letters

A reader never sees a sidebearing. What the eye sees between an `n` and an `i` is one white strip: the right sidebearing of the `n` and the left sidebearing of the `i`, side by side. So the gap between two letters is a sum of two numbers that belong to two different glyphs.

```python
def gap(font, first, second, master):
    return pGlyph(font, font[first]).getRSB(master) + pGlyph(font, font[second]).getLSB(master)


print(gap(font, "n", "i", "Regular"), gap(font, "n", "i", "Bold"))
```

```text
126 78
```

That's 66 and 60 in the Regular, 32 and 46 in the Bold.

Now a whole word. The classic one for testing spacing is `minimum`: seven letters, all upright strokes, so the gaps should come out nearly equal. To get every pair of neighbors, use `zip` from chapter 35 and a slice from chapter 10. `word[1:]` is the word without its first letter, and zipping a word with that pairs each letter with the next one:

```python
word = "minimum"
print(list(zip(word, word[1:])))
```

```text
[('m', 'i'), ('i', 'n'), ('n', 'i'), ('i', 'm'), ('m', 'u'), ('u', 'm')]
```

Seven letters, six gaps. `zip` stops when the shorter of its two lists runs out, so the last `m` has no partner and nothing goes wrong. Now measure each pair:

```python
for master in ["Light", "Regular", "Bold"]:
    gaps = [gap(font, a, b, master) for a, b in zip(word, word[1:])]
    print(master, gaps)
```

```text
Light [154, 158, 154, 158, 160, 168]
Regular [126, 130, 126, 130, 132, 140]
Bold [60, 80, 78, 80, 66, 92]
```

There it is. In the Light the six gaps run from 154 to 168. In the Regular, from 126 to 140. In both, the widest gap is 14 units more than the narrowest, on gaps of well over a hundred. No eye will catch that.

In the Bold they run from 60 to 92. The widest gap is half as big again as the narrowest, and the two sit a few letters apart in the same word. That's what "gappy" means, and now it has numbers.

## Step 5: One number for unevenness

Reading six numbers per master works for one word. To compare words you want one number, and the simplest is the difference between the widest and the narrowest gap. I'll call it the spread. `max` and `min` from chapter 36 give it:

```python
def spread(gaps):
    return max(gaps) - min(gaps)


print(spread([60, 80, 78, 80, 66, 92]))
```

```text
32
```

A spread of 14 on gaps of 130 is about a tenth. A spread of 32 on gaps of 76 is over four tenths. The spread on its own doesn't say that, so the script below prints the smallest gap next to it.

One caution about what the number means. A spread of 0 is not the goal. Round letters need less room than straight ones, since a curve pulls away from its neighbor at the top and the bottom, so a well-spaced `noon` has a narrower gap in the middle than at its ends. The spread is useful for words made of one kind of stroke, like `minimum`, and for comparing one master with another. Exercise 2 looks at this.

## Step 6: Which letters to blame

The gaps say where the line is uneven. To find out why, print the sidebearings of the letters in the word, each letter once. A set from chapter 25 drops the repeats, and `sorted` puts what's left in order:

```python
print(sorted(set("minimum")))
```

```text
['i', 'm', 'n', 'u']
```

For the Bold, the table for these four comes out like this:

```text
i     46   222    24
m     56   788    14
n     56   523    32
u     52   523    36
```

The left sidebearings are close: 46 for the `i`, which is a little tight, and 52 to 56 for the rest. The right sidebearings are 24, 14, 32 and 36. The `m` has 14 units on its right and 56 on its left. Every gap after an `m` is narrow, and every gap after a `u` is wide.

So the trouble is on the right sides, and the `m` is the worst of them. Mira writes it on her list. Chapter 62 starts to do something about it.

## The whole script

The script asks for a word and prints the gaps in each master, then the letters. It works for words in small letters whose glyphs are named like the letter itself, which is true of `a` to `z`. For anything else it says so and stops. Chapter 77 does better with names.

```python
#FLM: Sidebearing Report
# Asks for a word, prints the white between its letters in each master,
# then the sidebearings of each letter. Changes nothing.
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box, run_text_dialog
from fly.tr.proxy.fl.objects.glyph import pGlyph

TITLE = "Halfmoon"
MASTERS = ["Light", "Regular", "Bold"]


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask_text(label, start=""):
    return run_text_dialog(qt.QtGui, label, start, TITLE)


def gap(font, first, second, master):
    return pGlyph(font, font[first]).getRSB(master) + pGlyph(font, font[second]).getLSB(master)


def spread(gaps):
    return max(gaps) - min(gaps)


def gap_line(font, word, master):
    gaps = [gap(font, a, b, master) for a, b in zip(word, word[1:])]
    numbers = " ".join([f"{g:>4}" for g in gaps])
    return f"{master:<9}{numbers}   smallest {min(gaps)}, spread {spread(gaps)}"


def letter_lines(font, word, master):
    lines = []
    for letter in sorted(set(word)):
        rich = pGlyph(font, font[letter])
        lines.append(f"{letter:<4}{rich.getLSB(master):>5}{rich.getAdvance(master):>6}{rich.getRSB(master):>6}")
    return lines


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    word = ask_text("Word to measure, in small letters:")
    if not word or len(word) < 2:
        return
    missing = [letter for letter in sorted(set(word)) if font[letter] is None]
    if missing:
        tell(f"No glyph named: {' '.join(missing)}")
        return

    print(word)
    for master in MASTERS:
        print(gap_line(font, word, master))
    for master in MASTERS:
        print()
        print(f"{master}: left, width, right")
        for line in letter_lines(font, word, master):
            print(line)


main()
```

Run it and type `minimum`. The top of the output:

```text
minimum
Light     154  158  154  158  160  168   smallest 154, spread 14
Regular   126  130  126  130  132  140   smallest 126, spread 14
Bold       60   80   78   80   66   92   smallest 60, spread 32
```

Below it come three small tables, one for each master. The Bold one is the table from step 6.

`" ".join(...)` over a list of formatted numbers is a trick worth keeping. `f"{g:>4}"` makes each number four characters wide, pushed to the right, and `join` from chapter 25 puts one space between them. The columns line up whatever the numbers are.

Mira prints the three lines and pins them over her desk. Ines reads them and asks whether every word is that bad. Mira types `hobnob`.

```text
hobnob
Light     130  134  137  130  134   smallest 130, spread 7
Regular   104  108  108  104  108   smallest 104, spread 4
Bold       62   64   59   62   64   smallest 59, spread 5
```

The Bold is as even here as the other two. So the Bold isn't wrong everywhere. It's wrong in some letters, and a script can find out which.

## What you learned

Every glyph has an advance width and two sidebearings in each master, and `getLSB`, `getAdvance` and `getRSB` take the master's name. `glyph.width` belongs to the master on screen, so don't mix it with numbers from another master. The white between two letters is the right sidebearing of the first plus the left sidebearing of the second, and `zip(word, word[1:])` gives the neighbors in a word. The spread of the gaps is a rough measure of evenness, good for comparing masters and poor as a target.

## Try it yourself

1. Run the script on `nun` and on `mum`. Before you look, work out the Bold gaps for `mum` by hand from the table in step 6. Which of the two words is more even in the Bold, and which letter makes the difference?
2. Run it on `noon`. In the Regular the gaps are 104, 76 and 108. Is the middle gap a fault? Set the word in the Regular, look at it, and decide. Then write one sentence on why a script that tried to make all gaps equal would spoil the font.
3. Add a column to `letter_lines`: the width of the black part, which is the advance width minus both sidebearings. For the Bold `m` it should be 718. Then compare with the Regular `m`. How many units did the black grow by, and how much of that came out of the right sidebearing?

## Next

The Bold `m` has 14 units on its right and should have about as much as the `n`. Chapter 62 sets a sidebearing from a script, looks at what moves when you do that, and checks the result afterwards.
