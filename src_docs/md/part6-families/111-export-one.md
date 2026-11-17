---
this_file: src_docs/md/part6-families/111-export-one.md
---

# 111. Export one font

Monday of week twenty-two, ten past two. The typesetter writes: "Send me an OTF of the Regular by five. I want to try the new fractions in the index."

Everything this book has done so far stayed inside FontLab. The file on Mira's disk is a source: it holds three masters, layers nobody will ship, notes, and an Undo history. The typesetter can't install that. She needs a font file, and making one from the source is called exporting.

This chapter exports one font. It's also the chapter where I have to tell you the most plainly what a script can't yet do for you.

## What you need

- `Plum-practice` open in FontLab 9 and saved, with Fly installed.
- `halfmoon.py` with `tell`.
- Chapter 26's `Path`, and chapter 97's version number.

I couldn't run the code in FontLab 9. The script's file handling is plain Python, and I ran it on a folder of stand-in files. The steps in FontLab's export window come from the FontLab User Guide, and I haven't clicked them in version 9.

## Where this chapter stops, and why

FontLab has a Python call for exporting. Its documentation says so, and the call is in the list of names FontLab offers. But I've read every script in the collections this book draws on, and none of them uses it. I can't tell you the names of its settings with confidence, or whether it waits until the file is written, or what it does when a file is already there.

I'm not going to print a call I can't vouch for in the one chapter where a wrong file goes to a client. So the export is done by hand, in **File > Export Font As**, and it takes six clicks. The script does the two jobs around it: beforehand it decides where the file goes, and afterward it checks that a real file arrived. People skip both of those when they're in a hurry, and five o'clock is a deadline.

## Step 1: What you can export

The export window offers profiles, and a profile is a named set of settings for one format. Four matter to this part of the book:

- **OpenType PS (.otf)**: one style in one file, with the outlines kept as the curves you drew. It's what the typesetter asked for.
- **OpenType TT (.ttf)**: one style in one file, with the curves converted to the kind that screens prefer.
- **OpenType Variations (.ttf)**: every master and the weight axis in a single file. The program that uses the font does chapter 106's sum itself.
- **DesignSpace + UFO**: the source, in an open format that other font tools read. It isn't installable.

The first two are single-style formats, so FontLab asks which content you mean: the current layer, the instances, or the masters. For one Regular, it's the current layer, and the current layer had better be the Regular.

## Step 2: Where it goes

A font file sent to a client should be findable in six months. Give every export its own folder, named for the day and the version:

```python
from datetime import date
from pathlib import Path

import fly.ap.core.scripting as scripting
from fly import fl

font = fl.CurrentFont()
package = scripting.current_package()
info = package.info
version = f"{info.versionMajor}.{info.versionMinor:03d}"
folder = Path(font.path).parent / "exports" / f"{date.today()}-v{version}"
print(folder)
```

```text
/Users/mira/Halfmoon/exports/2026-12-07-v1.001
```

Your path and date will differ. The version is chapter 97's, with its `:03d`. `date.today()` prints with the year first, so a folder list sorted by name is also sorted by time.

The folder doesn't exist yet. Chapter 26 made one with `mkdir(exist_ok=True)`. Here two are missing, `exports` and the dated one inside it, and `mkdir` refuses to make a folder whose parent isn't there. `parents=True` tells it to make whatever is missing on the way:

```python
folder.mkdir(parents=True, exist_ok=True)
```

## Step 3: The mistake

Now the check. After the export, is the font there?

```python
if folder.exists():
    print("Exported.")
```

```text
Exported.
```

Run that before you've exported anything. It says `Exported.`

The folder exists because the line above it made the folder. The test asked about the folder and the message spoke about the font. A script that reports success by looking at its own preparations will always report success.

Ask about the thing itself. What files are in the folder?

```python
for path in sorted(folder.iterdir()):
    print(path.name, path.suffix, path.stat().st_size)
```

Before the export that loop prints nothing, which is the truth. `iterdir()` gives each item in a folder as a `Path`. `path.suffix` is the end of the name from the last dot, such as `.otf`. `path.stat().st_size` is the file's size in bytes: `stat` asks the disk for the facts it keeps about a file, and the size is one of them.

## The whole script

```python
#FLM: Export Current
# Makes a dated folder for an export, says what to choose in FontLab,
# and on the next run reports what arrived. Exports nothing itself.
from datetime import date
from pathlib import Path

import fly.ap.core.scripting as scripting
import halfmoon
from fly import fl

WANTED = [".otf"]


def export_folder(font, package):
    info = package.info
    version = f"{info.versionMajor}.{info.versionMinor:03d}"
    return Path(font.path).parent / "exports" / f"{date.today()}-v{version}"


def arrived(folder):
    rows = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and not path.name.startswith("."):
            rows.append((path.name, path.suffix.lower(), path.stat().st_size))
    return rows


def instructions(folder, package):
    print("Nothing there yet. In FontLab:")
    print(f"  1. Pick the master to send. Now: {package.master}.")
    print("  2. File > Export Font As.")
    print("  3. Profile: OpenType PS (.otf). Content: Current layer.")
    print(f"  4. Destination: Folder, {folder}")
    print("  5. Family and Profile subfolders off. Existing files: Skip.")
    print("Then run this script again.")


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    if not font.path:
        halfmoon.tell("Save the font first, so the export has a home.")
        return
    package = scripting.current_package()
    folder = export_folder(font, package)
    folder.mkdir(parents=True, exist_ok=True)
    print(f"Export folder: {folder.parent.name}/{folder.name}")
    rows = arrived(folder)
    if not rows:
        instructions(folder, package)
        return
    for name, suffix, size in rows:
        note = "  EMPTY" if size == 0 else ""
        print(f"  {name:<28}{size / 1024:>8.1f} KB{note}")
    for suffix in WANTED:
        good = [row for row in rows if row[1] == suffix and row[2] > 0]
        print(f"{suffix}: {len(good)} good.")


main()
```

