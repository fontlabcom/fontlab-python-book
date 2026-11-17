---
this_file: src_docs/md/part5-words/096-numbers-in-font-info.md
---

# 96. The numbers in Font Info

Monday of week nineteen. The publisher's web designer has a question before she builds the cookbook's site: will the ring on the Å in "Ångström's rye" be cut off in a tight heading? She has been bitten by another foundry's font, where every accented capital lost its top in one browser.

Oskar draws a box on the whiteboard, with a glyph in it. "A program doesn't look at your outlines to decide how tall a line is. It reads a few numbers from Font Info and believes them. If a glyph is taller than the numbers say, some programs cut it off at the edge of the box."

Today you read those numbers in every master, measure the tallest and lowest glyph, and compare. Then you set one number wrong on purpose, to see that the report notices.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The `tell` function from [chapter 39](../part2-a-toolbox/039-ask-the-user.md). The script below defines it again, so it runs by itself.

I couldn't run the code in FontLab 9. The Font Info values are the ones in Plum's source file. The glyph heights I computed from the same file, adding each component's shift to the outline it borrows. If you built accented capitals in Part 3, one of yours may tie with `Aring` for the tallest. The way the script asks a layer for its box is the way Fly's metrics panel asks.

## Step 1: Eight numbers, three systems

A font file carries the height of a line three times, for three families of programs. The names are historical and you don't need to love them:

- **typo**: ascender, descender and line gap. These are the ascender, descender and line gap you see in FontLab's Font Info.
- **hhea**: ascender, descender and line gap again, read by Apple's systems.
- **win**: an ascent and a descent, read by Windows. Many programs treat these two as the edges of the box and clip there.

That's eight fields. You know from chapter 95 what to do with a list of fields: put them in a table and let `getattr` read them. They belong to each master, so the reading visits every master and goes back, with `try` and `finally`:

```python
import fly.ap.core.scripting as scripting

FIELDS = {
    "openTypeOS2TypoAscender": "typo ascender",
    "openTypeOS2TypoDescender": "typo descender",
    "openTypeOS2TypoLineGap": "typo line gap",
    "openTypeHheaAscender": "hhea ascender",
    "openTypeHheaDescender": "hhea descender",
    "openTypeHheaLineGap": "hhea line gap",
    "openTypeOS2WinAscent": "win ascent",
    "openTypeOS2WinDescent": "win descent",
}


def read_numbers(package):
    numbers = {}
    original = package.master
    try:
        for master in package.masters:
            package.setMaster(master)
            numbers[master] = {key: getattr(package.info, key) for key in FIELDS}
    finally:
        package.setMaster(original)
    return numbers


package = scripting.current_package()
numbers = read_numbers(package)
for key, label in FIELDS.items():
    print(f"{label:<16}{numbers['Regular'][key]:>6.0f}")
```

```text
typo ascender      765
typo descender    -235
typo line gap      200
hhea ascender      965
hhea descender    -235
hhea line gap        0
win ascent         965
win descent        235
```

`numbers` is a dictionary of dictionaries: a master's name leads to that master's eight values. There's no `or ""` this time. These are numbers, and a number field that nobody set reads as 0, which is a value the report should show.

Look at the last line. The two descenders are −235 and the win descent is 235. Windows counts its descent downward, as a positive number. Keep that in mind for Step 3.

## Step 2: The tallest and the lowest glyph

In chapter 43 you found a glyph's box from its nodes, and a glyph built from components had none. The package's layers answer for the whole glyph, components included:

```python
from fly import fl

font = fl.CurrentFont()
layer = package.findName("Aring").findLayer("Regular")
box = layer.boundingBox
print(box.y(), box.y() + box.height())
```

```text
0.0 885.0
```

`box.y()` is the bottom edge and the height is added to get the top. The Å stands on the baseline and its ring ends at 885.

Now every glyph. Keep the height together with the name in a tuple, so the report can say which glyph it was:

```python
def extremes(package, font, master):
    low = None
    high = None
    for glyph in font.glyphs:
        layer = package.findName(glyph.name).findLayer(master)
        if layer is None or layer.isNull:
            continue
        box = layer.boundingBox
        if box.width() == 0 and box.height() == 0:
            continue
        bottom = box.y()
        top = box.y() + box.height()
        if low is None or bottom < low[0]:
            low = (bottom, glyph.name)
        if high is None or top > high[0]:
            high = (top, glyph.name)
    return low, high


print(extremes(package, font, "Regular"))
```

```text
((-235.0, 'bar'), (885.0, 'Aring'))
```

