---
this_file: src_docs/md/part4-space/078-kerning-to-a-spreadsheet.md
---

# 78. Kerning in a spreadsheet

Wednesday of week fifteen. Tobias has the proof and a pencil. What he doesn't have is FontLab, and he isn't going to get it for one job. He's asked for the kerning as a table he can open in a spreadsheet, one row for each pair and one column for each weight. He'll change the cells he disagrees with and send the file back.

Review often happens outside the font editor. Chapter 28 sent a metrics table out as a CSV file and read one back. Today kerning makes the same round trip, and the way back is the harder half: the script has to find the handful of cells that changed among three hundred, and write only those.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The helpers `ask` and `tell` from chapter 39. The scripts below write them out again, so each one runs by itself.
- The `reports` folder next to your font, from chapter 26.
- A spreadsheet program, or a text editor and some patience.
- The kerning as chapter 75 left it: 101, 104 and 102 pairs.

I couldn't run the code in FontLab 9. The file contents and counts below were produced in plain Python from Plum's source file.

## Step 1: One row for each pair

Monday's report collected every pair that any master has, with a union of sets. That collection is the table's rows. Each row has the two names and then three values, with an empty cell where a master lacks the pair:

```python
def cell(value):
    if value is None:
        return ""
    return f"{value:.0f}"


print([cell(-69.0), cell(None), cell(11.0)])
```

```text
['-69', '', '11']
```

The values come from FontLab as floats, and `:.0f` writes them without the `.0` that would make Tobias wonder whether halves are allowed.

A row is a list, as chapter 28 said, and lists can be joined with a plus sign:

```python
MASTERS = ["Light", "Regular", "Bold"]
print(["First", "Second"] + MASTERS)
```

```text
['First', 'Second', 'Light', 'Regular', 'Bold']
```

That's the heading row. The rows under it are built the same way: two names, plus a comprehension that asks each master for the pair with `get`. The whole of the writing is in the script below, in `write_table`. Run it with `MODE = "out"` and it should say:

```text
104 rows written to plum-kerning.csv
```

Open the file in a text editor before you open it in a spreadsheet. The first lines should be:

```text
First,Second,Light,Regular,Bold
@L_A,@R_C,-32,-13,-32
@L_A,@R_O2,-32,-7,-32
@L_A,@R_U2,-18,-20,-18
```

## Step 2: Be Tobias

You have no Tobias, so you'll have to do his part. Open `plum-kerning.csv` in a spreadsheet and make these ten changes. They're the loose ends that the last four chapters collected on Mira's list, with the values he chose from the proof:

| First | Second | Column | Was | Becomes |
| --- | --- | --- | --- | --- |
| `@L_A` | `@R_O2` | Regular | −7 | −24 |
| `@L_A` | `Q` | Regular | −7 | −20 |
| `@L_O` | `@R_A2` | Regular | −7 | −20 |
| `L` | `T` | Regular | −113 | −70 |
| `P` | `@R_aacute` | Regular | −10 | empty |
| `P` | `a` | Regular | −10 | empty |
| `Q` | `@R_A2` | Regular | −7 | −20 |
| `T` | `@R_wacute` | Bold | −94 | −60 |
| `T` | `w` | Bold | −105 | −60 |
| `questiondown` | `exclamdown` | Light | empty | 8 |

Save the result as CSV under a new name, `plum-kerning-tobias.csv`, in the same folder. Keep the file you sent. When a correction looks odd next week, you'll want to see what the cell said before.

A warning about spreadsheets. Some of them see a cell that begins with `@` and take it for a formula. If yours complains about the first column, import the file with that column set to text.

## Step 3: Read it back, and count

Reading a CSV is chapter 28's `csv.reader`, which gives each row as a list of strings. Compare each cell with the font, and collect the ones that differ:

```python
changes = []
for row in rows[1:]:
    if not row:
        continue
    first, second = row[0], row[1]
    for master, text in zip(MASTERS, row[2:]):
        if text != tables[master].get((first, second)):
            changes.append((master, first, second, text))
print(len(changes))
```

