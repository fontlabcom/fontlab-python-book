---
this_file: src_docs/md/part1-first-words/015-the-selection.md
---

# 15. The selection

Ines is looking at a proof of Plum's lowercase and something bothers her about the rhythm. She asks Mira for the widths of ten letters, the ones with a bowl or an arch: a, b, d, e, g, h, n, o, p, q. And their average, if that's no trouble.

Mira knows two ways to do it. She can loop over the whole font and print 208 lines, then pick out ten by eye. Or she can type the ten names into a list, as in chapter 7. That works, until Ines says "and now the same for these", pointing at the screen.

Pointing is the natural way to say which glyphs you mean. You click one cell in the Font window, you hold a key and click the others, and the cells you picked are highlighted. FontLab calls that the selection. Today the script asks FontLab what you picked.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open in a Font window.
- No Glyph window in front. The tool in this chapter reads the selection of the Font window.

## Step 1: Select ten glyphs

In the Font window, click the cell of `a`. Then hold ++cmd++ on a Mac, or ++ctrl++ on Windows, and click `b`, `d`, `e`, `g`, `h`, `n`, `o`, `p` and `q`. Ten cells are highlighted.

If you click without the key, the selection starts over with that one cell. That's fine. Start again.

## Step 2: Ask what's selected

```python
import fly.ap.core.scripting as scripting

names = scripting.names_selected_names()
print(names)
```

```text
['a', 'b', 'd', 'e', 'g', 'h', 'n', 'o', 'p', 'q']
```

The square brackets tell you what came back: a list. The quotes tell you what's in it: strings. FontLab handed your script the names of the ten glyphs you clicked. If your list comes in another order, you'll put it in order yourself in a moment.

The first line is a new kind of import, so let's read it slowly. Until now you've written `from fly import fl`: from the toolbag, take one tool. This line says: `import` a whole pocket of the bag, the one at `fly.ap.core.scripting`, and `as scripting` gives it a short label so you don't have to write the long path every time you use it. The pocket holds many tools. You reach each one with a dot: `scripting.names_selected_names()`.

The tool's name is long, and it tells you what you get: the names of the selected glyphs. The parentheses are empty because the tool needs nothing from you. You've been calling tools that hand something back since `len` in chapter 5. This one hands back a whole list, and you can do with it everything chapter 10 taught you:

```python
print(len(names))
print(names[0])
print("o" in names)
print("z" in names)
```

```text
10
a
True
False
```

The last two lines use `in` on a list. In chapter 9 it asked whether one string sits inside another. Between a thing and a list, it asks whether the thing is one of the list's items.

## Step 3: Names are not glyphs

Now ask the first selected glyph for its width.

```python
print(names[0].width)
```

```text
AttributeError: 'str' object has no attribute 'width'
```

Read the complaint. A `'str' object` is a string. The list holds names, and a name is text: it has the drawers that strings have, like `endswith`, and no `width`. The glyph has the width. The name is only the label on the wardrobe.

You know how to get from the name to the glyph. You did it in chapter 6:

```python
from fly import fl

font = fl.CurrentFont()
glyph = font[names[0]]
print(glyph.name, glyph.width)
```

```text
a 471.0
```

`font[...]` takes a name and hands back the glyph. Here the name comes out of the list, where in chapter 6 you typed it in quotes. This two-step move, ask for names and then look each one up in the font, is how most scripts in this book get from "what the designer pointed at" to "the glyphs to work on".

## Step 4: Loop over the selection

One glyph works, so do all ten. Start a new script:

```python
import fly.ap.core.scripting as scripting
from fly import fl

font = fl.CurrentFont()
names = scripting.names_selected_names()

total = 0
for name in sorted(names):
    glyph = font[name]
    total = total + glyph.width
    print(f"{name:<10}{glyph.width:>6.0f}")
print(f"{len(names)} glyphs, average width {total / len(names):.0f}")
```

```text
a            471
b            543
d            543
e            470
g            543
h            523
n            523
o            520
p            543
q            543
10 glyphs, average width 522
```

Nothing in the loop is new. It's the loop over a list of names from chapter 7, with the running total from that chapter's exercise, the columns from chapter 12 and `sorted` from chapter 10. What's new is where the list comes from. You didn't type it and the script didn't build it. You pointed.

