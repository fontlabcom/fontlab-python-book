---
this_file: src_docs/md/part4-space/066-tabular-figures.md
---

# 66. Figures that line up

Monday of week thirteen. The publisher's spring price list came back from the typesetter with a note in the margin: "Columns wobble. Pounds worst." Ines pins it to the board. Thirty titles, thirty prices, set in Plum, with the figures stacked in columns so that a reader can run an eye down the pence.

Figures made for columns are called tabular figures: every one of them has the same advance width, so the fourth figure of one price stands under the fourth figure of the next. Figures made for running text are proportional: the `1` is narrow and the `0` is wide, as letters are. Plum has one set of figures, and Mira is sure they were drawn as tabular.

"Then why do they wobble?" Ines asks.

That's a question with numbers in it, so it's a question for a script.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, and the Font window in front.
- The helpers `ask` and `tell` from chapter 39. The scripts below write them out again, so each one runs by itself.

The script at the end changes the font, in one Undo step. I couldn't run it in FontLab 9. The measurements come from Plum's source file.

## Step 1: Are they tabular?

The figures have names, not digits: the glyph for 0 is called `zero`. Write the ten names down once and ask each for its width:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

FIGURES = ["zero", "one", "two", "three", "four",
           "five", "six", "seven", "eight", "nine"]
font = fl.CurrentFont()
widths = [pGlyph(font, font[name]).getAdvance("Regular") for name in FIGURES]
print(widths)
print(set(widths), len(set(widths)))
```

```text
[490, 490, 490, 490, 490, 490, 490, 490, 490, 490]
{490} 1
```

Ten times 490. A set keeps one of each, as chapter 25 showed, so a set of the widths with one thing in it means "all the same". `len(set(widths)) == 1` is a tidy test for it, and you'll use it again.

The Light gives 456 ten times, and the Bold 490. Mira was right. The figures are tabular, in all three masters. So the wobble isn't in the widths.

## Step 2: The signs that go with them

"Pounds worst," the note said. A price isn't only figures. Ask the currency signs too:

```python
SIGNS = ["dollar", "Euro", "sterling", "yen"]

for master in ["Light", "Regular", "Bold"]:
    print(master, [pGlyph(font, font[name]).getAdvance(master) for name in SIGNS])
```

```text
Light [456, 456, 489, 480]
Regular [490, 490, 480, 490]
Bold [490, 490, 480, 490]
```

There's the first fault. The dollar and the euro sign have the figures' width. The pound sign doesn't, in any master: it's 33 units too wide in the Light and 10 too narrow in the other two. The yen is off in the Light. In a column of prices in pounds, every line begins with a sign of the wrong width, and everything after it stands 10 units to the side of where the column above expects it.

(`Euro` has a capital letter. It's the name the glyph has carried since the 1990s, and names must match letter for letter.)

## Step 3: Same width isn't the whole story

Mira looks at the Bold column of the price list longer than at the others. "They're all leaning," she says. Print the three numbers of chapter 61 for a few Bold figures:

```python
for name in ["zero", "four", "eight"]:
    rich = pGlyph(font, font[name])
    print(name, rich.getLSB("Bold"), rich.getAdvance("Bold"), rich.getRSB("Bold"))
```

```text
zero 28 490 -4
four 24 490 -19
eight 37 490 5
```

The Bold zero has 28 units of white on its left and less than nothing on its right: the black pokes 4 units out of its own box. It's the Bold's old trouble again. The figures were fattened inside widths nobody changed, and they grew to the right.

In running text that only looks tight. In a table it does something else. A tabular figure is a black shape in a fixed box, and a column looks straight when each shape sits in the middle of its box. The Regular zero does: 36 and 36. The Regular seven doesn't quite: 53 and 29.

So there are two things to do. Give the signs the figures' width. And put every shape in the middle of its box.

## Step 4: The centering sum

Take the Regular seven: 53 on the left, 490 wide, 29 on the right.

The black is what's left when you take both sidebearings from the width. I'll call it the ink, to keep it apart from the Bold's kind of black:

```python
left, width, right = 53, 490, 29
ink = width - left - right
print(ink)
```

```text
408
```

The box is 490 and the ink is 408, so there are 82 units of white to share. Half on each side:

```python
target = 490
print((target - ink) / 2)
```

```text
41.0
```

The seven should have 41 on its left. It has 53, so it moves by 41 minus 53: 12 units to the left. Its width stays 490, and the right side comes out as 41 too.

Now the same sum for the Regular two, which has 41, 490 and 50:

```python
left, width, right = 41, 490, 50
ink = width - left - right
print(ink, (target - ink) / 2)
```

```text
399 45.5
```

That's the mistake of the chapter, and Python didn't complain about it. 91 units of white don't halve evenly. If you hand 45.5 on, the script moves the outline by 4.5 units, and every node of the two lands on a half. Plum's nodes all sit on whole units, and as far as I know a font with nodes on halves gets them rounded at export, each on its own. I haven't checked that in FontLab 9. You've met the cure: `//` from chapter 49, the division that keeps whole numbers whole.