`rows[1:]` skips the heading. `zip` is from chapter 35: it walks two lists side by side, here the three master names and the three cells after the names.

```text
312
```

Three hundred and twelve changes, where Tobias made ten. 104 rows of three cells is 312: every cell in the file differs from the font.

You've been here before. A file holds text. The cell says `"-32"`, a string, and the font says `-32.0`, a number, and a string is never equal to a number, whatever they look like when printed. The empty cell is `""` and the font's answer for a missing pair is `None`, and those aren't equal either.

Had the script gone on to write its "changes", it would have handed 312 strings to `write_kerning`. As far as I can read its source, that function refuses anything that isn't a whole number, so the font would have been safe. The count is still what told you, before any write: when a plan is thirty times bigger than you expected, stop and find out why.

## Step 4: Turn a cell into a value

Each cell has to become what the font would hold: a whole number, or `None` for an empty cell. Fly has a function made for this cell:

```python
import fly.ap.kerning.edit.model as kerning_edit

print([kerning_edit.parse_cell("-32"), kerning_edit.parse_cell(""), kerning_edit.parse_cell(" 8 ")])
print(kerning_edit.parse_cell("−70"))
```

```text
[-32, None, 8]
-70
```

It strips spaces, reads the number, and returns `None` for an empty cell. The second line shows a courtesy you'd not have thought of until it bit you. Some spreadsheets and some careful typists write a true minus sign, `−`, where a keyboard gives a hyphen, `-`. To a person they're the same. To Python's `float` the first is not a number at all. `parse_cell` accepts both.

And `-32 == -32.0` is true: a whole number and a float with the same value are equal. So the parsed cell can be compared with the font's value directly.

What if a cell holds `?` or `ask Mira`? `parse_cell` raises a `ValueError`, as `float` did in chapter 68. Tobias is a person with a pencil, so the script should expect it: catch the error with chapter 19's `try`, note the row and the text, and go on to the next cell. One bad cell shouldn't hide the nine good ones, and it shouldn't be written either.

## The whole script

```python
#FLM: Kerning CSV
# MODE "out" writes every kerning pair to a CSV table, one column per master.
# MODE "in" reads an edited copy and writes only the cells that changed.
import csv
from pathlib import Path

import fly.ap.core.scripting as scripting
import fly.ap.kerning.batch as kerning_batch
import fly.ap.kerning.edit.model as kerning_edit
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"

MASTERS = ["Light", "Regular", "Bold"]
MODE = "out"
OUT_NAME = "plum-kerning.csv"
IN_NAME = "plum-kerning-tobias.csv"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes


def cell(value):
    if value is None:
        return ""
    return f"{value:.0f}"


def write_table(tables, address):
    everything = set()
    for master in MASTERS:
        everything = everything | set(tables[master])
    with open(address, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["First", "Second"] + MASTERS)
        for first, second in sorted(everything):
            values = [cell(tables[master].get((first, second))) for master in MASTERS]
            writer.writerow([first, second] + values)
    return len(everything)


def read_changes(tables, address):
    with open(address, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    changes = []
    problems = []
    for number, row in enumerate(rows[1:], 2):
        if not row:
            continue
        first, second = row[0], row[1]
        for master, text in zip(MASTERS, row[2:]):
            try:
                new = kerning_edit.parse_cell(text)
            except ValueError:
                problems.append((number, master, text))
                continue
            old = tables[master].get((first, second))
            if new != old:
                changes.append((master, first, second, old, new))
    return changes, problems


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    tables = {master: scripting.kerning_pairs(package, master) for master in MASTERS}
    folder = Path(font.path).parent / "reports"

    if MODE == "out":
        count = write_table(tables, folder / OUT_NAME)
        print(f"{count} rows written to {OUT_NAME}")
        return

    changes, problems = read_changes(tables, folder / IN_NAME)
    for master, first, second, old, new in changes:
        print(f"{master:<9}{first:<14}{second:<12}{cell(old):>5} ->{cell(new):>5}")
    print(f"{len(changes)} cells differ from the font.")
    for number, master, text in problems:
        print(f"row {number}, {master}: can't read {text!r}")
    if problems or not changes:
        return
    if not ask(f"Write {len(changes)} kerning values?"):
        return

    edits = {}
    for master, first, second, old, new in changes:
        if master not in edits:
            edits[master] = {}
        edits[master][(first, second)] = new
    kerning_batch.write_kerning(package, edits, "Kerning from CSV")
    tables = {master: scripting.kerning_pairs(package, master) for master in MASTERS}
    changes, problems = read_changes(tables, folder / IN_NAME)
    print(f"Done. {len(changes)} cells differ from the font.")


main()
```

