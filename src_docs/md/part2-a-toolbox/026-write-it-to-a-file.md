---
this_file: src_docs/md/part2-a-toolbox/026-write-it-to-a-file.md
---

# 26. Write it to a file

Still Friday, four o'clock. The language question is answered, and now the weekly report is due. Mira picks **Scripts > Halfmoon > Friday Report**, five lines appear in the Output panel, and she does what she's done every Friday since chapter 18: drags the mouse across them, copies, switches to her mail, pastes.

Today she drags one line short. Ines gets a report with no widest glyph and writes back: *Where's the last line? And could this be an attachment? I keep them in a folder.*

Copying from a panel by hand is a small job, and small jobs done by hand are where the slips happen. The script already knows every word of the report. It can put them in a file.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `Friday Report.py` from [chapter 18](../part1-first-words/018-save-it-run-it-again.md).
- The `scripting-book` folder where your practice font lives.

## Step 1: Where is the font?

A file has to go somewhere. The natural place for a report about a font is next to the font. So the first question is where the font file sits on the disk, and the font can tell you:

```python
from fly import fl

font = fl.CurrentFont()
print(font.path)
```

```text
/Users/mira/Documents/scripting-book/Plum-practice.vfj
```

Yours will show your own name and wherever you put the folder. On Windows it starts with a drive letter and uses backslashes.

That string is a **path**: the route from the top of the disk down to one file. Read it like an address written backwards, biggest thing first. `Users`, then the person `mira`, then her `Documents`, then the folder `scripting-book`, and at the end the file. The slashes separate the stops.

You want the same address with a different last stop: same folder, but `report.txt` in place of the font. You could cut the string up yourself with `split`. Don't. Python comes with a tool that knows how addresses work, on a Mac and on Windows:

```python
from pathlib import Path

font_file = Path(font.path)
folder = font_file.parent
print(folder)
print(font_file.name)
```

```text
/Users/mira/Documents/scripting-book
Plum-practice.vfj
```

`Path` comes from `pathlib`, which ships with Python the way `datetime` does. You hand it the string and get back a path object: a wardrobe again, with drawers that make sense for an address. `parent` is the folder the file sits in. `name` is the last stop on its own.

To add a stop to a path, you use a slash. That's odd the first time you see it, because a slash between numbers means divide. Between a path and a string it means "and then, inside that":

```python
report_file = folder / "report.txt"
print(report_file)
```

```text
/Users/mira/Documents/scripting-book/report.txt
```

Nothing has been written yet. You've made an address. There's no house there.

## Step 2: Open, write, close

Writing a file takes three moves. You open it, you put text in, you close it. Python has a way of writing this so that the third move can't be forgotten:

```python
with open(report_file, "w", encoding="utf-8") as f:
    f.write("Friday report: GG Plum")
```

Run it. The Output panel stays empty. Go to the `scripting-book` folder in the Finder, or in Explorer on Windows. There's a new file, `report.txt`. Open it with a double-click, and there's your line.

Take the first line of the listing apart, because you'll type it for the rest of your scripting life.

`open(...)` opens a file and hands you something to write with. Three things go through the slot. The first is the address. The second, `"w"`, says what you're there to do: `w` for write. The third, `encoding="utf-8"`, I'll come back to in a moment.

`as f` puts the opened file in a box labeled `f`.

`with` and the colon and the indented block say: the file is open for as long as these indented lines run. When the indentation ends, Python closes it for you. You know this shape from `for` and `if`. Inside the block is "while the file is open". Outside is "afterwards".

Why does closing matter? Until a file is closed, some of your text may still be waiting in memory and not yet on the disk. Open the file too early from another program and you can find it half-written or empty. `with` makes sure the file gets closed even when a line inside the block goes wrong.

And `encoding="utf-8"`. A file on disk holds numbers, not letters. Chapter 23 showed you that every character has a number. An encoding is the rule for storing those numbers in a file, and UTF-8 is the rule that can store all of them and that nearly every program now expects. Leave it off and Python picks whatever your computer's system prefers, which on some Windows machines can't store an ő. This morning's report was full of such letters. Type the encoding every time and you won't have to think about it again.

## Step 3: Three things that go wrong

Break it on purpose, three ways. First, write a second line:

```python
with open(report_file, "w", encoding="utf-8") as f:
    f.write("Friday report: GG Plum")
    f.write("Glyphs: 208")
```

Open the file again.

```text
Friday report: GG PlumGlyphs: 208
```

The line from step 2 hasn't been kept and added to. It's been replaced. `"w"` means write from the start: if the file exists, its old contents are thrown away the moment you open it. Python doesn't ask. Keep that in mind before you aim `"w"` at a file you care about.

And the two pieces of text sit on one line. `print` has been ending every line for you since chapter 2. `write` doesn't. It puts down what you give it and nothing more. To end a line you write the line-ending character yourself. In Python you type it as `\n`, a backslash and an n, inside the quotes:

```python
    f.write("Friday report: GG Plum\n")
    f.write("Glyphs: 208\n")
```

Second mistake. Hand `write` a number:

```python
    f.write(208)
```

```text
TypeError: write() argument must be str, not int
```

`print` takes anything and turns it into text. `write` takes text and only text. An f-string is the handy way to make text out of anything, and you already know those.

Third mistake. Send the file to a folder that isn't there:

```python
report_file = folder / "reports" / "report.txt"
with open(report_file, "w", encoding="utf-8") as f:
    f.write("Friday report\n")
```

```text
FileNotFoundError: [Errno 2] No such file or directory: '/Users/mira/Documents/scripting-book/reports/report.txt'
```

