---
this_file: src_docs/md/part6-families/112-export-all.md
---

# 112. Export them all

Tuesday of week twenty-two. The typesetter liked the fractions. Now the publisher wants the family: five weights, each as OTF for the printer and TTF for the office. That's ten files.

Mira exports them before lunch and sends a folder. At four the publisher's production desk writes back: "Where's the SemiBold for Word?"

Nine files had arrived, and nobody had counted them, because nine files in a folder look like a lot of files.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- Chapter 111's dated folder, and chapter 108's five instances if you want to do the export for real.

I couldn't run the code in FontLab 9. The script reads a folder and never asks FontLab to export, so I ran it in plain Python on stand-in files with names I made up. What FontLab calls its exported files, I haven't seen.

## Step 1: Say what should be there

Chapter 111 looked at a folder and reported what it found. That works for one file. For ten it's the wrong way round, since a list of what's there can't show you what isn't. You have to say first what you expect.

Five styles and two formats. A loop inside a loop visits every combination:

```python
STYLES = ["Light", "Regular", "Medium", "SemiBold", "Bold"]
FORMATS = [".otf", ".ttf"]

for suffix in FORMATS:
    for style in STYLES:
        print(f"GG Plum {style} {suffix}")
```

```text
GG Plum Light .otf
GG Plum Regular .otf
GG Plum Medium .otf
GG Plum SemiBold .otf
GG Plum Bold .otf
GG Plum Light .ttf
GG Plum Regular .ttf
GG Plum Medium .ttf
GG Plum SemiBold .ttf
GG Plum Bold .ttf
```

You've put a loop inside a loop before: in chapter 71, to walk every glyph of every kerning class, and in chapter 101, to look for every master in every glyph. There the inner list changed with each class. Here both lists stay as they are, and the inner loop runs through all its items for each single item of the outer one, so the count is one length times the other: 2 times 5. When the client adds WOFF2 next month, you add one string to `FORMATS` and the list grows to 15 by itself.

## Step 2: The mistake

Now match the list against the folder. The quick way is to ask whether the style's name is in the file's name:

```python
from pathlib import Path

folder = Path("/Users/mira/Halfmoon/exports/2026-12-08-v1.001")
names = [path.name for path in folder.rglob("*.otf")]
print(sorted([name for name in names if "Bold" in name]))
```

```text
['GGPlum-Bold.otf', 'GGPlum-SemiBold.otf']
```

Two files answer to "Bold". `in` asks whether one string appears anywhere inside another, and `Bold` appears inside `SemiBold`. A check built on that line would see the SemiBold's file, tick the box for the Bold, and stay quiet if the real Bold were missing. Font style names nest like this all the time: Light sits in ExtraLight, and Italic in every italic.

The cure is to compare whole names and not parts. That has its own snag, because I can't tell you how FontLab spells the file. It might be `GGPlum-SemiBold.otf`, or `GG Plum SemiBold.otf`, or something with an underscore.

So compare what all those spellings share. Take the letters and digits, lower them, and drop everything else:

```python
def key(text):
    return "".join([c for c in text.lower() if c.isalnum()])

print(key("GGPlum-SemiBold"))
print(key("GG Plum SemiBold"))
print(key("GG Plum" + "Bold"))
```

```text
ggplumsemibold
ggplumsemibold
ggplumbold
```

`isalnum()` is chapter 81's question, asked of one character at a time. `"".join` glues the survivors back together with nothing between them. Two spellings of the same file give the same key, and the Bold's key isn't the SemiBold's, because the comparison is now `==` on the whole thing.

Why not compare the file names as they are, with `==`? Because then the script would hold my guess about FontLab's spelling, and the first time the guess was wrong, all ten files would be `MISSING` while sitting in the folder. A check that cries wolf gets ignored within a week. The squeezed key asks less: the family, then the style, in that order, with whatever punctuation the exporter likes.

It can still be fooled. If two families were named `GG Plum` and `GGP Lum`, their keys would be the same. No font office names its families that way, and you now know where the weak spot is, which is more than the `in` test offered.

## Step 3: Look in every folder

`rglob` appeared in that snippet without a word. `folder.iterdir()` lists what's directly in a folder. `folder.rglob("*")` lists everything in it and in every folder below, however deep. The `*` means "any name".

That matters because the export window can sort its output into subfolders by family or by profile, and I don't know which switches you left on. With `rglob`, the script finds the files either way. `path.relative_to(folder)` then prints the path from the export folder down, such as `otf/GGPlum-Bold.otf`, so you see where each one landed.

## The whole script

