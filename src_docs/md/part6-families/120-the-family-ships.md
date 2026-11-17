---
this_file: src_docs/md/part6-families/120-the-family-ships.md
---

# 120. The family ships

Monday of week twenty-four. Friday's folder went to the publisher a little after four. This morning the art director's assistant writes: "Is this the release? Can we build the catalog on it?"

Mira starts typing yes and stops. The folder holds five weights. The art director asked for nine. Ines read the text proof on paper on Friday. Nobody has typed a line with the new files in the layout program the publisher uses. And nobody has told the art director in so many words that four weights aren't coming this year.

The build finished. That says the machine's part was done. A release is a claim made to a person, and it has parts no script can do. So the last script of Part 6 does no work on the font at all. It writes down what was asked for, what's in the folder, and what a person still owes, and it refuses to say "released" while anything is open.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- Friday's export folder from chapter 119, with the build's log beside it.

I couldn't run the code in FontLab 9. I ran the script in plain Python on a folder laid out like the one chapter 119's build leaves behind. Nothing here asks FontLab for more than the path of the open font, so this chapter leans on FontLab less than any other in the part.

## Step 1: Which folder?

The script needs the folder that was shipped. You have a function for that, `latest_export` from chapters 115 and 116. Here it is again, so these lines run by themselves:

```python
from pathlib import Path

import fly.ap.core.scripting as scripting
from fly import fl


def latest_export(font, package):
    info = package.info
    ending = f"-v{info.versionMajor}.{info.versionMinor:03d}"
    exports = Path(font.path).parent / "exports"
    if not exports.exists():
        return None
    folders = [f for f in sorted(exports.iterdir()) if f.name.endswith(ending)]
    return folders[-1] if folders else None


font = fl.CurrentFont()
print(latest_export(font, scripting.current_package()))
```

```text
None
```

## Step 2: The mistake

`latest_export` looks for the newest folder whose name ends in the font's version. Until Friday that was the right question. Since Friday it's the wrong one, and the reason is chapter 119's own rule: the build gives the font its next number as its last step. The font on Mira's desk says 1.004. The folder that went out says 1.003. There is no folder for 1.004, and there shouldn't be.

Nothing was broken. A function written for one moment was asked at another. The font's version used to mean "what I'm about to ship", and since Friday it means "what I'll ship next". Code that reads a value depends on what the value means, and a meaning can change with no line of that code changing.

So ask a question whose answer doesn't move: which is the newest folder that holds font files?

```python
from pathlib import Path

FORMATS = [".otf", ".ttf"]


def shipped_folder(font):
    exports = Path(font.path).parent / "exports"
    if not exports.exists():
        return None
    found = None
    for folder in sorted(exports.iterdir()):
        if any([p.suffix.lower() in FORMATS for p in folder.rglob("*")]):
            found = folder
    return found
```

`any` with a list is chapter 44's. The folders are sorted by name, and the names start with a date, so the last one that passes is the newest. An empty folder doesn't pass. That matters: run Friday's build once too often and it makes an empty folder for 1.004, and the release must not land there. `build-log.txt` sits in `exports` too, and it's a file. Asking a file for the files inside it gives none, so it doesn't pass either.

## Step 3: Three kinds of line

Every item on a release list is in one of three states, and the list is only honest if it keeps them apart.

**Shipped, or there.** The script can see it: a weight with both its files, a proof page, the copy of the source font, the log saying the build finished.

**Not yet.** Asked for, not delivered, and everybody has agreed why. Thin and ExtraLight need a Thin master. ExtraBold and Black need a Black one. Chapter 107 worked that out and chapter 110 showed what three masters can and can't reach. These lines stay on the list, with their reason, and they don't block the release. Take them off and the list would read "5 of 5", which is true and misleading.

**Open.** Somebody still owes something. One open line and the script won't print "Released."

The third group includes things the script can't see at all. Whether Ines read the proof on paper isn't on the disk. So the script holds a short list of the hand jobs, each with a place for a name:

```python
BY_HAND = [
    ("Text proof read on paper at 9 point", "Ines, 18 Dec"),
    ("Typed in the layout program", ""),
    ("Client told which weights are missing and why", ""),
]
```

An empty name means open. To close a line, a person types who did it and when, in the script, and runs it again. That's all the signing there is. The script can't check that the name is true. What it does is make the claim sit in a file with a name on it, and that's more than a "yes" in an email.

## The whole script

