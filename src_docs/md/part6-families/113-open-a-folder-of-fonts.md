---
this_file: src_docs/md/part6-families/113-open-a-folder-of-fonts.md
---

# 113. Open a folder of fonts

Wednesday of week twenty-two. A reseller wants to know which of Halfmoon's old families exist in more than one weight. Oskar's answer is a folder called `archive`. "Forty files," he says. "Fifteen years. I don't remember what's in half of them."

Every script so far worked on the font you had open. Today's script opens fonts itself, one after another, asks each a question, and closes it. Opening is the simple half. The closing needs care, because a script that closes fonts can close the wrong one, and it can throw work away without asking.

## What you need

- FontLab 9 with Fly installed, and `halfmoon.py` with `tell`.
- A folder of FontLab files to try it on. Three copies of `Plum-practice` under different names will do.
- Chapter 95's `try` and `finally`, and chapter 112's `rglob`.

I couldn't run the code in FontLab 9. I ran the script on a stand-in archive of forty invented files, with stand-ins for the two FontLab calls that open and close. Those two calls are used in the same way by one tested set of example scripts in FontLab's own collections, and that's all I have to go on for them.

## Step 1: Find the files

Chapter 112 walked a folder and everything below it with `rglob("*")`. The star stands for any name. Its smaller relation is `glob`, which looks in the one folder only, and both take a pattern:

```python
from pathlib import Path

ARCHIVE = Path.home() / "Halfmoon" / "archive"
files = sorted(ARCHIVE.glob("*.vfc"))
print(len(files))
```

```text
31
```

`Path.home()` is your own folder on this computer, whatever it's called. `"*.vfc"` means any name that ends in `.vfc`, FontLab's usual file type.

## Step 2: The mistake

Thirty-one. Oskar said forty.

He might have miscounted. Before you tell him so, look at what the pattern can't see. It asks for names ending in `.vfc` in one folder, and that leaves out three kinds of file:

- five files saved as `.vfj`, FontLab's other format, the one made of readable text;
- four drafts in a subfolder called `old`;
- and those four are named `.VFC` in capitals, by some older computer.

The pattern did what it was told. It counted the files that matched, and nothing in a count says what didn't match. Chapter 112 met the same thing from the other side: a test that's too loose finds too much, and one that's too tight finds too little, and neither complains.

So search everything, and decide in Python, where you can lower the case first:

```python
KINDS = [".vfc", ".vfj"]


def font_files(folder):
    return [p for p in sorted(folder.rglob("*")) if p.suffix.lower() in KINDS]


print(len(font_files(ARCHIVE)))
```

```text
40
```

Forty. The folder also holds a text file, a PDF and an exported `.otf`, and none of them is counted, because their suffixes aren't in `KINDS`.

## Step 3: Open one, and know which one you opened

Fly's `pr` is a way of asking FontLab to do things a person would do from the menus. You give it the name of a job and the details:

```python
from fly import fl, pr

reply = pr.call("open_font", path=str(files[0]))
print(reply.get("status"))
```

```text
ok
```

`reply` is a dictionary, and `"status"` is `"ok"` when the font opened. That's all it tells you that I can vouch for. It doesn't hand you the font.

So which font is it? You might reach for `fl.CurrentFont()`, on the guess that a font that opened a moment ago is the current one. Don't. It's a guess about what FontLab does with its windows, and if it's wrong, the "current font" is `Plum-practice`, with this morning's unsaved work in it.

Ask for the font by the one thing you know for certain about it, the file it came from:

```python
def open_package(path):
    reply = pr.call("open_font", path=str(path))
    if reply.get("status") != "ok":
        return None
    for item in fl.flWorkspace.instance().packages():
        package = fl.flPackage(item)
        if package.path and Path(package.path).resolve() == path.resolve():
            return package
    return None
```

`fl.flWorkspace.instance().packages()` is every font FontLab has open, and `fl.flPackage(item)` turns each into the kind of package you've used since chapter 29. `resolve()` writes a path out in full, so two spellings of the same place compare as equal. The function returns the package whose file is the file you asked for, or `None`.

