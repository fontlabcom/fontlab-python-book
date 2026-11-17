---
this_file: src_docs/md/part4-space/068-widen-the-lot.md
---

# 68. Open it up a little

Wednesday of week thirteen. Mira's list has said the same thing in four different hands since last Monday. "Whole Bold tight." "Bold o: 30 and 8." "Bold zero has 12 a side." "Bold rounds wrong together." Yesterday's script couldn't help with it, because a fault that every letter shares isn't an odd one.

The cause has been plain since chapter 61. When the Bold was made, the black grew and the widths stayed. The left sides were set by hand to sensible values. The right sides got whatever was left over.

Ines has a second reason to care. The catalog sets its captions in the Bold at a small size, and small type wants more air between its letters, not less.

So today every Bold right side in the alphabet gets a new value, in one go. The question is which value.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, and the Font window in front.
- The helpers `ask`, `ask_text` and `tell` from chapter 39. The scripts below write them out again, so each one runs by itself.
- `copy_sb.py` from chapter 63, for the accented letters at the end.

The script changes the font, in one Undo step. I couldn't run it in FontLab 9. Its numbers come from Plum's source file with the changes of chapters 62, 63 and 67 worked in.

## Step 1: The obvious cure, and what's wrong with it

Too tight means too little, so add some. Say 20 units on the right of every letter. Before you write anything into the font, work out what that would give for four letters:

```python
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box, run_text_dialog
from fly.tr.proxy.fl.objects.glyph import pGlyph

TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask_text(label, start=""):
    return run_text_dialog(qt.QtGui, label, start, TITLE)


font = fl.CurrentFont()
for name in ["n", "o", "H", "D"]:
    rich = pGlyph(font, font[name])
    print(name, rich.getLSB("Bold"), rich.getRSB("Bold") + 20)
```

```text
n 56 52
o 30 28
H 56 60
D 56 37
```

Left side, then the right side as it would be. The `n` and the `o` come out close to even, which looks promising. The `H` would have more on its right than on its left, and the `D` has 37 where the round `o` has 28.

Adding the same number to everything is called tracking, and it's what a layout program does when you ask it to letterspace a line. It moves every letter apart by the same amount. It can't make an uneven font even: whatever was 16 units out before is 16 units out after. For Ines's captions tracking would be fine, if the Bold were sound to begin with. It isn't, so the mending comes first.

There's a second thing wrong with it, and it's about scripts and not about type. Run an "add 20" script twice and you've added 40. Nothing in the font remembers that you've been there already. A script like that is safe only in the hands of somebody who never loses count.

## Step 2: A better source

There's one master where the right sides are known to be good. Last Thursday's report found the Regular clean: every follower matched its model. So take the Bold's right sides from the Regular's, made smaller by the amount the Bold is tighter.

How much tighter is it meant to be? The left sides say. They were set by hand:

```python
print(56 / 70)
print(30 / 38)
```

```text
0.8
0.7894736842105263
```

The Bold `n` has 56 on its left where the Regular has 70, and the `o` has 30 against 38. Both come to about 0.8, four fifths. Somebody chose that, on purpose, for the left sides. Give the right sides the same treatment:

```python
print(66 * 0.8)
print(38 * 0.8)
print(70 * 0.8)
```

```text
52.800000000000004
30.400000000000002
56.0
```

Those are the Regular right sides of `n`, `o` and `H` at four fifths. Two things to notice.

The stray 4 and 2 at the far end aren't yours. A computer stores 0.8 in a form that can't hold it whole, as you can't write a third in full in decimal figures, and the tiny error shows up after the multiplying. It's about a hundred million millionth of a unit. You'll never see it in a font, and you shouldn't try to remove it. You remove the whole tail:

```python
print(round(66 * 0.8), round(38 * 0.8), round(70 * 0.8))
```

```text
53 30 56
```

And look at what came out. The Bold `o` gets 30 on the right, and it has 30 on the left. The `H` gets 56 and has 56. Nobody told the script that round letters and straight letters ought to be even on both sides. The Regular knew, and the sum carried it over.

This sum also has a property that "add 20" lacks. It reads the Regular and writes the Bold. Run it twice and the second run finds everything already in place. Run it with 0.85 next week and you get 0.85 of the Regular, not 0.85 on top of 0.8. A script that works out its answer from a source it doesn't change can be run as often as you like.

## Step 3: Ask for the factor

0.8 is a guess from two letters, and Ines will want to try others. So the script asks, with `ask_text` from chapter 39 and a starting value in the field:

```python
text = ask_text("Right sides, as a share of the Regular's:", "0.8")
print(round(66 * text))
```

Click OK, and:

```text
Traceback (most recent call last):
  File "<string>", line 2, in <module>
TypeError: type str doesn't define __round__ method
```