Mira sends the table to Ines. The four letters with a bowl and a stem, b, d, p and q, are all 543 wide, and so is g. The two arches are 523. The outsiders are a and e, about fifty units narrower than the `o`. Ines says that's what she saw.

Now click a different set of cells in the Font window, say the figures, and run the script again without changing a character of it. This is the point of the chapter. A script that reads the selection is one you write once and then aim with the mouse.

## Step 5: When nothing comes back

What does the tool hand back when you've selected one glyph and no more? Try it. Click one cell in the Font window so that only that glyph is selected, and run the script. You get one line and an average that equals the width. One is a fine number of glyphs.

The harder case is none. Close every font and run the script.

```text
ZeroDivisionError: division by zero
```

With no font open, the tool hands back an empty list, `[]`. The loop over an empty list runs zero times, without complaint, and `total` stays `0`. The last line then divides 0 by `len(names)`, which is also 0, and no number is the answer to that.

An empty list is not an error. It's a correct answer to "what's selected?". The script has to decide what to do with that answer, and it does so with an `if`:

```python
import fly.ap.core.scripting as scripting
from fly import fl

font = fl.CurrentFont()
names = scripting.names_selected_names()

if len(names) == 0:
    print("Nothing is selected.")
else:
    total = 0
    for name in sorted(names):
        glyph = font[name]
        total = total + glyph.width
        print(f"{name:<10}{glyph.width:>6.0f}")
    print(f"{len(names)} glyphs, average width {total / len(names):.0f}")
```

```text
Nothing is selected.
```

Everything that needs at least one glyph now sits under `else:`, one level further in. Save this as `selected_report.py`. Open `Plum-practice` again, select the ten letters, and check that the table is back.

Make this a habit for any list that comes from outside your script, whether from FontLab, from a file or from a person: ask how long it is before you count on its first item or divide by its length.

## Step 6: Put it to work

Mira has a use for this the same afternoon. She has sketched the `a.sc` on paper and counts it as started, and she wants to take its red mark away without touching the others. She selects the one cell and runs a short script, which is chapter 14's marking line fed by today's list:

```python
import fly.ap.core.scripting as scripting
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

font = fl.CurrentFont()
for name in scripting.names_selected_names():
    pGlyph(font, font[name]).mark = 0
    print("Cleared", name)
```

Remember the rule from chapter 14: this script writes to the font, so save the font first. Then select `a.sc` in your own copy and run it. You should see `Cleared a.sc` in the output, and the cell should go plain.

There's no `if` for the empty list here, and none is needed. A loop over an empty list does nothing, and nothing is the right thing to do. The guard in step 5 was there because of the division, not because of the loop.

??? info "Going deeper: what counts as selected"
    The tool reads the selection of the Font window. If no cells are highlighted but FontLab has a current glyph, the one that `fl.CurrentGlyph()` handed you in chapter 6, the tool hands back a list with that one name. So a script built on it does something sensible in both situations: on the cells you picked, or on the glyph you're looking at.

    The selection inside a Glyph window, where you pick nodes and contours of a drawing, is a different thing and has different tools. Part 3 gets to those. The tool also has a partner that goes the other way and makes a script select glyphs for you. You'll use it in Part 2, when a script that finds problem glyphs leaves them selected for you to look at.

## What you learned

`scripting.names_selected_names()` hands back a list of the names of the glyphs selected in the Font window, and `font[name]` turns each name into its glyph. A tool can hand back a whole list, and that list can be empty, so a script checks `len(names) == 0` before it divides by the length or reaches for the first item. `import ... as` brings in a whole pocket of tools under a short label. A script that works on the selection is written once and aimed with the mouse.

## Try it yourself

1. Select the ten figures, `zero` to `nine`, and run `selected_report.py`. All ten should be 490 wide, so the average is 490 too. Then add `period` and `comma` to the selection and watch the average drop.
2. Change the report so that its last line also names the widest and the narrowest glyph of the selection. Chapter 10's `sorted` won't do it alone, because it sorts names. Keep two boxes, `widest` and `narrowest`, start both with the first glyph, and compare inside the loop.
3. Write `mark_selected.py`: it marks every selected glyph green, mark 121, and prints how many it marked. Save the font before you run it.

## Next

Chapter 16 takes a script that has grown too long to read and cuts it into steps with names.