```python
#FLM: Export Family
# Lists every font file a full export should leave in today's folder,
# then says which are there, which are missing and which are strangers.
from datetime import date
from pathlib import Path

import fly.ap.core.scripting as scripting
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


# Chapter 39's tell, written out again so this script runs by itself.
def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


STYLES = ["Light", "Regular", "Medium", "SemiBold", "Bold"]
FORMATS = [".otf", ".ttf"]


def export_folder(font, package):
    info = package.info
    version = f"{info.versionMajor}.{info.versionMinor:03d}"
    return Path(font.path).parent / "exports" / f"{date.today()}-v{version}"


def key(text):
    return "".join([c for c in text.lower() if c.isalnum()])


def expected(family):
    table = {}
    for suffix in FORMATS:
        for style in STYLES:
            table[(key(family + style), suffix)] = f"{family} {style} {suffix}"
    return table


def found(folder):
    table = {}
    for path in sorted(folder.rglob("*")):
        if path.is_file() and not path.name.startswith("."):
            table[(key(path.stem), path.suffix.lower())] = path
    return table


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    folder = export_folder(font, package)
    if not folder.exists():
        tell(f"No folder {folder.name} yet. Run export_current.py.")
        return
    want = expected(package.info.familyName)
    have = found(folder)
    missing = 0
    for item in want:
        if item in have and have[item].stat().st_size > 0:
            print(f"  ok       {have[item].relative_to(folder)}")
        else:
            print(f"  MISSING  {want[item]}")
            missing += 1
    for item in have:
        if item not in want:
            print(f"  extra    {have[item].relative_to(folder)}")
    print(f"{len(want)} wanted, {len(want) - missing} there, {missing} missing.")


main()
```

Save it as `export_family.py`. Before it can find anything, do the export. Run `export_current.py` for today's folder and its path. Then, in **File > Export Font As**, choose **OpenType PS (.otf)**, set the content to **Instances**, set the destination to that folder, and export. Do the same with **OpenType TT (.ttf)**. Those are the User Guide's words for the steps, and chapter 111 said how far I trust them.

On the afternoon in the story, the script would have said this:

```text
  ok       otf/GGPlum-Light.otf
  ok       otf/GGPlum-Regular.otf
  ok       otf/GGPlum-Medium.otf
  ok       otf/GGPlum-SemiBold.otf
  ok       otf/GGPlum-Bold.otf
  ok       ttf/GGPlum-Light.ttf
  ok       ttf/GGPlum-Regular.ttf
  ok       ttf/GGPlum-Medium.ttf
  MISSING  GG Plum SemiBold .ttf
  ok       ttf/GGPlum-Bold.ttf
  extra    otf/GGPlum-Regular.fea
10 wanted, 9 there, 1 missing.
```

The file names are my stand-ins. Yours come from FontLab.

Mira exports the SemiBold again as TTF, drags the `.fea` file out of the folder, and runs the script once more. It ends:

```text
10 wanted, 10 there, 0 missing.
```

Then she sends the folder, with that line pasted into the message. The production desk can count to ten as well as she can, and now they don't have to. If a file goes astray on their side, the line says what left Halfmoon's building.

Notes on the listing.

`expected` and `found` both return a dictionary with the same kind of key: a tuple of the squeezed name and the suffix, as in chapter 86. That's the design. Two tables with matching keys can be compared by asking `item in have`, and neither table needs to know how the other spells things. In `expected` the value is a readable description for the `MISSING` line. In `found` it's the real path.

The first loop walks `want`, so the report comes in the order of your lists and a missing file leaves its line where you'd look for it. The second loop walks `have` for whatever nobody asked for. The `.fea` file in my stand-in folder is the kind of thing an export can leave beside a font, and a stranger is worth a line: it may be harmless, or it may be last week's file in this week's folder.

A file of size 0 counts as missing. That's chapter 111's lesson, kept.

`missing += 1` counts as it goes, and the last line does one subtraction. Mira reads only that line on most days. If it ends `0 missing.`, she sends the folder.

The script doesn't create the folder. Chapter 111's script does that, and this one says so if the folder isn't there. One script that makes and one that checks is cleaner than two that both make.

## Break it on purpose

Start from the folder that reports `0 missing`. In it, rename one file so that its style is wrong: change `GGPlum-Medium.otf` to `GGPlum-Meduim.otf`. Run the script. Two lines change, and the summary with them:

```text
  MISSING  GG Plum Medium .otf
```

```text
  extra    otf/GGPlum-Meduim.otf
10 wanted, 9 there, 1 missing.
```

The script can't know those two lines are one mistake. It knows a wanted file is absent and an unwanted one is present, and it puts both in front of you. A check that tried to guess ("perhaps you meant Medium") would sooner or later guess wrong about a file going to a printer. Rename the file back.

Now the other direction. Add `"Black"` to `STYLES` and run. Two `MISSING` lines appear, one for each format, and the last line reads `12 wanted, 10 there, 2 missing.` Plum has no Black: chapter 107 showed the axis stops at 700. The script believed the list because the list is all it has. `STYLES` has to say what the font can make, and exercise 3 takes it from the font so that it can't drift. Take `"Black"` out.

## What you learned

A loop inside a loop builds every combination of two lists, and its length is the product of theirs. To find what's missing you first write down what's expected, then compare two tables that share a kind of key. `in` on strings finds a part anywhere, so names that contain other names need a whole comparison, and squeezing both sides to letters and digits makes that comparison survive spaces and hyphens. `rglob("*")` reads a folder and everything under it, and `relative_to` shows where each file sits.

## Try it yourself

1. The client adds web fonts. Put `".woff2"` in `FORMATS` and run. How many files are wanted now, and how many lines did you have to change?
2. Print the missing files again at the very end, after the summary line, so that a long report can't scroll them out of sight. Collect them in a list as you go.
3. Replace the `STYLES` constant with the names of the font's own instances. Chapter 107's `instance_records` reads them. What should the script say when the font has no instances at all?

## Next

One family is checked and sent. On the office server sits Oskar's archive: forty font files from before anybody at Halfmoon wrote a script. Chapter 113 opens each one, asks it a question, and closes it again without saving.