Save it as `kerning_csv.py`. Change `MODE` to `"in"` and run it:

```text
Regular  @L_A          @R_O2          -7 ->  -24
Regular  @L_A          Q              -7 ->  -20
Regular  @L_O          @R_A2          -7 ->  -20
Regular  L             T            -113 ->  -70
Regular  P             @R_aacute     -10 ->
Regular  P             a             -10 ->
Regular  Q             @R_A2          -7 ->  -20
Bold     T             @R_wacute     -94 ->  -60
Bold     T             w            -105 ->  -60
Light    questiondown  exclamdown        ->    8
10 cells differ from the font.
```

Ten, and they're the ten in the table above. Click Yes:

```text
Done. 0 cells differ from the font.
```

All three masters now have 102 pairs, and the same 102. Run Monday's `orphan_pairs.py` and its last line should read `102 different pairs, 0 not in every master.` One Undo should take all ten back. I haven't seen it in FontLab 9.

Notes on the listing.

`enumerate(rows[1:], 2)` numbers the rows from 2, because that's the number the spreadsheet shows beside the first row under the heading. A message that says "row 37" should mean the row 37 Tobias sees.

`{text!r}` in an f-string prints the text with its quotes, as `repr` would. For a cell with a stray space or nothing in it, the quotes are what let you see the problem.

`if problems or not changes: return` stops in two cases. If any cell couldn't be read, nothing is written until a person has looked at it. A half-applied review is hard to reason about afterwards.

`cell` serves both directions. It formats values for the file and for the report, so an empty old or new value prints as a gap.

An empty cell under a pair that exists means "remove this pair", through the `None` order of chapter 73. That's the right meaning for a kerning table and a dangerous one for a careless reviewer, which is one more reason the script prints every change and asks.

The same check as on Friday closes the run: read the font again, compare again, and print the count.

## What the round trip settled

Mira's list from the last four chapters is empty. The `L T` of the Regular no longer sits apart from its neighbors. The four `A` and `O` pairs of the Regular are in line with the other weights. The two `P` pairs are gone, and the Spanish question mark has its pair in the Light.

Two of Tobias's values are in the Bold, and both pull its kerning back. He wrote one more line at the bottom of the printout, in pencil: "Bold: all of it feels a notch too strong. Not pair by pair." That was Mira's own note of last Thursday, and it's tomorrow's chapter.

## What you learned

A kerning table for review has one row for each pair that any master holds, and an empty cell where a master lacks it. What comes back from a file is text: `"-32"` is not `-32.0`, and `""` is not `None`. `kerning_edit.parse_cell` turns a cell into a whole number or `None`, and you collect only the cells that differ from the font. If the count of changes is far from what you expect, or a cell can't be read, stop before writing.

## Try it yourself

1. In your copy of Tobias's file, put `?` in one cell and run the script with `MODE = "in"`. Read the message. Then put the old value back.
2. Add a column `Note` at the end of the table when writing, empty for every row. Does `read_changes` still work on a file with that column? Work out why from what `zip` does when one list is longer than the other.
3. Write the table with the rows sorted by the Regular's value, deepest first, and pairs the Regular lacks at the end. You'll need a key function that returns a tuple, and a decision about what a missing value sorts as.

## Next

"All of it a notch too strong." Chapter 79 turns the whole of the Bold's kerning down by a percentage, in one step, and looks hard at what rounding does to small pairs on the way.
