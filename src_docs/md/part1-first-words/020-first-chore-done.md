---
this_file: src_docs/md/part1-first-words/020-first-chore-done.md
---

# 20. The first chore, done

It's Friday afternoon, three weeks after Mira found Oskar's sheet. The publisher's inventory is due on Monday, and Ines has added a condition: she wants to be able to produce it herself, for any font that's open, without calling anybody.

Mira has every piece of it. `three_lists.py` from chapter 16 finds the empty glyphs, the ones without a Unicode value and the small caps. `Friday Report.py` knows the family name and the date, lives in the **Scripts** menu and no longer falls over when no font is open. The width report from chapter 12 knows how to line up a column.

No Python is new today. The chapter is about putting the pieces together in an order that keeps working at every stage, which is a skill of its own.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `three_lists.py` from [chapter 16](016-name-your-steps.md) and `template.py` from [chapter 17](017-comments-and-names.md).
- The `Halfmoon` folder inside the `Scripts` folder, from [chapter 18](018-save-it-run-it-again.md).

## Step 1: Say what the script answers

Before you write a line, write down what the reader of the output wants to know. Tomas, at the publisher, asked five questions:

- How many glyphs are in the font?
- How many of them are empty?
- How many have a Unicode value, and how many don't?
- How many small caps are there?
- Which glyphs are behind each of those numbers?

That list is the plan. Each line of it will become one or two lines of the script, and when the output answers all five, you're done. Without the list, a script like this tends to grow a sixth and seventh answer that nobody asked for.

Open `template.py`, save it as `inventory.py` in your `scripting-book` folder, and turn the plan into the header:

```python
#FLM: Inventory
# Counts what is in the current font: all glyphs, empty glyphs,
# glyphs with and without a Unicode value, and small caps.
# Reads only. Changes nothing in the font.
```

The last comment line tells whoever runs the script what it leaves alone. Ines doesn't need to save the font first, as she would for the marking script of chapter 14. It's worth one line to say so.

## Step 2: Collect, in one walk

Bring in the working part of `three_lists.py`, and wrap it the way chapter 19 showed: a `main` function with a guard at the top.

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

SMALL_CAP_SUFFIX = ".sc"


def is_empty(font, glyph):
    return pGlyph(font, glyph).isEmpty()


def main():
    font = fl.CurrentFont()
    if font is None:
        print("Inventory: open a font first.")
        return

    empty = []
    no_unicode = []
    small_caps = []
    for glyph in font.glyphs:
        if is_empty(font, glyph):
            empty.append(glyph.name)
        if glyph.unicode is None:
            no_unicode.append(glyph.name)
        if glyph.name.endswith(SMALL_CAP_SUFFIX):
            small_caps.append(glyph.name)

    print(len(font), len(empty), len(no_unicode), len(small_caps))


main()
```

```text
208 4 4 3
```

The `print` line is scaffolding. It's ugly and it will go, but it tells you now that the collecting works, before you've spent any time on the looks. You know these four numbers from earlier chapters: 208 glyphs, four empty, four without a Unicode value, three small caps. If one of them is off, the mistake is in the thirty lines you have, and not somewhere in the forty you'll have later.

The suffix sits in a setting at the top, in capitals, like `LIMIT` in chapter 17. Another studio might name its small caps `.smcp`, and then one line changes.

## Step 3: Count what you didn't collect

Tomas asked how many glyphs have a Unicode value. The script has no list of those. Does it need a fourth list and a fourth `if`?

It doesn't. Every glyph either has a Unicode value or doesn't have one, so the two counts add up to the size of the font. You have the size and you have one of the counts. Inside `main`, indented like the lines around it, add:

```python
with_unicode = len(font) - len(no_unicode)
print(with_unicode)
```

```text
204
```

This is cheaper than a fourth list. The more important gain is that the two numbers can never disagree with each other, because one is made from the other. When a report has numbers that must add up, calculate one of them from the rest.

## Step 4: Line up the numbers

Five labels and five numbers make a small table. Chapter 12 gave you the tool: an f-string with a width for each column. Since the same pattern is needed five times, it gets a name.

```python
def line(label, count):
    print(f"{label:<18}{count:>5}")
```

Put it under `is_empty`. Then replace the scaffolding line in `main` with the real output:

```python
    print(f"Inventory of {font.info.familyName}, {date.today()}")
    print()
    line("Glyphs", len(font))
    line("Empty", len(empty))
    line("With Unicode", len(font) - len(no_unicode))
    line("Without Unicode", len(no_unicode))
    line("Small caps", len(small_caps))
```

Run it.

```text
NameError: name 'date' is not defined
```

That's the deliberate mistake of the chapter, though you may have made it for me. The heading line came from `Friday Report.py`, and the import it depends on stayed behind. When you carry lines from one script to another, look at every name in them and ask where it comes from. Add the missing line at the top, above the Fly imports:

```python
from datetime import date
```

```text
Inventory of GG Plum, 2026-11-13

Glyphs              208
Empty                 4
With Unicode        204
Without Unicode       4
Small caps            3
```

Your date will be your own. The numbers stand in a column with their last digits aligned, which is how people expect to read counts.

## Step 5: Name the glyphs

The fifth question was "which ones?". `report` from chapter 16 printed a title, a count and the names. The counts are in the table now, so the function gets simpler, and it gets two improvements.

```python
def name_list(title, names):
    if len(names) == 0:
        return
    print()
    print(f"{title}:")
    for name in sorted(names):
        print("   ", name)
