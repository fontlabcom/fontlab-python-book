---
this_file: src_docs/md/part2-a-toolbox/035-lists-of-lists.md
---

# 35. Rows

Thursday. Yesterday's function told Mira that `M` and `W` are wider than 700 units. This morning that isn't enough. She's spacing, and a spacer wants to see three numbers for every glyph: how much white is on its left, how wide it is in all, and how much white is on its right. She wants them side by side, for six glyphs at once, so that she can compare the `n` with the `o` and the `H` with the `O`.

That's a table, with one line per glyph and the same kinds of things in each line. You built a table in chapter 28 and sent it straight to a file, row by row, without keeping it. In chapter 30 you kept a small one, the list of rename pairs, without looking hard at its shape. Today you keep it, because in the next chapter you'll want to sort it, and you can't sort what you've already printed.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `halfmoon.py` as [chapter 34](034-arguments-with-defaults.md) left it.
- Six glyphs selected in the Font window: `H`, `O`, `A`, `n`, `o` and `v`.

## Step 1: The white on each side

A glyph sits in a box as wide as its advance width. The black shape doesn't touch the edges of the box. The gap between the left edge and the leftmost point of the shape is the left sidebearing. The gap on the other side is the right sidebearing. When two glyphs stand next to each other, the right sidebearing of the first and the left sidebearing of the second add up to the white between them. Spacing a font is, for the most part, choosing those two numbers for every glyph.

The rich glyph from chapter 14 knows both. Ask it about the `n`:

```python
from fly import fl
import halfmoon

font = fl.CurrentFont()
glyph = font["n"]
rich = halfmoon.rich(font, glyph)
print(rich.getLSB(), glyph.width, rich.getRSB())
```

```text
70 523.0 66
```

LSB and RSB are the left and right sidebearings, and `getLSB()` and `getRSB()` ask for them. Type people shorten the words that way all day, so the names are worth knowing. The `n` has 70 units of white on its left, 66 on its right, and 523 in all. The black part must be 387 units wide, since the three have to add up.

I worked these numbers out from the font file. If FontLab gives you a unit more or less, trust FontLab.

The sidebearings come back as whole numbers and the width with `.0` after it. Use `int(glyph.width)` from chapter 11 so that they match.

## Step 2: A list is a row

Put the four facts about the `n` into one list:

```python
row = [glyph.name, rich.getLSB(), int(glyph.width), rich.getRSB()]
print(row)
```

```text
['n', 70, 523, 66]
```

A list doesn't have to hold things of one kind. This one holds a string and three numbers, and it's one line of Mira's table. In chapter 30 you made small lists of two, `[old, new]`, and kept a list of them. It's the same idea here with four.

Now do it for every selected glyph, and keep the rows in a list of their own:

```python
rows = []
for glyph in halfmoon.glyphs_of(font, only_selected=True):
    rich = halfmoon.rich(font, glyph)
    rows.append([glyph.name, rich.getLSB(), int(glyph.width), rich.getRSB()])

print(rows)
```

```text
[['H', 76, 672, 70], ['O', 36, 708, 36], ['A', 13, 596, 11], ['n', 70, 523, 66], ['o', 38, 520, 38], ['v', 8, 455, 3]]
```

Your rows may come in a different order, depending on how you selected the cells. Your numbers may differ from mine by a unit, too. I worked mine out from the font's source file.

Count the brackets at the start: two. The outer pair is the table and each inner pair is a row. A list of lists is the simplest way Python has to hold a table, and you'll meet it wherever data has rows.

## Step 3: Two numbers to find a cell

One number in brackets picks a row. A second picks a cell in it:

```python
print(rows[0])
print(rows[0][2])
print(rows[3][0])
```

```text
['H', 76, 672, 70]
672
n
```

Read `rows[0][2]` from left to right. `rows[0]` is the first row, which is itself a list. Then `[2]` asks that list for its third item. It's a street and a house number.

It works, and it reads badly. Nothing about `[2]` says "width". If you write `row[1]` when you meant `row[3]`, the script gives you a left sidebearing where you wanted a right one, and no error will ever tell you. The next step is the cure.

## Step 4: Unpack

You've written loops like this since chapter 30 without my explaining them properly:

```python
for name, lsb, width, rsb in rows:
    print(f"{name:<6}{lsb:>5}{width:>6}{rsb:>5}")
```

```text
H        76   672   70
O        36   708   36
A        13   596   11
n        70   523   66
o        38   520   38
v         8   455    3
```

Each time around, the loop takes one row and deals its four items into four boxes, in order. That's called **unpacking**. It isn't special to loops. It works anywhere there's an equals sign:

```python
name, lsb, width, rsb = rows[3]
print(name, width)
```

```text
n 523
```

Four names on the left, a row of four on the right, and each name gets its item. After that line you never write `[2]` again. You write `width`.

That's the table Mira wanted, and it's worth a look as a type designer and not only as a programmer. The `O` and the `o` have the same white on both sides, as round letters should. The `n` has more on its left, where the straight stem is, than on its right, where the arch is. The `A` and the `v` have almost none, because their diagonals make their own white. And the `H` has 76 on one side and 70 on the other, which a symmetrical letter shouldn't. Mira writes that down.

Now the mistake. Suppose you decide the table doesn't need the right sidebearing and take `rsb` out of the loop line, but leave the rows as they are:

```python
for name, lsb, width in rows:
    print(name, lsb, width)
```

```text
ValueError: too many values to unpack (expected 3)
```