`low` and `high` start as `None`, because before the first glyph there's no lowest anything. `if low is None or bottom < low[0]` reads: take this glyph if it's the first, or if it's lower than the lowest so far. Empty glyphs, like the space and the fraction figures nobody has drawn yet, are skipped. Their box has no size and would pull both answers toward zero.

The lowest glyph is the vertical bar, at −235. The tallest is the Å.

## Step 3: The mistake

Room above is the win ascent minus the tallest top. Mira writes the room below the same way round:

```python
n = numbers["Regular"]
low, high = extremes(package, font, "Regular")
print("above", n["openTypeOS2WinAscent"] - high[0])
print("below", low[0] - n["openTypeOS2WinDescent"])
```

```text
above 80.0
below -470.0
```

Minus 470: the bar sticks out of the box by nearly half the font's height, in a font that has been sold for years. That can't be true, and the number is too large to be a drawing fault. When a result is absurd, suspect the sum before the font.

The bottom of the box is at −235. The field says 235, because Windows counts downward. The room below is the distance from −235 up to the glyph's bottom, which is `low[0] + n["openTypeOS2WinDescent"]`: −235 plus 235, zero. The bar touches the edge and doesn't cross it.

Signs are the classic trap of vertical metrics, and no error message will ever warn you. A descender is negative, a win descent is positive, and a script that mixes them prints a confident wrong number.

## Step 4: Do the three systems agree?

A line's height is ascender minus descender plus line gap. Work it out for the two systems that have all three numbers:

```python
typo = n["openTypeOS2TypoAscender"] - n["openTypeOS2TypoDescender"] + n["openTypeOS2TypoLineGap"]
hhea = n["openTypeHheaAscender"] - n["openTypeHheaDescender"] + n["openTypeHheaLineGap"]
print(typo, hhea)
```

```text
1200.0 1200.0
```

765 + 235 + 200 and 965 + 235 + 0. The two systems split the line differently and arrive at the same 1,200 units. If they didn't, the same text would have different line spacing on a Mac and in Windows, and somebody would spend a day blaming the layout.

## The whole script

```python
#FLM: Vertical Metrics
# For each master: the tallest and lowest glyph against the clip lines,
# and the line height by two systems. Changes nothing.
from fly import fl, qt
import fly.ap.core.scripting as scripting
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


FIELDS = {
    "openTypeOS2TypoAscender": "typo ascender",
    "openTypeOS2TypoDescender": "typo descender",
    "openTypeOS2TypoLineGap": "typo line gap",
    "openTypeHheaAscender": "hhea ascender",
    "openTypeHheaDescender": "hhea descender",
    "openTypeHheaLineGap": "hhea line gap",
    "openTypeOS2WinAscent": "win ascent",
    "openTypeOS2WinDescent": "win descent",
}


def extremes(package, font, master):
    low = None
    high = None
    for glyph in font.glyphs:
        layer = package.findName(glyph.name).findLayer(master)
        if layer is None or layer.isNull:
            continue
        box = layer.boundingBox
        if box.width() == 0 and box.height() == 0:
            continue
        bottom = box.y()
        top = box.y() + box.height()
        if low is None or bottom < low[0]:
            low = (bottom, glyph.name)
        if high is None or top > high[0]:
            high = (top, glyph.name)
    return low, high


def read_numbers(package):
    numbers = {}
    original = package.master
    try:
        for master in package.masters:
            package.setMaster(master)
            numbers[master] = {key: getattr(package.info, key) for key in FIELDS}
    finally:
        package.setMaster(original)
    return numbers


def report(master, n, low, high):
    problems = 0
    print(master)
    top_room = n["openTypeOS2WinAscent"] - high[0]
    bottom_room = low[0] + n["openTypeOS2WinDescent"]
    for label, found, room in [("tallest", high, top_room), ("lowest", low, bottom_room)]:
        note = f"room {room:.0f}" if room >= 0 else f"STICKS OUT by {-room:.0f}"
        print(f"  {label:<8}{found[1]:<12}{found[0]:>6.0f}   {note}")
        if room < 0:
            problems += 1
    typo = (n["openTypeOS2TypoAscender"] - n["openTypeOS2TypoDescender"]
            + n["openTypeOS2TypoLineGap"])
    hhea = (n["openTypeHheaAscender"] - n["openTypeHheaDescender"]
            + n["openTypeHheaLineGap"])
    note = "" if typo == hhea else "   <-- they differ"
    print(f"  line    typo {typo:.0f}, hhea {hhea:.0f}{note}")
    if typo != hhea:
        problems += 1
    return problems


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    numbers = read_numbers(package)
    problems = 0
    for master in package.masters:
        low, high = extremes(package, font, master)
        if high is None:
            print(f"{master}: no outlines")
            continue
        problems += report(master, numbers[master], low, high)
    for key, label in FIELDS.items():
        values = {numbers[master][key] for master in package.masters}
        if len(values) > 1:
            found = ", ".join(f"{m} {numbers[m][key]:.0f}" for m in package.masters)
            print(f"{label} is not the same in every master: {found}")
            problems += 1
    print(f"{problems} things to look at.")


main()
```

