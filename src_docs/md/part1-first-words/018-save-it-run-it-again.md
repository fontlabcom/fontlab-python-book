---
this_file: src_docs/md/part1-first-words/018-save-it-run-it-again.md
---

# 18. Save it, run it again

On Wednesday Ines stops at Mira's desk with a request that sounds small. Every Friday, before the weekly call with the publisher, she wants five lines about Plum: the family name, the date, how many glyphs there are, which ones have no Unicode value yet, and the widest glyph. Tomas keeps asking about the last one.

Mira can write that. She has all the pieces. What bothers her is the word "every". Every Friday she'd open the Scripting panel, find the file, open it and press the button. Four steps aren't many, but they're four steps she has to remember on the busiest morning of the week.

She messages Oskar. The answer comes back before lunch: "Put it in the menu. Then it's a command, like any other."

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `template.py` from chapter 17. If you skipped it, an empty script will do.

## Step 1: Write the report

Start from the template and save it under a new name, `friday_report.py`, in your `scripting-book` folder. You'll move it later.

Two of the five lines need a loop, so they get a function each. Type the first one and try it on its own before you go on:

```python
from fly import fl


def widest_glyph(font):
    widest = font[0]
    for glyph in font.glyphs:
        if glyph.width > widest.width:
            widest = glyph
    return widest


font = fl.CurrentFont()
print(widest_glyph(font))
```

```text
<fgGlyph 'emdash'>
```

Read the function from the top. It puts the first glyph of the font into a box called `widest`. Then it walks through all the glyphs, and each time it meets one that's wider than the glyph in the box, it puts that one in the box in its place. When the loop is done, the box holds the widest glyph of all, and `return` hands it back.

This is a pattern you'll use for the tallest, the narrowest, the longest name, the largest kerning pair: start with the first one, compare it with each of the others, keep the winner.

The second function collects names in a list, the way you did in chapter 10:

```python
def names_without_unicode(font):
    names = []
    for glyph in font.glyphs:
        if glyph.unicode is None:
            names.append(glyph.name)
    return names
```

You saw in chapter 6 that a glyph with no Unicode value has `None` in that drawer. `is None` is how you ask whether a box holds that nothing. Chapter 19 has more to say about it.

## Step 2: Borrow today's date

The report needs a date, and Mira isn't going to type it in by hand each week. Python can read the computer's calendar. The tool for it doesn't come from Fly. It comes with Python itself, in a package called `datetime`.

```python
from datetime import date

print(date.today())
```

```text
2026-11-13
```

You'll get your own day, in the same year-month-day order. That order sorts well in a file list, which matters in Part 6 when you export a family to a dated folder.

The import line has the shape you know from chapter 4: `from` a package, `import` a tool. Python arrives with a few hundred packages like this one, for dates, file names, math and much else. You've been inside FontLab so far, and here you reach past it for the first time.

Now make the mistake. Python cares about capitals, and so do package names:

```python
from datetime import Date
```

```text
ImportError: cannot import name 'Date' from 'datetime'
```

The real message goes on to name the file where Python looked. It's the same error you got in chapter 4 when you asked Fly for a tool it doesn't have: the package is there, the name inside it isn't. Change `Date` back to `date`.

## Step 3: Put it together

Here's the whole script, in the shape from chapter 17. There are no settings this time, so that part is left out.

```python
#FLM: Friday Report
# Friday Report.py
# Prints a short status report on the current font for Ines:
# family name, date, glyph count, glyphs without a Unicode value,
# and the widest glyph.

from datetime import date

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


font = fl.CurrentFont()
print("Friday report:", font.info.familyName)
print("Date:", date.today())

no_unicode = names_without_unicode(font)
widest = widest_glyph(font)
print("Glyphs:", len(font))
print("Without Unicode:", len(no_unicode), no_unicode)
print(f"Widest: {widest.name} ({widest.width:.0f})")
```

```text
Friday report: GG Plum
Date: 2026-11-13
Glyphs: 208
Without Unicode: 4 ['.notdef', 'a.sc', 'b.sc', 'c.sc']
Widest: emdash (1000)
```

One line reaches into `font.info`, the drawer of facts about the whole font that gave you the units per em in chapter 11. `familyName` is another drawer in the same wardrobe, next to the style name and a few dozen more. Part 6 opens most of them. Today you need one.

The em dash is the widest glyph in Plum, 1,000 units, which is the full height of the grid turned sideways. That's where its name comes from. Tomas will be pleased to have that settled.

## Step 4: Find the Scripts folder

FontLab keeps a folder of its own for the things you add to it. It's called the user data folder, and Fly's installer put its packages there in chapter 4. Inside it is a folder named `Scripts`. Every Python file in that folder shows up in FontLab's **Scripts** menu.

