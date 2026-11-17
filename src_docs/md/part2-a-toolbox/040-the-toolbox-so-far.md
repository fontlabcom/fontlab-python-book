---
this_file: src_docs/md/part2-a-toolbox/040-the-toolbox-so-far.md
---

# 40. The toolbox so far

Friday of the seventh week, four in the afternoon. Ines has a pad of paper and a question she asks about everything the studio spends time on: what did it buy?

Mira has an answer ready, and it's a list. Before she reads it out, though, there's one debt left from chapter 27. Back then Ines asked whether a script could make the seven missing small-cap glyphs, and I said that changing a font takes care, and the care started in chapter 29. You've had eleven chapters of it since. Today you'll write that script.

There's almost no new Python in this chapter: one conversion, `tuple(...)`, which turns a list into a tuple. As at the end of Part 1, the work is putting together things you know. This one script uses a file from chapter 27, a set from chapter 25, a comprehension from chapter 37, a question from chapter 39 and the safety habits of chapters 29 to 31. If you can follow it, you've got Part 2.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open in the Font window.
- `halfmoon.py` as [chapter 39](039-ask-the-user.md) left it.
- `smallcaps.txt` from chapter 27, in your `scripting-book` folder.
- Save the font before you start. This script adds glyphs.

## Step 1: Move the reader into the module

In chapter 27 you wrote the lines that read a list of names from a file: open it, strip each line, and skip blanks and the lines that start with `#`. A second script needs them now, and the rule from chapter 33 says what to do. Put it in `halfmoon.py`:

```python
def read_names(path):
    names = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            name = line.strip()
            if name and not name.startswith("#"):
                names.append(name)
    return names
```

The test `if name and not name.startswith("#")` reads "if there's anything left and it isn't a note". An empty string counts as false, as chapter 31 said, so the blank lines drop out.

I haven't folded this into a comprehension. You could, but the line needs a box, `name`, to hold the stripped text that's used twice. Chapter 37's rule says that's a job for a loop.

## Step 2: Work out what's missing

Start the new script. Call it `add_from_list.py` for now.

```python
from pathlib import Path
from fly import fl
import halfmoon

font = fl.CurrentFont()
wanted = halfmoon.read_names(Path(font.path).parent / "smallcaps.txt")

have = {glyph.name for glyph in font.glyphs}
to_make = [name for name in wanted if name not in have]

print(len(wanted), "wanted,", len(to_make), "to make:")
print(" ".join(to_make))
```

```text
10 wanted, 7 to make:
d.sc e.sc f.sc g.sc h.sc zero.sc one.sc
```

There are two comprehensions here, and each does one job. `have` is a set of every name in the font. I made it a set because the only thing we'll ask of it is "is this name in there?", and chapter 25 showed that a set answers that fastest. `to_make` is a list and not a set, because the order of the art director's file is worth keeping: the glyphs will be added in the order she wrote them.

If you did exercise 3 of chapter 20 and made a `d.sc`, you'll see six to make. The script has noticed that it's there.

## Step 3: Describe the new glyphs

Fly has a helper that adds glyphs the way FontLab's own **Font > New Glyph…** command does, so that each one can be undone. It doesn't take bare names. It wants a small description of each glyph: its name and, for every master, the advance width the empty glyph should start with.

```python
from fly.ap.glyphs.creation import NewGlyph, create_glyphs

MASTERS = ["Light", "Regular", "Bold"]
WIDTH = 500

layers = tuple([(master, WIDTH) for master in MASTERS])
print(layers)

specs = [NewGlyph(name, layers) for name in to_make]
print(len(specs))
```

```text
(('Light', 500), ('Regular', 500), ('Bold', 500))
7
```

`layers` is a tuple of pairs, one pair for each master: the master's name and a width. It's the rows-of-fields shape from chapter 35. The helper asks for a tuple here and not a list, so `tuple(...)` converts one.

`NewGlyph(name, layers)` makes one description. It's a filled-in form that says "a glyph called `d.sc`, 500 units wide in each of three masters", and nothing has been added to the font yet. The second comprehension fills in seven forms.

I've typed the three master names as a constant. That's honest for now, since this is Plum and Plum has those three, but a script that only works on one font isn't finished. Part 6 shows you how to ask a font for its masters. The width of 500 is a placeholder too. Mira will set real widths when she draws the glyphs.

## Step 4: Hand the forms over