That's today's mistake. The message says `round` was handed a `str`, a piece of text. But you multiplied 66 by something first. What did that give? Take the `round` away and look:

```python
print(66 * text)
```

```text
0.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80.80
```

Sixty-six times the text `0.8`, end to end. Whatever comes out of a text field is text, even when every character in it is a figure. And a number times a text isn't an error in Python. It means "repeat": `3 * "ab"` is `"ababab"`. So the wrong line ran without complaint, and the complaint came one step later, from `round`, which didn't know what to do with a string 198 characters long.

The cure is to say what you mean. `float` turns a text into a number with a decimal point:

```python
factor = float(text)
print(factor, round(66 * factor))
```

```text
0.8 53
```

`float` is short for "floating point", the name of that inexact way of storing numbers you met a minute ago. Its sister `int` makes whole numbers and refuses `"0.8"`.

## Step 4: When the text isn't a number

Mira types the factor the way she writes it on paper, with a comma: `0,8`.

```text
ValueError: could not convert string to float: '0,8'
```

Python wants a point. And somebody will type `four fifths` one day, or nothing. A person who mistypes into a field shouldn't get a traceback for it. Chapter 19 had the tool: `try` the conversion, and if it raises `ValueError`, say so kindly and stop.

```python
def ask_factor(start):
    text = ask_text("Right sides, as a share of the Regular's:", start)
    if text is None:
        return None
    try:
        return float(text.strip())
    except ValueError:
        tell(f"{text} isn't a number I can read. Use a point, as in 0.8.")
        return None
```

The function has three ways out. Cancel gives `None`. A good number gives the number. Bad text gives a message and then `None`. Whoever calls it has one thing to check: `None` means stop.

## The whole script

```python
#FLM: Open Up Bold
# Sets the Bold's right sidebearings to a share of the Regular's.
import string

import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.metrics.panel.model as metrics
from fly import fl, qt
from fly.pens import layer_of
from fly.ap.ui.dialogs import run_standard_message_box, run_text_dialog
from fly.tr.proxy.fl.objects.glyph import pGlyph

TITLE = "Halfmoon"

SOURCE = "Regular"
TARGET = "Bold"
LETTERS = string.ascii_uppercase + string.ascii_lowercase


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes


def ask_text(label, start=""):
    return run_text_dialog(qt.QtGui, label, start, TITLE)


def ask_factor(start):
    text = ask_text(f"Right sides, as a share of the {SOURCE}'s:", start)
    if text is None:
        return None
    try:
        return float(text.strip())
    except ValueError:
        tell(f"{text} isn't a number I can read. Use a point, as in 0.8.")
        return None


def plan_rows(font, factor):
    rows = []
    for name in LETTERS:
        if font[name] is None:
            continue
        rich = pGlyph(font, font[name])
        layer = layer_of(rich.fl, TARGET)
        if str(layer.metricsRight) or str(layer.metricsWidth):
            print(f"{name}: has a rule for its right side or width. Left alone.")
            continue
        old = rich.getRSB(TARGET)
        new = round(rich.getRSB(SOURCE) * factor)
        if new != old:
            rows.append((rich, layer, old, new, rich.getAdvance(TARGET) + new - old))
    return rows


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    factor = ask_factor("0.8")
    if factor is None:
        return

    rows = plan_rows(font, factor)
    for rich, layer, old, new, width in rows:
        print(f"{rich.name:<4}{old:>5} to {new:>3}   width {rich.getAdvance(TARGET)} to {width}")
    print(f"{len(rows)} layers to change, factor {factor}.")
    if not rows or not ask(f"Set {len(rows)} right sidebearings in the {TARGET}?"):
        return

    def change():
        for rich, layer, old, new, width in rows:
            metrics.shift_and_set(layer, 0, width)

    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    layers = [layer for rich, layer, old, new, width in rows]
    owners = [rich.fl for rich, layer, old, new, width in rows]
    history.commit("Open up", layers, owners, change,
                   operation="geometry", facts=facts, allow_bases=True)
    print(f"Done. {len(plan_rows(font, factor))} layers still off.")


main()
```

Save it as `open_up.py`. With 0.8 in the field it prints 52 lines, one for every letter of the alphabet in both cases. Here are the first five and three from the middle:

```text
A     -33 to   9   width 596 to 638
B      15 to  35   width 517 to 537
C      26 to  23   width 621 to 618
D      17 to  33   width 665 to 681
E       9 to  31   width 485 to 507
m      32 to  53   width 806 to 827
n      32 to  53   width 523 to 544
o       8 to  30   width 520 to 542
52 layers to change, factor 0.8.
```

Your `m` line may read differently if you skipped chapter 62, where its width went to 806. What comes after "to" won't: 53, whatever it was before.