```

The first improvement is the guard. A finished font has no empty glyphs, and a heading with nothing under it looks like a script that broke. If the list is empty, the function leaves early and prints nothing. The table above already says `0`.

The second is `sorted`. The lists were filled in glyph order, which is the order of the Font window. Tomas doesn't have the Font window. Alphabetical order is the one he can find things in.

Three calls at the end of `main`:

```python
    name_list("Empty", empty)
    name_list("Without Unicode", no_unicode)
    name_list("Small caps", small_caps)
```

## Step 6: Hang it in the menu

Here's the whole script.

```python
#FLM: Inventory
# Counts what is in the current font: all glyphs, empty glyphs,
# glyphs with and without a Unicode value, and small caps.
# Reads only. Changes nothing in the font.

from datetime import date

from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

SMALL_CAP_SUFFIX = ".sc"


def is_empty(font, glyph):
    return pGlyph(font, glyph).isEmpty()


def line(label, count):
    print(f"{label:<18}{count:>5}")


def name_list(title, names):
    if len(names) == 0:
        return
    print()
    print(f"{title}:")
    for name in sorted(names):
        print("   ", name)


def main():
    font = fl.CurrentFont()
    if font is None:
        print("Inventory: open a font first.")
        return

    empty = []
    no_unicode = []
    small_caps = []
    for glyph in font.glyphs:
        if is_empty(font, glyph):
            empty.append(glyph.name)
        if glyph.unicode is None:
            no_unicode.append(glyph.name)
        if glyph.name.endswith(SMALL_CAP_SUFFIX):
            small_caps.append(glyph.name)

    print(f"Inventory of {font.info.familyName}, {date.today()}")
    print()
    line("Glyphs", len(font))
    line("Empty", len(empty))
    line("With Unicode", len(font) - len(no_unicode))
    line("Without Unicode", len(no_unicode))
    line("Small caps", len(small_caps))
    name_list("Empty", empty)
    name_list("Without Unicode", no_unicode)
    name_list("Small caps", small_caps)


main()
```

Below the table, it prints:

```text
Empty:
    a.sc
    b.sc
    c.sc
    space

Without Unicode:
    .notdef
    a.sc
    b.sc
    c.sc

Small caps:
    a.sc
    b.sc
    c.sc
```

Read the output the way Tomas will. The `space` glyph is empty, and it should be: a space has a width and no drawing. The `.notdef` glyph has no Unicode value, and it shouldn't have one: it's the box a font shows for a character it doesn't have. The script can't know either of those things. It reports what it finds, and a person who knows fonts decides what's a problem. Mira writes two lines to Tomas explaining the two exceptions, which takes less time than teaching them to the script.

Use **Save Script As…** to put a copy in the `Halfmoon` folder as `Inventory.py`, choose **Scripts > Refresh Scripts**, and run **Scripts > Halfmoon > Inventory**. Then close every font and run it once more, to see the guard speak:

```text
Inventory: open a font first.
```

Mira shows Ines where the command is. Ines opens a font Mira has never seen, an old Halfmoon display face, and runs it. Sixty lines of Python count a font they weren't written for.

??? info "Going deeper: what the inventory doesn't know yet"
    The script calls a glyph a small cap when its name ends in `.sc`. That's a convention, not a fact about the drawing: a glyph named `a.sc` that holds a lowercase a would be counted all the same. It also counts a glyph as having a Unicode value without asking whether it's the right one, and it treats a glyph built entirely from other glyphs as not empty, without saying that it borrows. Lines 4 and 5 of Oskar's sheet are about that last point. Each of these is a chapter of Part 2.

## Where you are

Three weeks ago the first chapter asked you to type one line and press a button. Look at the script above. You can read every line of it and say what it does and why it's there, and you wrote most of those lines yourself, in earlier chapters, before you put them together today.

On Oskar's sheet, line 1 was crossed out in chapter 4, line 2 in chapter 8 and line 3 in chapter 12. Line 9, "list every glyph whose name ends in `.sc`", has had a pencil dot next to it since chapter 9. The inventory lists them on demand, for any font. Mira crosses it out. Seven lines are left, and every one of them asks the script to know more about a font than names, widths and Unicode values.

## What you learned

A larger script is assembled from small ones that already work: write down the questions it answers, get the numbers right with one plain `print`, and only then make the output readable. A count that can be calculated from two others should be, so that the report can't contradict itself. Lines carried from another script bring their imports and settings along as a debt, and the complaint that follows names what's missing. The script reports and the person reading decides what the numbers mean.

## Try it yourself

1. Add a line to the table for glyphs wider than 800 units, with the limit as a setting at the top, and a name list for them. On `Plum-practice` the count is 11.
2. Add a line for the widest glyph, using `widest_glyph(font)` from `Friday Report.py`. The `line` function wants a number in its second slot, so decide how to show a name and a width: write a second small function, or use a plain `print` with an f-string.
3. Make a new empty glyph by hand with **Font > New Glyph…**, name it `d.sc`, and run the inventory again. Predict all five numbers before you look. Then check your prediction against the output.

## Next

Part 2 begins with a question the loop answers slowly, "what's the width of `adieresis`?", and a new kind of container that answers it at once.