That reads strangely. You weren't looking for a file, you were making one. What's missing is the folder `reports`. `open` will make a file. It won't make folders. Either make the folder by hand, or let the path make it, which you'll do in step 5.

## Step 4: Let print do the writing

Ending every line with `\n` and turning every number into text is a nuisance, and you have a tool that already does both. `print` can write to a file. You tell it which one with `file=`:

```python
with open(report_file, "w", encoding="utf-8") as f:
    print("Friday report:", font.info.familyName, file=f)
    print("Glyphs:", len(font), file=f)
```

```text
Friday report: GG Plum
Glyphs: 208
```

That text is in the file now, not in the Output panel. Everything you know about `print` still holds: commas between the pieces, a space put between them, any kind of thing accepted, a new line at the end. The only change is where the words land. Leave `file=f` off one line and that line goes to the Output panel as before. That's a slip anyone can make, and one you spot quickly.

This is why I held file writing back until you were comfortable with `print`. A report that prints is one small change away from a report that saves.

## Step 5: A name with the date in it

Ines keeps the reports in a folder, so each needs its own name, or every Friday will wipe out the last. The date belongs in the name. You have the date from chapter 18, and an f-string builds the name:

```python
from datetime import date

today = date.today()
reports = folder / "reports"
reports.mkdir(exist_ok=True)
report_file = reports / f"plum-report-{today}.txt"
print(report_file.name)
```

```text
plum-report-2026-11-13.txt
```

`mkdir` is short for "make directory", and directory is an older word for folder. `exist_ok=True` tells it not to complain when the folder is already there, which from the second Friday on it will be.

The date comes out as year, month, day. Leave it that way. File names that start with the year sort themselves into date order in any folder window, and no one has to wonder whether 11-12 is November or December.

## Step 6: The Friday report, saved

Now change the real script. Open `Friday Report.py` from the `Halfmoon` folder inside FontLab's `Scripts` folder. Three things change. Two imports join the one at the top. Four lines in `main` work out where the file goes. And the five `print` lines move into a `with` block and gain `file=f`. The two functions and the guard from chapter 19 stay as they are.

## The whole script

```python
#FLM: Friday Report
# Friday Report.py
# Saves a short status report on the current font for Ines,
# as a text file in the folder "reports" next to the font.

from datetime import date
from pathlib import Path

from fly import fl


def widest_glyph(font):
    widest = font[0]
    for glyph in font.glyphs:
        if glyph.width > widest.width:
            widest = glyph
    return widest


def names_without_unicode(font):
    names = []
    for glyph in font.glyphs:
        if glyph.unicode is None:
            names.append(glyph.name)
    return names


def main():
    font = fl.CurrentFont()
    if font is None:
        print("Friday Report: open a font first.")
        return

    no_unicode = names_without_unicode(font)
    widest = widest_glyph(font)

    today = date.today()
    reports = Path(font.path).parent / "reports"
    reports.mkdir(exist_ok=True)
    report_file = reports / f"plum-report-{today}.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        print("Friday report:", font.info.familyName, file=f)
        print("Date:", today, file=f)
        print("Glyphs:", len(font), file=f)
        print("Without Unicode:", len(no_unicode), no_unicode, file=f)
        print(f"Widest: {widest.name} ({widest.width:.0f})", file=f)

    print("Saved", report_file)


main()
```

Save, and run it from the **Scripts** menu. One line appears in the Output panel:

```text
Saved /Users/mira/Documents/scripting-book/reports/plum-report-2026-11-13.txt
```

The last line of the script has no `file=f` and sits outside the `with` block, so it goes to the panel, after the file is closed. It's the script saying out loud that it did something, and where. A script that writes a file and says nothing leaves you hunting through folders.

Mira attaches the file. All five lines are in it, because nobody dragged a mouse. Ines files it and replies with one word, which from Ines is praise.

The script has one weak spot, and you should know about it. A font that's never been saved has no file, so it has no path to stand next to. Make a new font with **File > New Font**, run the report on it, and see what the complaint says. Then close that font without saving. In chapter 19 you learned to guard against a missing font with `if font is None:`. A guard for a font with no path is the first exercise.

??? info "Going deeper: letting the user pick the folder"
    The script decides where the file goes, and for a weekly report that's what you want. For a tool that other people use, you'd let them choose, with the same Save window every program shows. FontLab scripts can open that window. It needs a few ideas you haven't met, so it waits for chapter 39, where your scripts start asking questions.

## What you learned

`font.path` is where the font file lives, and `Path` from `pathlib` takes that address apart and builds new ones with `/`. A file is written inside `with open(address, "w", encoding="utf-8") as f:`, which closes the file for you. `"w"` replaces whatever was there. `print(..., file=f)` sends a line to the file and not the Output panel, so any report you can print is a report you can save.

## Try it yourself

1. Run the report on a new, unsaved font and read the error. Then add a guard above the line that builds `reports`: if the font has no path, print a sentence asking the user to save the font first, and don't write anything. Print `font.path` for the unsaved font first, so you know what to test for.
2. Open a file with `"a"` where the script has `"w"`. Run it three times and look at the file. What does `"a"` stand for, and when would Ines want it?
3. Change `missing_chars.py` from chapter 25 so that it saves the language report as `plum-languages.txt` in the `reports` folder. Open the result. Are the ő and the ž there? Then take `encoding="utf-8"` out and try again. On a Mac you'll likely see no difference. Put it back anyway.

## Next

Chapter 27 goes the other way. Somebody sends Mira a text file with a list of glyph names, and the script has to read it.