Notes on the listing.

`import string` brings in a small module from the library that came with Python. `string.ascii_uppercase` is the text `"ABCDEFGHIJKLMNOPQRSTUVWXYZ"` and `string.ascii_lowercase` is the same in small letters. Typing the alphabet yourself is a fine way to lose a letter, and yesterday's trick of looping over a string does the rest.

The commit passes `allow_bases=True`. Most letters of the alphabet are borrowed by automatic accented letters, and without the keyword the script would stop at `A` with a refusal. Chapter 55 said what the keyword agrees to, so save the font before you answer Yes.

Each row carries its layer, which is what exercise 2 of chapter 66 asked you to do. The script fetches every layer once, while planning, and `change` has nothing to look up.

`shift_and_set(layer, 0, width)` moves the drawing by nothing and sets the width. A right side is the width's business alone, as chapter 62 found.

The `metricsRight` test does what chapter 65 said it would. A layer whose right side follows a rule gets its value from the rule, and a script that wrote a number over it would be arguing with the font. On Plum no Bold layer has such a rule, and nothing is skipped.

And `C` goes down, from 26 to 23. The script doesn't only give. It sets each right side to its share of the Regular's, and two letters, `C` and `G`, had more than their share. All 52 changes together add 1,511 units to the alphabet. The `W` gains most, 85.

## Did it work?

Answer Yes, and run `sb_report.py` from chapter 61 on the word that started all this, in the Bold:

```text
minimum
   109  104  109  104  105  112   smallest 104, spread 8
```

Last Monday that line read 60, 80, 78, 80, 66 and 92. After chapter 62's two repairs the smallest gap was 80 and the spread was 12. The Regular has 126 to 140 in the same places. The Bold's six gaps now rise and fall in step with the Regular's, at a little over four fifths of their size. That was the intention when somebody set its left sides.

Then the letters that follow. The accented letters still have their old widths, and the rule from chapter 63 says a composite is as wide as its base. In `copy_sb.py`, set both dictionaries to `{}` and run it. The first pass finds nothing to do. The second offers the Bold layers of the accented letters you built yourself in chapters 53, 56 and 60, where the base under them got wider, and makes them as wide as their bases. Plum's own accented letters are automatic, so the script names them on its last line and leaves them to FontLab. There are more than sixty of those layers. Look at one, the Bold `aacute` say, to see whether FontLab has made it as wide as the `a`. `IJ` and `ij` aren't accented letters and stay as they were. They've been on Mira's list since chapter 62, and they stay on it.

Two things today's script didn't touch, on purpose. The figures keep the width chapter 66 gave them. And the drawn letters outside the plain alphabet, `germandbls`, `ae`, `oslash` and their kind, aren't in `LETTERS`. The third exercise brings them in.

## What Ines thinks

She sets a caption in the new Bold at the catalog's size and holds it at arm's length. Better. For the smallest size she'd like a touch more, so Mira runs the script again with 0.85: 45 layers change, the `n` goes from 53 to 56 and the `o` from 30 to 32. She lets `copy_sb.py` bring the accents along and prints. They pin both proofs up. After a while Mira chooses **Edit > Undo** twice, once for the accents and once for the letters, and the font is back at 0.8. "The font is right at 0.8," she says. "Captions can be tracked in the layout. That's what tracking is for."

She crosses four lines off her own list.

## What you learned

Adding one amount to every sidebearing keeps every unevenness, and a script that adds can't be run twice safely. A script that reads one master and writes another gives the same result however often you run it. Multiplying by a decimal factor leaves a long tail, and `round` cuts it off and gives a whole number. Text from a field is text: `float` turns it into a number, and `try` with `except ValueError` catches what `float` can't read.

## Try it yourself

1. Make `ask_factor` accept `0,8`. Chapter 30's `replace` can turn the comma into a point before `float` sees the text. Then type `0,8,5` and check that the person still gets the kind message.
2. A factor of 8 is surely a slip for 0.8, and it would set the `n` to 528. Make `ask_factor` refuse anything below 0.5 or above 1.5, with a message that says what the limits are. Where does the test go: inside the `try`, or after it? Try both and say which reads better.
3. Add `"germandbls"`, `"ae"` and `"oslash"` to the letters. `LETTERS` is a string and can't hold a ten-letter name as one thing, so turn it into a list first: `list(string.ascii_uppercase + string.ascii_lowercase) + ["germandbls", "ae", "oslash"]`. Run the script and answer No. Which of the three would change most?

## Next

The sidebearings are in order: every letter has a left and a right that make sense on their own. Some pairs of letters still don't sit well together, and no sidebearing can mend that, because what suits `A` beside `H` is wrong for `A` beside `V`. Chapter 69 opens the list of exceptions the font keeps for such pairs: its kerning.