```python
#FLM: Release
# Reads the newest export folder that holds fonts and writes RELEASE.txt
# into it: what was asked for, what is there, and what a person still
# has to do. Changes nothing in the font.
from pathlib import Path

from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


# Chapter 39's tell, written out again so this script runs by itself.
def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


# Chapter 112's key, written out again so this script runs by itself.
def key(text):
    return "".join([c for c in text.lower() if c.isalnum()])


FAMILY = "GG Plum"
FORMATS = [".otf", ".ttf"]
WANTED = ["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold",
          "Bold", "ExtraBold", "Black"]
NOT_YET = {
    "Thin": "needs a Thin master",
    "ExtraLight": "needs a Thin master",
    "ExtraBold": "needs a Black master",
    "Black": "needs a Black master",
}
PAPERS = ["proof-glyphs.html", "proof-text.html"]
BY_HAND = [
    ("Text proof read on paper at 9 point", "Ines, 18 Dec"),
    ("Typed in the layout program", ""),
    ("Client told which weights are missing and why", ""),
]


def shipped_folder(font):
    exports = Path(font.path).parent / "exports"
    if not exports.exists():
        return None
    found = None
    for folder in sorted(exports.iterdir()):
        if any([p.suffix.lower() in FORMATS for p in folder.rglob("*")]):
            found = folder
    return found


def weight_lines(folder):
    stems = {(key(p.stem), p.suffix.lower()) for p in folder.rglob("*")}
    lines, shipped, open_items = [], 0, 0
    for style in WANTED:
        there = [s for s in FORMATS if (key(FAMILY + style), s) in stems]
        if len(there) == len(FORMATS):
            lines.append(f"  shipped   {style}")
            shipped += 1
        elif style in NOT_YET and not there:
            lines.append(f"  not yet   {style}: {NOT_YET[style]}")
        else:
            lines.append(f"  OPEN      {style}: has {' '.join(there) or 'no files'}")
            open_items += 1
    return lines, shipped, open_items


def build_finished(folder):
    log = folder.parent / "build-log.txt"
    if not log.exists():
        return False
    with open(log, encoding="utf-8") as f:
        text = f.read()
    ours = False
    for line in text.splitlines():
        if "half, for" in line:
            ours = line.endswith(f"Second half, for {folder.name}")
        elif ours and line.endswith("Build finished."):
            return True
    return False


def paper_lines(folder, font):
    checks = [(name, (folder / name).exists()) for name in PAPERS]
    checks.append(("copy of the source font", (folder / Path(font.path).name).exists()))
    checks.append(("build finished, by the log", build_finished(folder)))
    lines, open_items = [], 0
    for label, good in checks:
        lines.append(f"  {'there  ' if good else 'OPEN   '}   {label}")
        if not good:
            open_items += 1
    return lines, open_items


def hand_lines():
    lines, open_items = [], 0
    for label, who in BY_HAND:
        if who:
            lines.append(f"  done      {label} ({who})")
        else:
            lines.append(f"  OPEN      {label}")
            open_items += 1
    return lines, open_items


def main():
    font = fl.CurrentFont()
    if font is None or not font.path:
        tell("Open a saved font first.")
        return
    folder = shipped_folder(font)
    if folder is None:
        tell("No export folder holds fonts yet. Run the Friday build.")
        return
    weights, shipped, open_weights = weight_lines(folder)
    papers, open_papers = paper_lines(folder, font)
    hand, open_hand = hand_lines()
    open_items = open_weights + open_papers + open_hand
    lines = [f"Release {folder.name}"]
    lines += [f"Weights: {shipped} of {len(WANTED)} asked for"] + weights
    lines += ["In the folder:"] + papers
    lines += ["By hand:"] + hand
    lines.append("Released." if open_items == 0 else f"Not released: {open_items} open.")
    for line in lines:
        print(line)
    with open(folder / "RELEASE.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


main()
```

Save it as `release.py` and run it:

```text
Release 2026-12-18-v1.003
Weights: 5 of 9 asked for
  not yet   Thin: needs a Thin master
  not yet   ExtraLight: needs a Thin master
  shipped   Light
  shipped   Regular
  shipped   Medium
  shipped   SemiBold
  shipped   Bold
  not yet   ExtraBold: needs a Black master
  not yet   Black: needs a Black master
In the folder:
  there     proof-glyphs.html
  there     proof-text.html
  there     copy of the source font
  there     build finished, by the log
By hand:
  done      Text proof read on paper at 9 point (Ines, 18 Dec)
  OPEN      Typed in the layout program
  OPEN      Client told which weights are missing and why
Not released: 2 open.
```