Save it as `export_current.py`. Save the font too, with **File > Save**, since an export is made from what FontLab holds and you want the source on disk to match it. Then run the script:

```text
Export folder: exports/2026-12-07-v1.001
Nothing there yet. In FontLab:
  1. Pick the master to send. Now: Regular.
  2. File > Export Font As.
  3. Profile: OpenType PS (.otf). Content: Current layer.
  4. Destination: Folder, /Users/mira/Halfmoon/exports/2026-12-07-v1.001
  5. Family and Profile subfolders off. Existing files: Skip.
Then run this script again.
```

Do what it says. Then run it again:

```text
Export folder: exports/2026-12-07-v1.001
  GGPlum-Regular.otf              60.0 KB
.otf: 1 good.
```

I made up that file name and that size. FontLab names the file from the font's names, and I haven't seen what it calls this one. The script doesn't care: it reports whatever is there.

Notes on the listing.

The script is run twice, and the folder tells it which run this is. Empty means "tell me what to do", and anything else means "tell me what I've got". Nothing has to be remembered between the runs, so nothing can be remembered wrong.

`package.master` is the name of the master FontLab is showing. Line 1 of the instructions prints it because "Current layer" exports the layer you're looking at, and if Mira was last working on the Bold, the typesetter gets a Bold in a file she'll take for the Regular.

`arrived` leaves out names that begin with a dot. Your computer keeps small files of its own in folders, and they aren't fonts. It lowers the suffix, because `.OTF` and `.otf` are the same format to everyone but Python.

`size / 1024` turns bytes into kilobytes. A kilobyte here is 1,024 bytes, and `:>8.1f` is chapter 12's right-hand column with one decimal.

The fifth instruction says **Skip** for existing files. FontLab offers four choices there, and the User Guide lists them: Rename, Overwrite, Move to Trash, Skip. A dated folder that already holds a file has been sent to somebody. With Skip, a second export on the same day does nothing to it, and you find out because the file's size doesn't change. If the font changed, chapter 97's script gives it a new version, and the new version gets a new folder.

## Break it on purpose

The check counts a file as good when its size is above 0. See why that's there. In **Finder** or **Explorer**, make an empty text file in the export folder and name it `Test.otf`. Run the script:

```text
Export folder: exports/2026-12-07-v1.001
  GGPlum-Regular.otf              60.0 KB
  Test.otf                         0.0 KB  EMPTY
.otf: 1 good.
```

Two files end in `.otf` and one is good. A suffix is a claim a file makes about itself, and anything can make it. An export that was interrupted, or a disk that filled up, can leave a name with nothing behind it. The typesetter's computer would refuse it at one minute to five.

A size above 0 is a low bar too. It proves there are bytes, and it doesn't prove they're a font. Chapter 118 opens the file and reads what's inside. Delete `Test.otf`.

## The call I didn't use

For the record, here are the names. FontLab's list of Python names has an `ExportControl` with settings called `profileName`, `destinationFolder`, `conflictMode` and `contentMode`, and the workspace has `exportFont(package, control)`. The User Guide says that's the scripted route.

What those settings accept, I don't know. `conflictMode` and `contentMode` take numbers, and no list says which number means Skip or Current layer. If you try the call, try it on a copy of the font and into an empty folder, and write down what each number did. Then chapters 112 and 119 can use it, and you'll know something I don't.

## What you learned

Exporting makes a font file from the source, through a profile that fixes the format, and for single-style formats you also say which master or instance you mean. `mkdir(parents=True, exist_ok=True)` makes a folder and any missing folders above it, and a folder named by date and version keeps each export apart. A check has to look at the result and not at the preparations: `iterdir`, `suffix` and `stat().st_size` say what files exist, what they claim to be and whether anything is in them. The export itself is done by hand in this book, because the scripted call exists and nobody I could read has shown how it behaves.

## Try it yourself

1. The typesetter also wants a TTF. Set `WANTED = [".otf", ".ttf"]`, run the script, and read the last two lines. Then export with **OpenType TT (.ttf)** into the same folder and run it again.
2. Add a line after the `good` count that prints `MISSING` in capitals when the count is 0, so that a missing format can't be read past.
3. Write `newest(exports)`, which takes the `exports` folder and returns the dated folder that sorts last. Why does sorting by name work here, and what name would break it?

## Next

One font went out. The client's list has five weights that Plum can make and two formats for each. Chapter 112 works out all ten file names before any of them exists.