The call that does the work needs four things: the font in the form FontLab's history knows it, the list of forms, a title, and a fresh set of facts for the safety checks. You met the first and the last in chapter 29.

```python
import fly.ap.core.scripting as scripting
import fly.ap.core.history.glyphs as history

package = scripting.current_package()
facts = history.scan_auto_facts(package)

made = create_glyphs(package, specs, "Add glyphs from list", facts)
print(len(made.glyphs), "glyphs added")
```

Before you run it, open `smallcaps.txt` and add `d.sc` a second time at the bottom, as you did with `a.sc` in exercise 1 of chapter 27. Now run the script.

```text
ValueError: Refused: d.sc is listed twice.
```

The traceback above that line runs through a file called `creation.py`. Chapter 38 told you what to do with it: the last line is a refusal that somebody wrote on purpose, and the last step of the trail that's yours is the `create_glyphs` line. The helper looked through all the forms before it touched the font, found the same name twice, and stopped. Look at the Font window. Nothing has been added, including the six glyphs that were fine. It's the all-or-nothing rule from chapter 31, and here the helper enforces it for you.

You could fix the file. But the art director's files will always have such things in them, and the right place to cope is the reader. In `halfmoon.py`, change one line of `read_names`:

```python
            if name and not name.startswith("#") and name not in names:
                names.append(name)
```

Now a name that's already in the list is skipped. Reload the module and run the script again.

```text
7 glyphs added
```

Scroll to the end of the Font window. There should be seven new empty cells, `d.sc` to `one.sc`, in the order of the file. In chapter 29 one run was one Undo step. This helper is different. Fly's source says it records each new glyph as its own step, so taking all seven back means seven undos. I haven't watched it do so. The quick way back is **File > Revert Font**, and that's why you saved first.

The helper refuses in two other cases that you should know about. If any name in the list already exists in the font, it says `Refused: a.sc exists now. Check the list again.` Our script can't trip that one, because `to_make` leaves those names out. And if you run the script while a Glyph window is the active window, it asks you to switch to the Font window first, for the same reason as in chapter 29.

## The whole script

Wrap it in `main`, add the guards and the questions, and give it a menu name:

```python
#FLM: Add Glyphs From List
# Adds an empty glyph for every name in a text file
# that the current font doesn't have yet.
from pathlib import Path
from fly import fl
import fly.ap.core.scripting as scripting
import fly.ap.core.history.glyphs as history
from fly.ap.glyphs.creation import NewGlyph, create_glyphs
import halfmoon

MASTERS = ["Light", "Regular", "Bold"]
WIDTH = 500


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return

    folder = Path(font.path).parent if font.path else ""
    path = halfmoon.choose_text_file("Choose a glyph list", folder)
    if path is None:
        return

    wanted = halfmoon.read_names(path)
    have = {glyph.name for glyph in font.glyphs}
    to_make = [name for name in wanted if name not in have]
    if not to_make:
        halfmoon.tell(f"All {len(wanted)} glyphs in the list are in the font already.")
        return

    print(f"{len(wanted)} wanted, {len(to_make)} to make:")
    print(" ".join(to_make))
    if not halfmoon.ask(f"Add {len(to_make)} empty glyphs, {WIDTH} units wide?"):
        return

    layers = tuple([(master, WIDTH) for master in MASTERS])
    specs = [NewGlyph(name, layers) for name in to_make]
    package = scripting.current_package()
    made = create_glyphs(package, specs, "Add glyphs from list", history.scan_auto_facts(package))
    halfmoon.tell(f"Added {len(made.glyphs)} glyphs. Each one is its own Undo step.")


main()
```

One line is new in form. `folder = Path(font.path).parent if font.path else ""` uses the value-with-a-choice from chapter 37: the font's folder if the font has been saved, and otherwise an empty string, which lets the file window open wherever it likes. That's the unsaved-font guard chapter 26 left you as an exercise.

Save it as `Add Glyphs From List.py` in `Scripts/Halfmoon/`. It has under fifty lines. The collecting part is three lines long, and the rest is questions, guards and news. That proportion is normal for a script other people will run. It's also why the module matters. If `ask`, `tell`, `choose_text_file` and `read_names` weren't in `halfmoon.py`, this script would be a hundred lines long, and the next one would carry the same hundred lines again.

## What's in the box

Here's what Mira reads out to Ines. First, the menu. These are in `Scripts/Halfmoon/`, and anyone in the studio can run them without opening a file:

| Command | What it does | Changes the font? |
|---|---|---|
| Inventory | counts glyphs, empty glyphs, Unicode values and small caps | no |
| Friday Report | prints the week's numbers and saves them in `reports` | no |
| Widest First | lists metrics of the selected glyphs and the most lopsided | no |
| Rename Suffix | renames one suffix to another, after asking | yes, one Undo step |
| Add Glyphs From List | adds empty glyphs named in a text file, after asking | yes, one Undo step each |

Look at the third column. Three of the five can't hurt anything. The two that change the font ask first, check before they act, and say how to take the change back. You can now see chapters 29 to 31 and chapter 39 as one lesson spread over four days.

Second, the module. `halfmoon.py` holds what the scripts share:

| Kind | Names |
|---|---|
| Constants | `RED`, `YELLOW`, `GREEN`, `LEGEND`, `TITLE` |
| Glyph questions | `rich`, `is_empty`, `glyphs_of`, `widest_glyph`, `wider_than` |
| Tables and tallies | `metrics_rows`, `by_width`, `lopsided`, `status_tally` |
| Files | `read_names` |
| Windows | `tell`, `ask`, `ask_text`, `choose_text_file`, `choose_save_file` |

That's about twenty names. Every one is a thing Mira got wrong at least once before she got it right, and none of them will have to be got right again.

Third, the Python. In Part 1 you learned to say things to a font one glyph at a time. In Part 2 you learned to keep what it answers and to work with other people's material. Dictionaries look things up and count them, and sets compare (chapters 21 to 25). Text files go in and out, and tables go to a spreadsheet (26 to 28). Changes can be undone, plans come before changes and switches default to safe (29 to 31). Constants, a module of your own and functions with defaults keep the scripts short (32 to 34). Rows, sorting and one-line lists shape the answers (35 to 37). And you can read a long error from end to end and ask a person a question (38 and 39).

Ines writes for a while. Mira's own guess is that the Friday numbers used to take her most of an hour and now take a minute, and that the two renaming afternoons in week five would each be ten minutes today. Ines doesn't write down a total. She writes: *Mira's chores no longer depend on Mira.* Then she underlines "Inventory", which she ran herself on Tuesday on a font Mira has never opened.

## Where you are

Get out Oskar's sheet. It hasn't moved since chapter 20. Four lines are crossed out and seven are left:

- List the glyphs that are built from other glyphs.
- Mark every glyph that mixes its own outlines with borrowed ones.
- Make the left sidebearing of the *d*, *q* and *g* match the *o*.
- Rebuild the accented letters from the base letters and the accents.
- Find kerning pairs that are larger than they should be.
- Put the right family name and version number into every weight.
- Export the whole family to a dated folder every Friday.

Part 2 crossed out none of them, and that's as it should be. The chores of these four weeks came from Ines, Tomas and the publisher. They were all about names, numbers and lists, the outside of a glyph. Every line left on the sheet is about what's inside one: outlines, borrowed shapes, sidebearings measured against other shapes, accents sitting on letters.

So far a glyph has been a name, a Unicode value, a width with its two sidebearings, a color and a tag. You've asked whether it's empty, and that's the only question you've asked about what's drawn in it. In Part 3 you'll look at the drawing.

## What you learned

A script that other people run is mostly guards, questions and news around a few lines of work, and a shared module keeps that from being typed twice. Adding glyphs goes through a helper that takes a description of each one, checks the whole list before it touches the font, and records each addition so that it can be undone. When a helper refuses a list, it's usually better to fix the code that makes the list than to fix the file.

## Try it yourself

1. Give each new glyph the width of its parent instead of 500: `d.sc` gets the width of `d`, and `zero.sc` the width of `zero`. You'll need `split` from chapter 9, a lookup like the one in chapter 21, and a decision about what to do when the parent isn't in the font. Use the same width in all three masters for now.
2. Add a sixth command to the menu: `Status Report`, which prints `halfmoon.status_tally(font)` sorted by count, largest first, as chapter 36 showed. It's a script of about ten lines. Does it need to ask anything? Does it need a guard?
3. Go through the scripts in your `scripting-book` folder from Part 1 and pick one that still has its own copy of `is_empty` or its own loop for the widest glyph. Rewrite it to use `halfmoon`, and check that its output hasn't changed. Then count how many lines you deleted.

## Next

Part 3 opens with a glyph window and a single letter. Chapter 41 asks the `o` what it's made of, and the answer is two closed outlines and a count of points.