Python had four items and three boxes, and it won't throw one away without being told. The other way around, with five names and four items, reads:

```text
ValueError: not enough values to unpack (expected 5, got 4)
```

The count is checked every time, so a row that's the wrong shape stops the script. A wrong index number would have gone on quietly and printed nonsense.

## Step 5: Rows that can't be changed

There's a second kind of row. Write it with parentheses where the list has square brackets:

```python
row = ("n", 70, 523, 66)
print(row[2])
name, lsb, width, rsb = row
print(name, width)
```

```text
523
n 523
```

It's called a **tuple**, and so far it behaves like a list. You can index it, loop over it, unpack it and ask its `len`. The difference shows when you try to change it:

```python
row[1] = 75
```

```text
TypeError: 'tuple' object does not support item assignment
```

A tuple is fixed once it's made. You can't replace an item, and there's no `append`.

Why have the weaker one? Think of a row as a record of a measurement. The `n` measured 70, 523 and 66 at ten o'clock this morning. A script further down that changes the 70 by accident has spoiled the record, and with a tuple that accident is an error message, where with a list it would be a silent wrong number in a report. The table itself is another matter. It grows as you add rows, so it has to be a list.

By habit, people use a list for a collection that grows and shrinks, with items of one kind, and a tuple for a record with a fixed number of fields. A list of tuples is a table.

You've held tuples already. The plan rows in chapter 30 were tuples of `(old, new, status)`, and `tally.items()` in chapter 22 handed you pairs that were tuples too. When Python prints parentheses around a row, that's what you're looking at.

## Step 6: Zip two lists together

Sometimes the columns arrive separately. Tomas sends two lists by message, some glyph names and the widths the publisher's old font had for them:

```python
names = ["H", "O", "A"]
old_widths = [680, 700, 600]
```

To compare them with Plum you need them as rows. `zip` takes two lists and pairs their items off, first with first, second with second, the way the two sides of a zipper meet:

```python
for name, old in zip(names, old_widths):
    now = int(font[name].width)
    print(f"{name:<4}{old:>5}{now:>5}{now - old:>5}")
```

```text
H     680  672   -8
O     700  708    8
A     600  596   -4
```

`zip` hands you tuples of two, and the loop unpacks them. If you want the pairs as a table you can keep, wrap it in `list`:

```python
print(list(zip(names, old_widths)))
```

```text
[('H', 680), ('O', 700), ('A', 600)]
```

One thing to know about `zip`: if the lists are of different lengths, it stops at the end of the shorter one and says nothing. Three names and two widths give two pairs, and the third name is dropped. When the two lists come from somebody else, compare their `len` first.

## The whole script

The row-making belongs in the module, because the next three chapters will use it. Add this to `halfmoon.py`:

```python
def metrics_rows(font, only_selected=False):
    rows = []
    for glyph in glyphs_of(font, only_selected):
        if not is_empty(font, glyph):
            measured = rich(font, glyph)
            rows.append((glyph.name, measured.getLSB(), int(glyph.width), measured.getRSB()))
    return rows
```

There are two things to notice in it. Each row is a tuple, so there are double parentheses in the `append` line: the outer pair belongs to `append` and the inner pair makes the tuple. And empty glyphs are left out by the `if not is_empty` test. A space has a width, but with no shape in it there's no leftmost point to measure a sidebearing from, and I'd sooner leave the row out than print a number that means nothing.

Then `metrics_rows.py` is short:

```python
# Prints left sidebearing, width and right sidebearing
# for the glyphs selected in the Font window.
from fly import fl
import halfmoon

font = fl.CurrentFont()
rows = halfmoon.metrics_rows(font, only_selected=True)

if not rows:
    print("Select some glyphs with shapes in them first.")
else:
    print(f"{'glyph':<8}{'LSB':>5}{'width':>7}{'RSB':>5}")
    for name, lsb, width, rsb in rows:
        print(f"{name:<8}{lsb:>5}{width:>7}{rsb:>5}")
```

```text
glyph     LSB  width  RSB
H          76    672   70
O          36    708   36
A          13    596   11
n          70    523   66
o          38    520   38
v           8    455    3
```

`if not rows:` is the truthiness rule from chapter 31 at work. An empty list counts as no, so the line reads "if there are no rows".

Mira prints the table for all the capitals, finds two more with lopsided sidebearings and fixes them by hand before lunch. Then she asks for the obvious next thing, which is the table with the widest glyph at the top.

## What you learned

A table is a list of rows, and a row is a small list or tuple with the same fields in the same order every time. Unpack a row into named boxes in place of using index numbers, and Python will check the count for you. A tuple is a row that can't be changed after it's made, which suits a record. `zip` pairs off two lists into rows and stops without warning at the end of the shorter one.

## Try it yourself

1. Add a fifth field to each row in `metrics_rows`: the width of the black part, which is the width minus both sidebearings. Which other lines, in which files, have to change? Run `metrics_rows.py` before you fix them and read the error.
2. Print only the rows whose two sidebearings differ by more than 4 units. For the six glyphs in this chapter that should leave one or two rows. `abs()` turns a negative number into a positive one, so `abs(lsb - rsb)` is the size of the difference whichever side is bigger.
3. Send the rows to a CSV file with the writer from chapter 28, with a header row. Then open the file in a spreadsheet. A writer takes a tuple as happily as a list.

## Next

The table comes out in whatever order the glyphs were selected. Chapter 36 sorts it by any column you like.
