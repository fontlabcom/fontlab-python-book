---
this_file: src_docs/md/part7-tools/138-pictures-of-your-work.md
---

# 138. Pictures of your work

It's Friday 8 January. The build ran this morning, at the second attempt, from Ines's terminal and then from the Scripts menu, and there's a folder called `2027-01-08-v1.004` with ten fonts in it.

The release notes want two pictures: the specimen word, and the `n` with Mira's sidebearing numbers under it. Last time she took them by hand. Press the keys, drag a rectangle, miss by a few pixels, drag again, find the file on the desktop, rename it, move it. Two pictures took ten minutes, and the two rectangles weren't the same size.

Somebody has already written a tool that photographs FontLab's windows. Today your script calls it, keeps the two files it needs out of the eight it's given, and puts them where the release lives.

## What you need

`Plum-practice` open, and an export folder with fonts in it, from chapter 119. `release.py` from chapter 120. And GrabLab, which comes as a folder called `fontlab-grablab` from the same place as Fly. It has an `install.vfpy` of the kind you met in chapter 133: drag it onto FontLab, then restart.

GrabLab isn't in Fly's toolbag, so today's script imports it by its own name, `grablab`. That makes it the second and last exception to the rule from chapter 4, after yesterday's. Yesterday's script ran outside FontLab. This one runs inside, and the reason is plainer: Fly has no alias for it.

I haven't run this chapter in FontLab 9, and a chapter about pictures is the one where that matters most, because I have no picture to show you. I read GrabLab's code to learn what it's called with and what it hands back, and ran `release_shots.py` against a stand-in that makes empty files with the names GrabLab's code builds. The printed lines below are from those runs. What the pictures look like, you'll see and I haven't.

## Step 1: Ask for pictures

Open two Glyph windows. In one, the `n`, with chapter 134's Sidebearings reporter switched on. In the other, type the specimen word.

Then, in the Scripting panel:

```python
from grablab import Grab

grab = Grab()
grab.newGrab()
paths = grab.grabGlyphWindows()
print(len(paths))
```

`Grab()` makes a grabber. `newGrab` starts a new set of pictures: it makes a folder for them, named with the date and time, inside a folder called GrabLab in your Pictures folder. `grabGlyphWindows` photographs every Glyph window that's showing and returns a list of the files it wrote.

Leave out the second line and you get the first mistake most people make with this tool:

```text
AttributeError: 'Grab' object has no attribute 'grab_folder'
```

The message is true and no help. It's GrabLab's own inside showing: the folder is set up by `newGrab`, and nothing has set it. When somebody else's tool gives you an `AttributeError` about a name you never typed, the usual cause is a step you skipped. Their README lists the steps in order.

## Step 2: Count what came back

With two Glyph windows open, I expect `print(len(paths))` to say:

```text
8
```

You asked for two pictures. GrabLab was written for people who document software, and it's generous. For each window it takes the drawing area alone and then the whole window with its title bar and toolbars, and it saves each of those as a PNG picture and as an SVG drawing. That's two windows, two views and two formats.

Print the names to see the pattern:

```python
from pathlib import Path

for path in paths:
    print(Path(path).name)
```

Each name starts with `fl_`, then two letters for what was photographed: `gv` for a Glyph window's drawing area, `gw` for the whole window. Then come the window's title, the time, and the font's name. If your FontLab is set to its dark look, the letters get a `d`: `gvd` and `gwd`.

This is what calling another tool is like. Inside your own module you decided what every function returns. Here somebody else decided, for their reasons, and the names of the files are the only description you get. So you write a small function that says what you want out of what you're given.

## Step 3: Keep two of eight

```python
from pathlib import Path

KEEP = ["fl_gv_", "fl_gvd_"]


def wanted(paths):
    found = []
    for path in paths:
        path = Path(path)
        if path.suffix == ".png" and any([path.name.startswith(kind) for kind in KEEP]):
            found.append(path)
    return sorted(found)
```

`Path(path)` is a precaution. GrabLab's code hands back `Path` objects today, but its documents only say "file paths", and wrapping a `Path` in `Path` costs nothing. `any` with a list is chapter 44's, and `startswith` is chapter 9's.

The list comes back sorted for the reason chapter 136 gave: the order windows are photographed in is GrabLab's business, and the order of your release pictures should be yours.

You can also ask for less in the first place. `Grab` takes settings by name, and `Grab(grab_svg=False)` makes a grabber that doesn't write the SVG drawings. That halves the eight. I haven't seen whether the choice outlasts the script and changes what GrabLab's own menu commands write. The filter stays, because the whole-window pictures still come.

## Step 4: Borrow the folder

The pictures belong in the release folder. Chapter 120's `release.py` has a function that finds it, `shipped_folder`, and the natural line is `import release`.

Try it and the release summary prints, all 21 lines, and `RELEASE.txt` is written again. `release.py` ends with a bare `main()`, so importing it runs it. You've met this three times, in chapters 114, 119 and 132, and the cure is the same. Open `release.py` and change its last line to:

```python
if __name__ == "__main__":
    main()
```

Now it runs when it's run and keeps quiet when it's borrowed. A script you may one day borrow from should end this way from the start.