```python
print((target - ink) // 2)
```

```text
45
```

45 on the left, and the odd unit goes to the right: 46. You could round instead. But chapter 53 showed that `round` sends a half to the nearest even number, so 45.5 would become 46 and 44.5 would become 44, and the spare unit would land left for one figure and right for the next. With `//` it always lands on the right. In a column, always is better than nearly.

## Step 5: One function for the sum

```python
def centered(left, width, right, target):
    ink = width - left - right
    new_left = (target - ink) // 2
    return new_left - left


print(centered(53, 490, 29, 490))
print(centered(41, 490, 50, 490))
print(centered(59, 480, 28, 490))
```

```text
-12
4
-11
```

The function takes four plain numbers and returns the distance to move. It knows nothing about fonts, so you can try it on numbers you've worked out on paper before any glyph is touched. The third line is the Regular pound sign: 59, 480 and 28 going into a box of 490. Its ink is 393, the white is 97, the left share is 48, and it moves 11 to the left while its box grows by 10.

Moving and setting the width in one go is what `metrics.shift_and_set` did in chapter 62. Nothing new is needed for the writing.

Where does `target` come from? From the figures themselves: `max` of their ten widths. Today the ten are equal and `max` has nothing to decide. If one of them ever differs, the widest wins, and that's the safe direction: a shape can always be given more room, and it can't always be squeezed.

## The whole script

```python
#FLM: Make Tabular
# Gives figures and currency signs one width in each master
# and centers each shape in it.
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.metrics.panel.model as metrics
from fly import fl, qt
from fly.pens import layer_of
from fly.ap.ui.dialogs import run_standard_message_box
from fly.tr.proxy.fl.objects.glyph import pGlyph

TITLE = "Halfmoon"

MASTERS = ["Light", "Regular", "Bold"]
FIGURES = ["zero", "one", "two", "three", "four",
           "five", "six", "seven", "eight", "nine"]
SIGNS = ["dollar", "Euro", "sterling", "yen"]


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes


def centered(left, width, right, target):
    ink = width - left - right
    new_left = (target - ink) // 2
    return new_left - left


def plan_rows(font):
    rows = []
    for master in MASTERS:
        widths = [pGlyph(font, font[name]).getAdvance(master) for name in FIGURES]
        target = max(widths)
        if len(set(widths)) > 1:
            print(f"{master}: the figures have {len(set(widths))} widths. Using {target}.")
        for name in FIGURES + SIGNS:
            rich = pGlyph(font, font[name])
            left = rich.getLSB(master)
            width = rich.getAdvance(master)
            right = rich.getRSB(master)
            dx = centered(left, width, right, target)
            if dx != 0 or width != target:
                rows.append((rich, master, dx, width, target))
    return rows


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    missing = [name for name in FIGURES + SIGNS if font[name] is None]
    if missing:
        tell(f"No glyph named: {' '.join(missing)}")
        return

    rows = plan_rows(font)
    for rich, master, dx, width, target in rows:
        print(f"{rich.name:<10}{master:<9}move {dx:+}, width {width} to {target}")
    print(f"{len(rows)} layers to change.")
    if not rows or not ask(f"Center {len(rows)} layers?"):
        return

    layers = [layer_of(rich.fl, master) for rich, master, dx, width, target in rows]
    owners = {}
    for rich, master, dx, width, target in rows:
        owners[rich.name] = rich.fl

    def change():
        for row, layer in zip(rows, layers):
            metrics.shift_and_set(layer, row[2], row[4])

    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    history.commit("Make tabular", layers, list(owners.values()), change, operation="geometry", facts=facts)
    print(f"Done. {len(plan_rows(font))} layers still off.")


main()
```