The quickest way there:

1. Open **Preferences**. On a Mac, press ++cmd+comma++.
2. Go to the **General** page.
3. Click **Open user data folder in Finder**. On Windows the button says **in Explorer**.

A file window opens. On a Mac the folder sits at `~/Library/Application Support/FontLab/FontLab 9`. Look inside for `Scripts`. You'll find that it isn't empty: Fly's installer left a folder called `Extensions` there, and you met its **List Extensions** command in chapter 4 without knowing where it lived.

A folder inside `Scripts` becomes a submenu. Use that. Make a new folder inside `Scripts` and call it `Halfmoon`. Everything the studio writes will go there, apart from what other people's installers bring.

## Step 5: Move the script and refresh the menu

In FontLab, choose **Save Script As…** from the Scripting panel's menu, go to your new `Halfmoon` folder, and save the script there as `Friday Report.py`.

Then choose **Scripts > Refresh Scripts**. FontLab reads the folder again and rebuilds the menu.

Open the **Scripts** menu. There's a **Halfmoon** submenu, and in it one command: **Friday Report**. Choose it. The five lines appear in the **Output** panel. The Scripting panel doesn't need to be open, and nothing needs to be loaded into it.

Where did the command's name come from? From the first line of the file. You met `#FLM:` at the end of chapter 17: when the first line of a script starts with it, FontLab uses the rest of that line as the title in the menu. If the line isn't there, FontLab builds a title out of the file name.

Try it. Change the first line to `#FLM: Friday Report for Ines`, save, and choose **Scripts > Refresh Scripts** again. The command has a new name, and the file doesn't. Change it back when you've seen it.

!!! note "Two copies"
    You now have `friday_report.py` in `scripting-book` and `Friday Report.py` in the `Scripts` folder. The menu runs the second. Delete the first, or one Friday you'll improve the wrong one and wonder why nothing changed.

## Step 6: Run it on another font

Open the original `plum-var.vfj` next to your practice copy, so that it's the font in front. Choose **Scripts > Halfmoon > Friday Report**.

```text
Friday report: GG Plum
Date: 2026-11-13
Glyphs: 205
Without Unicode: 1 ['.notdef']
Widest: emdash (1000)
```

The script isn't about `Plum-practice`. It never names a file. It asks FontLab for the current font, whichever font that is at the moment you choose the command, and reports on that. When there's more than one font to report on, the same command will do for each of them.

Now close every font and choose the command once more. You get a letter of complaint, and its last line is one you've seen:

```text
AttributeError: 'NoneType' object has no attribute 'info'
```

With no font open, `fl.CurrentFont()` hands back `None`, and `None` has no drawers. A command that sits in a menu will sooner or later be chosen at the wrong moment, by you or by somebody else in the studio. It should say something better than this. That's the next chapter.

On Friday morning Mira chooses the command, copies five lines out of the **Output** panel and pastes them into a message to Ines. It takes her less time than finding the file would have.

??? info "Going deeper: what else lives in that folder"
    The user data folder is where FontLab keeps everything that's yours and not part of the app: scripts, the packages Fly installed under `python/3.11/site-packages`, and a good deal that has nothing to do with Python. You can add other script folders too, anywhere on your disk, from the sidebar of the Scripting panel with **Add scripts folder**. A studio can keep one shared folder on a server that way, and Part 7 comes back to that idea.

## What you learned

A script saved in the `Scripts` folder of FontLab's user data folder becomes a command in the **Scripts** menu after **Scripts > Refresh Scripts**; a folder there becomes a submenu, and a first line starting with `#FLM:` sets the command's title. Python ships with packages of its own, such as `datetime`, that you import the same way you import from Fly. A script that asks for the current font works on whichever font is in front, and the pattern "start with the first, compare with the rest, keep the winner" finds the largest or smallest of anything.

## Try it yourself

1. Save `wide_glyphs.py` from chapter 17 into the `Halfmoon` folder, refresh, and run it from the menu. It already has its `#FLM:` line.
2. Write `narrowest_glyph(font)` by changing one character in a copy of `widest_glyph`, and add a line for it to the report. In Plum as it came, that's `quotesingle`, the straight single quote, at 190 units. If you get `a.sc`, that tells you what width FontLab gave your new glyphs.
3. Make a second folder inside `Scripts`, called `Scratch`, and save any small script there. Refresh and look at the menu. Then delete the folder in the file window, refresh again, and check that the submenu is gone.

## Next

Chapter 19 takes the complaint from step 6 and teaches the script to check for trouble before it starts.
