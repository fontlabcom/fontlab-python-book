---
this_file: src_docs/md/part1-first-words/014-mark-them-red.md
---

# 14. Mark them red

Mira prints the list of empty glyphs for Ines and reads it out: space, a.sc, b.sc, c.sc. Ines nods, turns to the Font window and starts hunting for the four cells. The list is correct, but Ines still has to carry it in her head from one window to the other.

Designers solved this long before scripts. They mark glyphs with a color: red for "not drawn yet", green for "approved". The colored cells stand out in the Font window at a glance. Line 5 of Oskar's sheet even says so: *Mark every glyph that mixes its own outlines with borrowed ones.* That chore needs things you'll learn in Part 2. But the marking half of it you can learn today.

Every script so far has read the font. This is the first one that writes to it, so we start with a precaution.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open in a Font window.
- `empty_glyphs.py` from [chapter 8](008-only-the-ones-i-want.md).

## Step 1: Save first

Until now, nothing you ran could harm the font. You asked questions, and the font was the same afterwards. From this chapter on, some scripts change things, and a script can change two hundred glyphs in the time it takes you to blink.

So make two habits now.

Work on a copy. You already do: `Plum-practice` is your copy, and the original `plum-var.vfj` stays untouched.

Save before you run. Choose **File > Save Font**. Now the file on disk holds the font as it was before the script. If the script does something you didn't want, choose **File > Revert Font**, and FontLab loads the font from disk again, as you saved it.

You might expect **Edit > Undo** to do that job. Don't count on it. Undo remembers the steps you take by hand. The changes in this chapter go into the font by a different door, and they leave no step behind for Undo to take back. Part 2 shows how a script can leave a proper Undo step. Until then, saving and reverting is your way back.

## Step 2: Read a mark

In chapter 8 you met the richer glyph: `pGlyph(font, glyph)` takes a plain glyph and hands back one that knows more about its own drawing. You asked it one question, `isEmpty()`. It has drawers too. One of them is called `mark`.

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

font = fl.CurrentFont()
rich = pGlyph(font, font["space"])
print(rich.mark)
```

```text
0
```

The box `rich` holds the richer version of the space glyph, so the long line doesn't have to be typed twice. Its mark is `0`, and `0` means no mark at all. If you got another number, somebody has marked the space in your copy by hand. That's fine. Read on and you'll see what the number means.

## Step 3: Change it

In chapter 5 you learned to read `=` as "becomes": the box on the left gets the thing on the right. Until now the left side was always a box of your own. It can be a drawer, too.

```python
rich.mark = 1
print(rich.mark)
```

```text
1
```

Add these two lines under the others and run the script. "The mark of this glyph becomes 1." Reading a drawer and writing to it use the same dot and the same name. Which one happens depends on the side of the `=` the drawer stands on.

Now look at the Font window and find the space. Its cell should be red. If it isn't yet, click the Font window so that FontLab draws it again.

A script changed the font for the first time in this book, and the change is as real as if you'd made it by hand. The mark is part of the font now, and if you save, the red mark is saved with it.

## Step 4: What the number means

Why is `1` red? FontLab stores a mark as one number, and the number is a position on the color wheel. The wheel runs through 360 degrees: red at the start, then yellow, green, cyan, blue, magenta and back to red. The mark is the position plus one, so that `0` stays free to mean "no mark".

| Mark | Color |
|---|---|
| 0 | none |
| 1 | red |
| 61 | yellow |
| 121 | green |
| 241 | blue |

Try a few. Change the `1` in your script to `121` and run it, then to `241`. Then set it back to `0`, and the cell goes plain again.

You don't have to remember the numbers. When a script needs a color, give the number a name at the top and use the name:

```python
RED = 1
GREEN = 121
```

The capitals don't mean anything to Python. They're a custom, and chapter 17 comes back to it.

## Step 5: The mistake that makes no noise

Now make a mistake on purpose. Type the drawer's name with a capital M:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

font = fl.CurrentFont()
rich = pGlyph(font, font["space"])
rich.Mark = 121
print(rich.mark)
```