Save it as `vertical_metrics.py`. On Plum as shipped it should print:

```text
Light
  tallest Aring          875   room 90
  lowest  bar           -235   room 0
  line    typo 1200, hhea 1200
Regular
  tallest Aring          885   room 80
  lowest  bar           -235   room 0
  line    typo 1200, hhea 1200
Bold
  tallest Aring          896   room 69
  lowest  bar           -235   room 0
  line    typo 1200, hhea 1200
0 things to look at.
```

Mira sends the web designer one line: the ring has 69 units of room in the tightest weight, and nothing in the family sticks out.

Notes on the listing.

The last loop in `main` collects one field's values from all masters in a set. A set keeps each value once, so a set with more than one member means the masters disagree. That's exercise 3 of chapter 95, put to work. The weights of a family should share these eight numbers. If they don't, a line's spacing changes when a word in it goes bold.

The typo ascender is 765, and the Å is 885. That's no fault. The typo ascender describes where the lowercase ascenders end and helps set the line spacing. The win ascent is the number that has to clear the accents.

The room shrinks from 90 to 69 as the weight grows, because a bolder ring is a taller ring. The Bold is the master to watch.

## Set a number, and take it back

The report says zero. A check that has never found anything hasn't been tested, as chapter 93 argued about its checker. So give it something to find. Lower the Bold's win ascent to 880, below the ring:

```python
old = numbers["Bold"]["openTypeOS2WinAscent"]
changes = [("Bold", "openTypeOS2WinAscent", old, 880)]
result = scripting.write_font_info(package, changes, undo_name="Lower Bold win ascent")
print(result)
```

```text
{'changed': 1}
```

A change is a tuple of four things: the master, the field, the value you believe is there now, and the value you want. The writer compares the third with the font before it touches anything. If the font has moved on since you read it, the writer refuses with `changed since preview; refresh the tool.` and writes nothing. It also wants a name for the Undo step, as the feature writer did in chapter 88.

Run `vertical_metrics.py` again. The Bold now reads:

```text
Bold
  tallest Aring          896   STICKS OUT by 16
  lowest  bar           -235   room 0
  line    typo 1200, hhea 1200
win ascent is not the same in every master: Light 965, Regular 965, Bold 880
2 things to look at.
```

Both checks fired. Now choose **Edit > Undo**, once, and run the report a third time. It should say zero again. If it doesn't, write the number back the way you changed it, with 880 as the old value and 965 as the new.

## What the script can't tell you

Which programs clip, and where, differs from one to the next and changes over the years. Some use the win pair, some the hhea pair, and some use the typo set when a certain switch in the font is on. In Plum that switch is off. The report measures against the win pair because it's the oldest and strictest habit. In Plum the hhea ascender is the same 965, so the answer holds for both.

The script also can't say what the numbers should be. Raising the win ascent to make room for a taller accent moves every line of text that's ever set in the font. That's a decision for Oskar and Ines, made once, before the first release.

## What you learned

Font Info holds the height of a line three times, as the typo, hhea and win numbers, and programs believe those numbers and never look at the outlines. A layer's bounding box gives the top and bottom of a whole glyph, components included, and a loop that starts from `None` finds the tallest and lowest. The win descent is counted downward as a positive number, so the room below is an addition, and a sign mistake there raises no error. `write_font_info` takes changes as tuples of master, field, old value and new value, and refuses when the old value no longer matches the font.

## Try it yourself

1. Print the eight numbers for all three masters as a table, one row per field and one column per master.
2. Change `extremes` so it also returns the second-tallest glyph. Which is it in the Bold, and how far below the Å?
3. Ines is thinking about Vietnamese, where a capital can carry two accents and reach 1,050 units. Without changing the font, work out what win ascent, hhea ascender and typo line gap would give 30 units of room and keep the two line heights equal.

## Next

The font's names and numbers have been read. One number changes every time a file leaves the building: the version. Chapter 97 raises it, writes it in the form the name wants, and notes the day.