The same 21 lines are now in `RELEASE.txt` inside the export folder, where anyone who opens the folder finds them.

Notes on the listing.

Almost nothing in it is new, which is the point of a last chapter. Tuples in a list are chapter 36's. The pairs of name and suffix in `weight_lines` are chapter 112's way of matching file names, with `key` so that `GGPlum-SemiBold` and "GG Plum SemiBold" count as the same. `' '.join(there) or 'no files'` is chapter 91's `or` between values. `lines += [...]` is chapter 115's. Reading the log is chapter 27's `with open` and chapter 87's `splitlines`.

Three functions return two or three things at once: the lines to print and a count of open items. `weights, shipped, open_weights = weight_lines(folder)` unpacks them, the way chapter 100 unpacked what each check returned. Each section counts its own open lines and `main` only adds them up. To add a section, write one more function of that shape.

`weight_lines` has three branches, one for each state. A weight is shipped when it has every format in `FORMATS`. It's "not yet" when it has a reason in `NOT_YET` and no files at all. Everything else is open, and that last branch catches two cases with one test: a wanted weight with a file missing, and a weight that's supposed to be absent turning up with a file.

`build_finished` reads the log as a story. It walks the lines and remembers, in `ours`, whether the last "half" line it passed was the second half for this folder. A `Build finished.` line counts only while `ours` is true. The log holds every build there ever was, and a finish that belongs to another folder says nothing about this one.

The script reads no font file and changes nothing in the font. Chapter 118's script inspects the files and chapter 114's checks the font, and Friday's build ran both. This one trusts the log for that, and says so in its line: "by the log".

## Mira's Monday

She opens the layout program, sets a paragraph in each of the five weights, and prints it. The Light holds at 9 point. She types her name into the second line.

Then she writes to the art director, not the assistant. "Five of the nine weights are in Friday's folder: Light, Regular, Medium, SemiBold and Bold. Thin, ExtraLight, ExtraBold and Black need two new drawings of the whole alphabet, one lighter than the Light and one heavier than the Bold. I can start on those in January. The list in the folder says the same."

She types her name into the third line and runs the script once more:

```text
  done      Text proof read on paper at 9 point (Ines, 18 Dec)
  done      Typed in the layout program (Mira, 21 Dec)
  done      Client told which weights are missing and why (Mira, 21 Dec)
Released.
```

Then she answers the assistant. "Yes. Five weights, and `RELEASE.txt` in the folder says which."

## Break it on purpose

Go into Friday's folder and move `GGPlum-Medium.ttf` to the desktop. Run:

```text
Weights: 4 of 9 asked for
```

and, further down:

```text
  OPEN      Medium: has .otf
```

and the last line counts one more open item. The file was there on Friday, when the build checked. The release script looks again, because a folder can change after a build, and a release is a claim about the folder as it is now. Put the file back.

Now copy `GGPlum-Light.otf`, in the same `otf` folder, and name the copy `GGPlum-Thin.otf`. Run:

```text
  OPEN      Thin: has .otf
```

Thin has a reason for being absent, and here it's present. The script could have counted that as good news. It doesn't, because a file nobody meant to ship is a problem of its own: the client would install a Thin that's a Light under another name. Delete the copy.

## What you learned

A release list has three kinds of line: what's there, what's agreed to be missing and why, and what somebody still owes. A script can check the first kind on the disk, can keep the second kind from being forgotten, and can only hold a place for the third, with a name in it. A function that reads a value depends on what the value means, so when the build began to bump the version, "the folder for the font's version" stopped being the shipped one. Putting a part together takes few new ideas: several functions that return their lines and a count, and a `main` that adds up.

## Try it yourself

1. Add a fourth hand job, "Old version removed from the client's server", and watch the count of open items change.
2. Print, under the first line, the date of the release taken from the folder's name. The first ten characters of `folder.name` are the date.
3. Move `BY_HAND` out of the script into a text file in the export folder, one job to a line, with the name after a `|`. Read it with chapter 27's loop and `split("|")`. Which is better kept in the script, and which beside the fonts?

## Next

Five weights are out, with a list that says so. Part 7 turns around and looks at the scripts themselves. Mira is one of two people at Halfmoon who can run them, and the other is on holiday. Chapter 121 gives a script a window with a button, so that somebody who has never opened the Scripting panel can use it.
