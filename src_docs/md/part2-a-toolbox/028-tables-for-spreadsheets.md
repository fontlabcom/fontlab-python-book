---
this_file: src_docs/md/part2-a-toolbox/028-tables-for-spreadsheets.md
---

# 28. Tables for spreadsheets

Tuesday. Tomas, who keeps the publisher's spreadsheet, has been patient since chapter 6. Every week Mira sends him the width report, and every week he pastes it into a sheet and gets all of it in column A: name and width in one cell, 208 times. Then he splits the cells by hand.

Today he writes: *Could you send it as CSV? Then it opens in columns by itself.*

Mira doesn't know what CSV is. She does know how to write a file, as of Friday. That's most of it.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- The `reports` folder next to your font, which the Friday report made in [chapter 26](026-write-it-to-a-file.md).
- A spreadsheet program to open the result: Numbers, Excel, LibreOffice or Google Sheets.

## Step 1: Commas between the cells

CSV stands for comma-separated values, and it's as plain as it sounds. A CSV file is a text file. Each line is one row of the table. Inside a line, commas mark where one cell stops and the next starts. This is a table of three rows and three columns:

```text
Glyph,Unicode,Width
A,U+0041,596
n,U+006E,523
```

Every spreadsheet program opens such a file and puts each piece in its own cell. That's all Tomas is asking for.

You could build such a line yourself. Chapter 25 used `" ".join(...)` to glue a list of strings together with spaces. Glue with a comma and you have a row:

```python
row = ["A", "U+0041", "596"]
print(",".join(row))
```

```text
A,U+0041,596
```

Now put a real width in the list, a number and not a string:

```python
row = ["A", "U+0041", 596]
print(",".join(row))
```

```text
TypeError: sequence item 2: expected str instance, int found
```

`join` glues strings and nothing else. "Sequence item 2" is the third thing in the list, since counting starts at zero, and it's an `int`. You'd have to turn every number into text first. That's a chore, but it's not the real problem. The real problem is in the next step.

## Step 2: The comma that breaks the table

Tomas's sheet has a notes column. Suppose one note reads `wide, check`. Glue it in:

```python
row = ["W", "859", "wide, check"]
print(",".join(row))
```

```text
W,859,wide, check
```

Count the commas. Three commas make four cells. The spreadsheet will put `wide` in the third column and ` check` in a fourth, and every row with such a note will be one cell longer than the rest. The comma inside the note looks, to the spreadsheet, like any other comma.

CSV has a fix for this: a cell that holds a comma goes inside double quotes. Then a cell that holds a double quote needs a fix of its own. There are a few more such rules, and they're tedious to get right by hand.

So don't write CSV by hand. Python ships with a module, which is a file of ready-made Python, that knows the rules.

## Step 3: Let the csv module write the row

```python
import csv
from pathlib import Path

from fly import fl

font = fl.CurrentFont()
table_file = Path(font.path).parent / "reports" / "test.csv"

with open(table_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Glyph", "Width", "Note"])
    writer.writerow(["W", 859, "wide, check"])

print("Saved", table_file)
```

Open `test.csv` in a plain text editor first, not in the spreadsheet. You want to see what was written:

```text
Glyph,Width,Note
W,859,"wide, check"
```

The note got its quotes, and you didn't put them there. The number 859 went in without complaint and without you turning it into text. Now open the same file in your spreadsheet program. Two rows, three columns, and the note in one cell with its comma.

Three new things are in that listing.

`csv.writer(f)` takes the open file and hands back a writer. Think of it as a clerk who sits between you and the file. You give the clerk rows. The clerk knows where commas and quotes go, and writes the line.

`writer.writerow([...])` hands over one row. A row is a list, one item for each cell. You don't write `\n` and you don't use `print`. The clerk ends the line.

`newline=""` in the `open` call is a magic line, and I'll say so plainly. The clerk writes its own line endings, and without `newline=""` Python on Windows adds a second one, which shows up in the spreadsheet as a blank row after every row. On a Mac you'd never notice the difference. Type it anyway, every time you open a file for the `csv` module, and your tables will open properly on Tomas's machine as well as yours.

## Step 4: A row is a list

Here's the mistake nearly everybody makes once. Hand the clerk a bare string where it expects a list:

```python
    writer.writerow("Aacute")
```

No error. Look in the file:

```text
A,a,c,u,t,e
```

Six cells, one letter in each. You know why if you think back to chapter 9: a string is a row of characters, and a `for` loop will walk through it letter by letter. The clerk asked for a row of things, got a string and took each letter for a cell. For a row with one cell, you still need the square brackets: `writer.writerow(["Aacute"])`.

Hand it a bare number and the clerk does complain, because a number isn't a row of anything:

```python
    writer.writerow(596)
```

```text
_csv.Error: iterable expected, not int
```

The `_csv.` in front is the module's own name for itself.

"Iterable" is Python's word for anything a `for` loop can walk through: a list, a string, a set, a dictionary, an open file. You'll see the word in error messages from now on. When you do, read it as "something I can go through one at a time", and check whether you forgot the brackets.

## Step 5: The whole font as a table

Now the real table. One row for the headings, then one row for each glyph. This is the loop from chapter 7 with `writerow` where `print` was:

```python
table_file = Path(font.path).parent / "reports" / "plum-metrics.csv"

with open(table_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Glyph", "Unicode", "Width"])
    for glyph in font.glyphs:
        writer.writerow([glyph.name, glyph.unicode, glyph.width])

print("Saved", table_file)
```

The first lines of the file:

```text
Glyph,Unicode,Width
.notdef,,500.0
A,65,596.0
Aacute,193,596.0
Abreve,258,596.0
```

It works, and Tomas would find two flaws in a minute. First, something that looks like a flaw and isn't.

Look at `.notdef`. Between its two commas there's nothing. Its Unicode value is `None`, and the clerk writes `None` as an empty cell. That's the right thing to do, and it's one decision you don't have to make.

The Unicode values are plain numbers, 65 and 193. Tomas and the proofreader think in the `U+0041` form, and you built that in chapter 23 with `f"U+{number:04X}"`. But that format falls over on `None`, as you also saw in chapter 23, so the `.notdef` row needs an `if`.

And the widths carry their `.0`. Chapter 11 dealt with that: `round(glyph.width)` gives a whole number.

Build each cell in a box of its own before you make the row. It's three more lines and far easier to read:

```python
    for glyph in font.glyphs:
        if glyph.unicode is None:
            code = ""
        else:
            code = f"U+{glyph.unicode:04X}"
        width = round(glyph.width)
        writer.writerow([glyph.name, code, width])
```

```text
Glyph,Unicode,Width
.notdef,,500
A,U+0041,596
Aacute,U+00C1,596
Abreve,U+0102,596
```

There's a reason beyond taste for the `U+` in front. A spreadsheet tries to be helpful with anything that looks like a number. Give it a bare `0041` and it may store 41 and throw the zeros away. Give it `00E9` and it may decide that's zero in scientific notation. `U+0041` doesn't look like a number to any spreadsheet, so it's left alone.

## Step 6: Read it back

A file your script wrote should be a file your script can read. The module has a reader to match the writer:

```python
with open(table_file, encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

```text
['Glyph', 'Unicode', 'Width']
['.notdef', '', '500']
['A', 'U+0041', '596']
['Aacute', 'U+00C1', '596']
```

And so on for all 209 lines. You loop over the reader as you looped over the file in chapter 27, but each turn gives you a list of cells and not a raw line. No `strip`, no splitting at commas, and a note with a comma in it comes back as one cell.

Look at the widths. They went out as the number `596`. They've come back as the string `'596'`, in quotes. The empty cell came back as `''` and not as `None`. A CSV file is text and nothing but text. It can't remember what was a number. If you read a table and want to do arithmetic with a column, you turn each cell back into a number yourself with `int(...)`, as you did with `int("00E9", 16)` in chapter 23. And you skip the heading row first, because `int("Width")` is an error.

Mira sends `plum-metrics.csv`. Tomas opens it, gets three columns, and sorts by width before he's finished reading her message. He writes back that `emdash` is 1000 units wide and asks whether that's a mistake. It isn't. An em dash is as wide as the em, and Plum's em is 1,000 units. But it's the first time the publisher's spreadsheet person has asked a question about the design.

## The whole script

Save this as `metrics_csv.py`:

```python
# Writes one row per glyph to reports/plum-metrics.csv next to the font.
import csv
from pathlib import Path

from fly import fl

font = fl.CurrentFont()
reports = Path(font.path).parent / "reports"
reports.mkdir(exist_ok=True)
table_file = reports / "plum-metrics.csv"

with open(table_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Glyph", "Unicode", "Width"])
    for glyph in font.glyphs:
        if glyph.unicode is None:
            code = ""
        else:
            code = f"U+{glyph.unicode:04X}"
        width = round(glyph.width)
        writer.writerow([glyph.name, code, width])

print("Saved", table_file)
```

??? info "Going deeper: semicolons, tabs and Excel"
    In countries that write decimal numbers with a comma, some spreadsheet programs expect a semicolon between cells. If Tomas's copy of Excel shows everything in one column, that's why. The writer takes a second argument for it: `csv.writer(f, delimiter=";")`. For a tab between cells, use `delimiter="\t"`. And if accented names look wrong in an older Excel, open the file with `encoding="utf-8-sig"`, which adds a mark at the start of the file that Excel looks for.

## What you learned

A CSV file is text with one row to a line and commas between the cells, and the `csv` module writes and reads it so that you never place a comma or a quote yourself. `csv.writer(f).writerow([...])` takes a list and writes a row. `csv.reader(f)` gives the rows back as lists of strings. Open the file with `newline=""` both ways, and remember that everything read from a CSV is text until you turn it into a number.

## Try it yourself

1. Add a fourth column, `Letter`, that holds the character itself: `A`, `Á`, `n`. You have `chr` from chapter 23. What goes in that cell for `.notdef`? Open the result in your spreadsheet and look at the row for `comma`. Then look at the same row in a text editor.
2. Read `plum-metrics.csv` back and add up the `Width` column. Skip the heading row. For Plum with the three small caps left out, the total of the Regular widths is 102107. What do your three empty small caps add?
3. Tomas sends a CSV with two columns, `Glyph` and `Note`. Make one by hand with five rows, and put a comma in one of the notes. Write a script that reads it and prints, for each row, the glyph name, its width from the font and the note.

## Next

Every script so far has only asked the font questions, or painted a mark on a cell. In chapter 29 a script changes Mira's real work, and she wants to be sure she can take it back.