## Step 4: Close it, whatever happens

Closing is another job for `pr`:

```python
pr.call("close_font", font_id=package.fgId, save=False)
```

`package.fgId` is the number FontLab knows this font by. `save=False` means close without saving and without asking. Read that again. No dialog appears. Whatever changed in that font since it was opened is gone.

For a font you opened to read, that's what you want. For any other font it's a disaster, which is why the last step mattered: the only package this script ever closes is one that `open_package` found by its path.

Two more precautions, and then the script.

First, the script never opens Oskar's files. It copies each into a scratch folder and opens the copy. If FontLab should change an old file on opening it, or if something I haven't foreseen goes wrong, the archive is as it was. `shutil.copy(path, folder)` copies a file into a folder and returns the new path. `tempfile.TemporaryDirectory()` makes a folder in the place your computer keeps for such things, and in a `with` block it removes the folder and everything in it when the block ends.

Second, the close goes in a `finally`. Chapter 95 used `finally` for work that must happen whether or not the lines above it failed. If reading a font's facts raises an error, the font is still closed.

## The whole script

```python
#FLM: Folder Report
# Opens a copy of each font file in a folder, notes a few facts,
# and closes the copy without saving. Changes no file in the folder.
import shutil
import tempfile
from pathlib import Path

import halfmoon
from fly import fl, pr

ARCHIVE = Path.home() / "Halfmoon" / "archive"
KINDS = [".vfc", ".vfj"]
LIMIT = 3


def font_files(folder):
    return [p for p in sorted(folder.rglob("*")) if p.suffix.lower() in KINDS]


def open_package(path):
    reply = pr.call("open_font", path=str(path))
    if reply.get("status") != "ok":
        return None
    for item in fl.flWorkspace.instance().packages():
        package = fl.flPackage(item)
        if package.path and Path(package.path).resolve() == path.resolve():
            return package
    return None


def facts(package):
    info = package.info
    version = f"{info.versionMajor}.{info.versionMinor:03d}"
    masters = len(package.masters)
    return f"{info.familyName:<16}{version:>6}{masters:>3} masters"


def look_at(path, scratch):
    copy = Path(shutil.copy(path, scratch))
    package = open_package(copy)
    if package is None:
        return "DID NOT OPEN"
    try:
        return facts(package)
    finally:
        pr.call("close_font", font_id=package.fgId, save=False)


def main():
    if not ARCHIVE.exists():
        halfmoon.tell(f"No folder {ARCHIVE}.")
        return
    files = font_files(ARCHIVE)
    print(f"Font files in {ARCHIVE.name}: {len(files)}.")
    failed = 0
    with tempfile.TemporaryDirectory() as scratch:
        for path in files[:LIMIT]:
            line = look_at(path, scratch)
            if line == "DID NOT OPEN":
                failed += 1
            print(f"  {str(path.relative_to(ARCHIVE)):<26}{line}")
    looked = len(files[:LIMIT])
    print(f"Looked at {looked} of {len(files)}. Did not open: {failed}.")


main()
```

Save it as `folder_report.py`, point `ARCHIVE` at your folder, and save your own font before you run it. With Oskar's archive:

```text
Font files in archive: 40.
  Bramble-2011-a.vfc        HM Bramble       2.006  2 masters
  Bramble-2013-c.vfc        HM Bramble       2.003  3 masters
  Bramble-2016-b.vfc        HM Bramble       2.005  2 masters
Looked at 3 of 40. Did not open: 0.
```

The names and numbers are mine, invented for the stand-in. Yours will be whatever your folder holds.

Three files, because `LIMIT` is 3. `files[:LIMIT]` is chapter 10's slice. Opening a font takes FontLab a moment, and forty moments is a while to wait for a script you haven't seen work. Watch three fonts open and close. Check in the **Window** menu that none of them stayed. Then raise `LIMIT` to 40:

```text
Font files in archive: 40.
  Bramble-2011-a.vfc        HM Bramble       2.006  2 masters
  Bramble-2013-c.vfc        HM Bramble       2.003  3 masters
  Bramble-2016-b.vfc        HM Bramble       2.005  2 masters
  Bramble-2019-a.vfc        HM Bramble       2.000  1 masters
  Damson-2010-b.vfc         DID NOT OPEN
  Damson-2013-a.vfc         HM Damson        1.002  2 masters
```

and thirty-four more lines, ending:

```text
  old/Sloe-draft-4.VFC      HM Sloe          2.006  3 masters
Looked at 40 of 40. Did not open: 1.
```

Notes on the listing.

`look_at` returns from inside the `try`. The `finally` still runs. Python works out the value to return, runs the `finally`, then hands the value back. So the font is closed before `main` prints its line.

A file that didn't open gets a line that says so, and the loop goes on. One bad file in forty shouldn't cost you the other thirty-nine. The script doesn't say why `Damson-2010-b.vfc` failed, because I don't know what the reply holds when a font doesn't open. Add `print(reply)` in `open_package` if you want to see for yourself. One case the script doesn't tell apart: if FontLab says `ok` but no open font has the copy's path, the line also reads `DID NOT OPEN`, and that font stays open. If the Window menu grows while the script runs, that's what happened, and you close those copies by hand without saving.

`str(path.relative_to(ARCHIVE))` is chapter 112's relative path, turned into a string so that `:<26` can pad it. The drafts show as `old/Sloe-draft-4.VFC`, folder and all.

"1 masters" is poor English, and exercise 1 mends it.

## Break it on purpose

Prove the `finally`. In `facts`, change `info.familyName` to `info.familyNam`, set `LIMIT` back to 3, and run:

```text
Font files in archive: 40.
Traceback (most recent call last):
  ...
AttributeError: ... has no attribute 'familyNam'
```

The script stopped at the first font. Now look in the **Window** menu. The copy of `Bramble-2011-a.vfc` isn't there. The error went up through `look_at`, and on its way the `finally` closed the font. Then it went up through the `with`, which removed the scratch folder. Both tidied up after a failure neither of them knew about.

Take the `try` and `finally` lines away, leave the close as an ordinary last line, and the same slip leaves a stray font open each time you run. That's a nuisance with three and a mess with forty. Put everything back.

## The line I won't have you run

One variant of this script circulates wherever people share snippets. It opens a file and then closes `fl.CurrentFont()`. On a good day the current font is the one it opened. On a bad day it's your own, and `save=False` does what it says. I've described it so that you'll know it when you meet it. This book's rule: a script closes only what it opened itself, found by path, and only copies.

FontLab's packages also have a `close` method of their own. The notes kept with FontLab's example scripts record that calling it from a script brought up a save dialog and crashed FontLab, so the book doesn't use it.

## What you learned

`glob` and `rglob` find files by pattern, and a pattern that's too tight leaves files out without a word, so count against what a person expects. `pr.call("open_font", path=...)` opens a font and answers with a status, and you find the font it opened by comparing paths, never by assuming it's the current one. `pr.call("close_font", font_id=..., save=False)` closes without asking, which is safe only for a copy the script opened itself, and `finally` makes sure it happens. `tempfile.TemporaryDirectory()` and `shutil.copy` give a script a place to work that isn't the user's own files.

## Try it yourself

1. Mend "1 masters". Chapter 40's one-line `if` will do: `"master" if masters == 1 else "masters"`.
2. Oskar's question was which families have more than one weight. Have `look_at` return the family name and the master count as a tuple, tally the largest count for each family in a dictionary, and print the families where it's above 1.
3. Add the year to each line. It's in the file name: `path.stem.split("-")[1]` for `Bramble-2011-a.vfc`. Which four files does that give no year for, and what should the script print for them?

## Next

The script can now go and look at fonts other than the one in front of you. Chapter 114 turns back to the one that's about to ship, and gathers everything that went wrong in the last release into a list of checks.