## The whole script

```python
#FLM: Release Shots
# Photographs every open Glyph window and copies the pictures into the
# newest export folder, in a subfolder called shots.
import shutil
from pathlib import Path

import halfmoon
import release
from fly import fl
from grablab import Grab

KEEP = ["fl_gv_", "fl_gvd_"]


def wanted(paths):
    found = []
    for path in paths:
        path = Path(path)
        if path.suffix == ".png" and any([path.name.startswith(kind) for kind in KEEP]):
            found.append(path)
    return sorted(found)


def copy_shots(shots, folder):
    target = folder / "shots"
    target.mkdir(exist_ok=True)
    number = len(list(target.glob("*.png")))
    copied = []
    for shot in shots:
        number += 1
        copy = target / f"{folder.name}-shot{number}.png"
        shutil.copy(shot, copy)
        copied.append(copy)
    return copied


def main():
    font = fl.CurrentFont()
    if font is None or not font.path:
        halfmoon.tell("Open a saved font first.")
        return 1
    folder = release.shipped_folder(font)
    if folder is None:
        halfmoon.tell("No export folder holds fonts yet. Run the Friday build.")
        return 1
    grab = Grab(grab_svg=False)
    grab.newGrab()
    shots = wanted(grab.grabGlyphWindows())
    if not shots:
        print("No Glyph window to photograph. Open one and run this again.")
        return 1
    for copy in copy_shots(shots, folder):
        print(copy.name)
    print(f"{len(shots)} pictures in {folder.name}/shots")
    return 0


if __name__ == "__main__":
    main()
```

Save it as `release_shots.py`, beside `release.py`.

`copy_shots` copies; it doesn't move. GrabLab's originals stay in Pictures, with their sidecar files beside them. Each picture GrabLab takes has two small text files with the same name that record sizes and what was photographed. Leave them where they are.

The copies get names of your choosing: the folder's name, then `shot1`, `shot2`. The count starts from the number of PNG files already in `shots`, so a second run adds `shot3` and `shot4` and replaces nothing. GrabLab itself never writes over a file, and it's a good habit to copy from it along with the pictures.

`main` returns 1 for "didn't happen" and 0 for "done", as the Friday scripts have since chapter 119, so this one can join a list of steps later.

## Run it

With the two Glyph windows open:

```text
2027-01-08-v1.004-shot1.png
2027-01-08-v1.004-shot2.png
2 pictures in 2027-01-08-v1.004/shots
```

Open the `shots` folder and look at them. Which window became `shot1` depends on how the two window titles sort, which I haven't seen. I expect the drawing area and nothing else, with the reporter's numbers under the `n` if the reporter was on.

Then check two things I can't check for you. Is the picture sharp enough for the notes? On a high-resolution screen a picture has twice as many pixels each way as the window's size suggests. And did the grab leave your windows as it found them? GrabLab changes a few display settings while it works and puts them back. If anything looks different afterwards, tell me.

Run it a second time:

```text
2027-01-08-v1.004-shot3.png
2027-01-08-v1.004-shot4.png
2 pictures in 2027-01-08-v1.004/shots
```

Mira has four pictures and wants two, so she deletes the first pair, where the `n` was too small. The second pair goes into the notes. Both were taken the same way and are the same kind of picture, and it took a few seconds.

## Break it on purpose

Close both Glyph windows, so that only the Font window is open, and run the script:

```text
No Glyph window to photograph. Open one and run this again.
```

`grabGlyphWindows` didn't complain. It photographed every Glyph window, there were none, and it returned an empty list. An empty list from somebody else's tool is a result your script has to expect. Without the `if not shots:` lines the script would have made an empty `shots` folder and printed "0 pictures", which looks like success.

Now a quieter break. In `KEEP`, delete `"fl_gvd_"`, switch FontLab to its dark look, open a Glyph window and run it. You get the same "No Glyph window" line, with a window open in front of you. The files were written, under names your filter no longer knows. A filter on names is a guess about somebody else's naming. When it finds nothing, print one of the names it was given and read it. Put the entry back.

## What you learned

Calling another person's tool means working with their choices: their order of steps, their folder, their file names, and more results than you asked for. You read their documents for the steps, look at what comes back before you trust it, and write one small function that keeps what you need. An empty answer is an answer and needs its own message. A script you might borrow from should guard its `main()`. When your script copies files for people to read, it gives them names you chose and doesn't write over what's there.

## Try it yourself

1. Add `"fl_gw_"` and `"fl_gwd_"` to a second list, and make the script copy whole-window pictures into a subfolder called `windows`.
2. `grab.grabFontWindows()` photographs Font windows. Add one picture of the Font window to the shots, and decide what it should be called.
3. Add "Pictures" to chapter 137's `HALVES`, after "Text proof". Then think about whether it belongs there: what did step 3 of that chapter say about jobs with a time limit, and how long does a photograph take? Time it before you decide.

## Next

This morning's build stopped the first time through, at the glyph proof. Days earlier somebody had changed one function in `halfmoon.py`, three scripts that use it stopped working, and nobody knew until today. Chapter 139 writes down what your functions are supposed to do, in a form Python can check in two seconds, without opening FontLab.