```text
0
```

There's no letter of complaint. The script ran to the end. And the mark is still `0`.

Compare that with chapter 6. There, you asked for a drawer that didn't exist, and Python refused with an `AttributeError`. Reading from a drawer that isn't there is an error. Writing to one often isn't. The richer glyph is a wardrobe that lets you add drawers, so Python made a new drawer called `Mark`, put 121 in it, and went on. FontLab never looks in that drawer. It only knows `mark`.

This is the first mistake in the book that Python doesn't catch for you. From now on, when a script writes something, make it read the value back, or go and look at the font. A script can finish without an error and still not have done what you meant.

Fix the capital and run it again. Then set the mark back to `0`.

## Step 6: Mark the empty ones

You have a loop that finds the empty glyphs, and you have a line that marks one glyph. Put the line inside the loop. Open `empty_glyphs.py`, change it to this, and save it as `mark_empty.py`:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

RED = 1

font = fl.CurrentFont()
count = 0
for glyph in font.glyphs:
    rich = pGlyph(font, glyph)
    if rich.isEmpty():
        rich.mark = RED
        count = count + 1
        print("Marked", glyph.name)
print(f"Marked {count} of {len(font)}")
```

Before you run it: **File > Save Font**. Then run.

```text
Marked space
Marked a.sc
Marked b.sc
Marked c.sc
Marked 4 of 208
```

The loop makes the richer glyph once for each turn and keeps it in the box `rich`. Then it uses the box twice: once to ask the question, once to write the mark. The script still prints the names. A script that changes things should say what it changed, so that you can check the font against the list.

Look at the Font window. The space is red, and at the end of the font, three red cells sit in a row. Ines doesn't need the list any more.

Now practice the way back. Choose **File > Revert Font**. FontLab loads the saved font, and the red cells are plain again. Run `mark_empty.py` once more to get them back, and this time keep them.

One more thing about the space. It's marked red as "not drawn yet", and it'll never be drawn, because a space has nothing in it by design. The test says "empty". It can't tell which glyphs are supposed to be empty. Leave it for now. In chapter 13 you learned to join two tests, and exercise 2 asks you to use that here.

When Mira draws the `a.sc`, the cell will stay red until somebody changes it. A mark doesn't follow the drawing, and it only changes when a person or a script sets it again. That's why a marking script is one you run again and again, and why it should also clear the marks that are no longer true. Exercise 3 does that.

??? info "Going deeper: grays, and marks on layers"
    The numbers 1 to 360 are the color wheel. The numbers from 1001 to 1255 are a scale of grays, from dark to light, for marks that should stay quiet. Other numbers aren't valid marks.

    The plain glyph you get from `font["space"]` has a `mark` drawer of its own, and it holds the same value. This book writes marks through the richer glyph, because the richer glyph is what you'll use for every other change to a glyph in parts 2 and 3. A glyph can also carry a different mark on each of its layers. Part 6 is about fonts with more than one layer.

## What you learned

A drawer on the left side of `=` gets a new value, in the same way a box does, and that's how a script changes a font. A glyph's mark is one number: `0` for none, and a position on the color wheel plus one for a color, so `1` is red and `121` is green. Marks set by a script don't go through Undo, so you save before you run and use **File > Revert Font** to go back. Writing to a misspelled drawer raises no error, so a script that writes should print what it did.

## Try it yourself

1. Mark every glyph that has no Unicode value in green. The test is in chapter 8. How many cells turn green, and which glyphs end up green that were red before?
2. Change `mark_empty.py` so that it doesn't mark the space: join the empty test with a second test on the glyph's name, using `and` from chapter 13. It should report `Marked 3 of 208`.
3. Write `clear_marks.py`: a loop that sets every glyph's mark to `0` and counts how many glyphs had a mark other than `0` before. Save the font first, run it, and then decide whether to revert.

## Next

Chapter 15 lets you point at glyphs with the mouse and have the script work on the ones you picked.