The Regular part of what it prints:

```text
one       Regular  move +15, width 490 to 490
two       Regular  move +4, width 490 to 490
three     Regular  move +10, width 490 to 490
four      Regular  move -7, width 490 to 490
five      Regular  move -1, width 490 to 490
six       Regular  move -3, width 490 to 490
seven     Regular  move -12, width 490 to 490
nine      Regular  move +2, width 490 to 490
dollar    Regular  move +3, width 490 to 490
Euro      Regular  move -16, width 490 to 490
sterling  Regular  move -11, width 480 to 490
yen       Regular  move -1, width 490 to 490
```

Twelve lines there. The zero and the eight are missing from it because they were in the middle already. The Light has twelve lines as well, and the Bold fourteen: every Bold figure moves left, by between 6 and 22 units. The list ends:

```text
38 layers to change.
```

And after you answer Yes, if the font reads back at once what was written into it:

```text
Done. 0 layers still off.
```

That last line plans the whole job a second time and counts what's left. It's the check-after habit of chapter 62 in one line: the script that knows how to find the fault is the best judge of whether the fault has gone. If it prints anything other than 0, run the script again and read its list.

The structure is `copy_sb.py` from chapter 63 again. Rows are planned first, as tuples. They're shown. You're asked. Then one `change` function does all of them inside one `history.commit`, so that one **Edit > Undo** should take all 38 back. I haven't seen it in FontLab 9. When a pattern has worked three times, it's worth recognizing as yours.

One line in `change` is lazier than I'd like: `row[2]` and `row[4]`. They're the move and the target, by position in the tuple. It works, and a week from now you won't remember what the 2 and the 4 were. The second exercise mends it.

Nothing borrows the figures in Plum, so no composite is left behind today. If your own font has fractions or superior figures built from components of these, run the borrowers check from chapter 62 first.

## What Mira does with it

She runs it, prints the price list again, and pins the new sheet beside the old one. The pounds column is straight. The Bold column no longer leans.

Then she takes the `one` back out. Centered by arithmetic, the Regular `1` moved 15 units to the right, and to her eye it now stands too far from the figure before it. A `1` is a stem with a flag on its left; its black isn't spread evenly over its ink, and its middle for the eye isn't its middle for the ruler. She moves it back 6 by hand.

That isn't the script failing. The sum gives every figure the same fair start in an afternoon's worth of clicks, and the eye spends its time on the one that needs it. She adds a line to her list: "Figures: Bold zero has 12 a side. Whole Bold tight."

## What you learned

Tabular figures share one advance width, and `len(set(widths)) == 1` tests that. Equal widths aren't enough for straight columns: each shape also has to sit in the middle of its box, and the signs that stand with the figures need the same box. The white to share is the box less the ink, and `//` halves it in whole numbers, with the spare unit always on the same side. A function that takes plain numbers can be tried on paper sums before it meets a glyph.

## Try it yourself

1. Work out on paper what `centered(28, 490, -4, 490)` gives, and what the Bold zero's two sidebearings are afterwards. Then run the line. A negative sidebearing goes through the sum like any other number: why does the ink come out larger than the box less 28?
2. Change `plan_rows` so that each row carries the layer too, and `change` so that it unpacks every row into names, as the `for` lines in `main` do. The `zip` and the positions `row[2]` and `row[4]` should both disappear.
3. Add `"percent"` to `SIGNS` and run the script, and answer No. What does it offer to do with the percent sign, which is 798 wide in the Regular? Take the name out again.

## Next

The figures showed a fault that the eye had missed for years and a script found in a second: one glyph whose number didn't match its neighbors'. Chapter 67 looks for that kind of fault everywhere, by comparing each glyph with the usual value of its group.
