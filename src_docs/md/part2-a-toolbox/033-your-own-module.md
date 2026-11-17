---
this_file: src_docs/md/part2-a-toolbox/033-your-own-module.md
---

# 33. Your own module

Tuesday. Ines changes her mind about green. The approved glyphs are hard to tell from the yellow ones on her laptop, so from today "done" is a bluer green, number 151.

Mira opens `status_marks.py` and changes one line, which is what constants are for. Then she remembers that `mark_empty.py` has a `GREEN` in it too, and so does the script from the exercise in chapter 14, and so does something she wrote on a Friday afternoon and called `test2.py`. She pasted the same three lines into each of them. Now she has four copies of one fact, and three of them are out of date.

The same has happened to `widest_glyph` and `is_empty`. Every script that needs them carries its own copy, and the copies have started to differ.

Functions cured copying inside one script. Today's cure is for copying between scripts: one file that holds the shared parts, which every other script borrows from.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `status_marks.py` from [chapter 32](032-tags-and-marks.md).
- Your `Friday Report.py` from [chapter 18](../part1-first-words/018-save-it-run-it-again.md).

## Step 1: You've been doing this since chapter 4

Look at the first line of nearly every script you've written:

```python
from fly import fl
```

In chapter 4 I asked you to type this line on trust. Here's what it does. Somewhere on your disk there's a folder called `fly` with Python files in it. Somebody wrote functions and boxes in those files, exactly as you write them. `import` finds the files, runs them once and hands you what they define.

A Python file that's meant to be borrowed from, and not run by itself, is called a **module**. `csv` is a module. So is `pathlib`. Neither is part of the language. They're files that came with Python, written by people, and you can open them and read them.

So you can write one too. A module is a text file whose name ends in `.py`. The only question is where to put it.

## Step 2: Where Python looks

When you write `import csv`, Python doesn't search your whole disk. It has a short list of folders, and it looks in each one in turn. You can read the list:

```python
import sys

for folder in sys.path:
    print(folder)
```

`sys` is one more module that comes with Python, and `sys.path` is a plain list of strings. Your list will differ from mine in its details. On a Mac it has lines like these in it:

```text
/Applications/FontLab 9.app/Contents/Resources/python3.11/lib/python3.11
/Users/mira/Library/Application Support/FontLab/FontLab 9/python/3.11/site-packages
```

Find the line that ends in `site-packages` and sits inside your own user folder. That's where the installer put Fly in chapter 4. It's a folder that belongs to you, FontLab's Python looks in it, and a FontLab update shouldn't empty it. That's where your module goes.

To open that folder without hunting for it, print it so you can copy it:

```python
import sys

for folder in sys.path:
    if folder.endswith("site-packages"):
        print(folder)
```

If that prints two lines, take the one with your name in it. On a Mac, copy the line, switch to the Finder, choose **Go > Go to Folder…** and paste. On Windows, paste it into the address bar of an Explorer window.

## Step 3: Write the module

In the Scripting panel, start a new script and type this. It's everything that Mira's scripts share so far:

```python
# Shared tools for Halfmoon Type scripts.
# Borrow from it with: import halfmoon
from fly.tr.proxy.fl.objects.glyph import pGlyph

RED = 1
YELLOW = 61
GREEN = 151

LEGEND = {
    0: "untouched",
    RED: "not-drawn",
    YELLOW: "needs-work",
    GREEN: "done",
}


def rich(font, glyph):
    return pGlyph(font, glyph)


def is_empty(font, glyph):
    return rich(font, glyph).isEmpty()


def widest_glyph(font):
    widest = font[0]
    for glyph in font.glyphs:
        if glyph.width > widest.width:
            widest = glyph
    return widest
```

Save it with the name `halfmoon.py` in the `site-packages` folder from Step 2. The name matters: all lowercase, no spaces, no hyphen, and not a name Python already uses. Call it `csv.py` and `import csv` will go on giving you Python's own, because that folder comes first in the list. Yours would never be found.

Now run it. Nothing is printed, and that's correct. The file defines three boxes, a dictionary and three functions, and then it ends. It never calls any of them. A module is a shelf of tools, and running it only puts the tools on the shelf.

Notice the import at the top. A module does its own importing. `halfmoon.py` needs `pGlyph`, so it says so, and a script that borrows from `halfmoon` doesn't have to know that.

`rich` is the smallest function you've written: one line that calls something and returns what it gets. It earns its place anyway. `pGlyph(font, glyph)` was in several of Mira's scripts, along with that long import line. Now the long line lives in one file.

## Step 4: Borrow from it

Start another new script:

```python
from fly import fl
import halfmoon

font = fl.CurrentFont()
print(halfmoon.GREEN)
print(halfmoon.widest_glyph(font).name)
print(halfmoon.is_empty(font, font["a.sc"]))
```

```text
151
emdash
True
```

The dot is the same dot as always. `halfmoon` is an object, with drawers, and its drawers are the names the file defined. `halfmoon.GREEN` opens the drawer called `GREEN`. `halfmoon.widest_glyph(font)` takes the function out of its drawer and calls it.

You can also take one name out and keep it on your own desk:

```python
from halfmoon import GREEN, widest_glyph

print(GREEN)
print(widest_glyph(font).name)
```

That's the shape of `from fly import fl`, which you now can read in full: from the module `fly`, take the name `fl`.

Which of the two is better? For your own module, I'd use `import halfmoon` and write the dots. `halfmoon.GREEN` says where the green comes from. Six months from now a bare `GREEN` in line 60 of a script will send you looking for its definition, and it won't be in that file.

If the import fails, you'll see this:

```text
ModuleNotFoundError: No module named 'halfmoon'
```

Python went through every folder in `sys.path` and found no `halfmoon.py`. Either the file is in a folder that isn't on the list, or its name isn't what you think it is. Look for a capital `H`, or for `halfmoon.py.txt`.

## Step 5: The edit that doesn't take

Ines's question from yesterday was whether the Friday report could count statuses. That's the tally loop from chapter 32, and it belongs in the module. Open `halfmoon.py` and add a function at the bottom:

```python
def status_tally(font):
    tally = {}
    for glyph in font.glyphs:
        status = LEGEND.get(rich(font, glyph).mark, "unknown-color")
        tally[status] = tally.get(status, 0) + 1
    return tally
```

Save it. Go back to the other script and use it:

```python
from fly import fl
import halfmoon

font = fl.CurrentFont()
print(halfmoon.status_tally(font))
```

```text
AttributeError: module 'halfmoon' has no attribute 'status_tally'
```

The function is in the file. You can see it. You saved. And Python says it isn't there.

Everybody who writes a module walks into this in the first hour. I said in Step 1 that `import` runs the file once. It means once. The first `import halfmoon` read the file and built the module. Every later `import halfmoon`, in this script or any other, gets the module that's already built. Python doesn't look at the file again. It does this for speed, and it's a sound rule for `csv`, which doesn't change while you work. For a module you're in the middle of writing, it means FontLab is still holding yesterday's copy.

A script in the Scripting panel is read each time you run it. A module isn't. That's why you've never met the problem before.

There are two ways out. Quitting FontLab and starting it again always works, since a new session has nothing built. The quicker way is to ask for a fresh read:

```python
from fly import fl
import importlib
import halfmoon

importlib.reload(halfmoon)

font = fl.CurrentFont()
print(halfmoon.status_tally(font))
```

```text
{'untouched': 197, 'unknown-color': 10, 'needs-work': 3, 'not-drawn': 3}
```

`importlib.reload(halfmoon)` reads the file again and rebuilds the module in place. Keep that line in while you're working on the module, and take it out when the module has settled.

The function is found. Now read what it found: ten glyphs in an unknown color and none done. That's correct too. The module says done is 151, and the nine green cells in your practice font were painted 121 in chapter 32. Ines's new green is a decision for the studio's Plum, where somebody will repaint the cells. Your practice font keeps the old one.

Change `GREEN` back to 121 in `halfmoon.py`, save, and run the script again. The reload line is still in it, so the change takes:

```text
{'untouched': 197, 'done': 9, 'unknown-color': 1, 'needs-work': 3, 'not-drawn': 3}
```

The pairs come in the order the font first showed each status: `A` is green and comes before the odd `Q`, which comes before the yellow `a`.

## Step 6: Thin scripts

Now look at what's left of `status_marks.py` when the module does the shared work:

```python
# Reports how many glyphs have each of Ines's statuses.
from fly import fl
import halfmoon

font = fl.CurrentFont()
tally = halfmoon.status_tally(font)

for status in halfmoon.LEGEND.values():
    print(f"{status:<14}{tally.get(status, 0):>4}")
print(f"{'unknown-color':<14}{tally.get('unknown-color', 0):>4}")
```

```text
untouched      197
not-drawn        3
needs-work       3
done             9
unknown-color    1
```

Seven lines and a comment, and they say what the script is for. The rest of the work is in the module.

Do the same to `Friday Report.py`. Delete its own `widest_glyph`, add `import halfmoon`, and call `halfmoon.widest_glyph(font)`. Then give Ines her statuses. The report goes to a file, so the new lines belong inside the `with` block, indented to match the lines already there, and each `print` needs its `file=f`:

```python
        tally = halfmoon.status_tally(font)
        for status in halfmoon.LEGEND.values():
            print(f"{status:<14}{tally.get(status, 0):>4}", file=f)
        print(f"{'unknown-color':<14}{tally.get('unknown-color', 0):>4}", file=f)
```

Leave off `file=f` and those lines go to the Output panel while the file stays as it was. The file in the Scripts folder is still the thing you click in the menu, and `halfmoon.py` stays in the folder Python searches. One is a script you run. The other is a module you borrow from.

That's the rule for what goes where. If two scripts need the same function, the same constant or the same legend, it goes in the module. Whatever makes this script different from that one stays in the script.

??? info "Going deeper: lines that run only when a module is run directly"
    A module can hold a few lines that run only when you run the file directly, and not when another script imports it. You'll see them in other people's modules, looking like this:

    ```python
    if __name__ == "__main__":
        print(LEGEND)
    ```

    Python puts the name of each module in a box called `__name__`. For the file you ran, the box holds `"__main__"`. For a file that was imported, it holds the module's own name. People use those lines for a quick test of the module. You can leave them alone for now.

## The whole module

`halfmoon.py`, as it stands today:

```python
# Shared tools for Halfmoon Type scripts.
# Borrow from it with: import halfmoon
from fly.tr.proxy.fl.objects.glyph import pGlyph

RED = 1
YELLOW = 61
GREEN = 121

LEGEND = {
    0: "untouched",
    RED: "not-drawn",
    YELLOW: "needs-work",
    GREEN: "done",
}


def rich(font, glyph):
    return pGlyph(font, glyph)


def is_empty(font, glyph):
    return rich(font, glyph).isEmpty()


def widest_glyph(font):
    widest = font[0]
    for glyph in font.glyphs:
        if glyph.width > widest.width:
            widest = glyph
    return widest


def status_tally(font):
    tally = {}
    for glyph in font.glyphs:
        status = LEGEND.get(rich(font, glyph).mark, "unknown-color")
        tally[status] = tally.get(status, 0) + 1
    return tally
```

It will grow. From here on, when a chapter writes a function that more than one script could use, I'll say "put it in `halfmoon.py`", and you'll know what that means.

In the studio's copy Mira changes one line, `GREEN = 151`, in one file, and repaints nine cells. Yours stays at 121, to match the cells you painted. Then she deletes `test2.py`.

## What you learned

A module is a Python file that other scripts borrow from with `import`, and its functions and constants are reached with a dot. Python looks for modules only in the folders listed in `sys.path`, and it reads each one once per session, so an edited module needs `importlib.reload` or a restart of FontLab. Keep what scripts share in the module and what makes a script different in the script.

## Try it yourself

1. Move `names_without_unicode(font)` from your Friday report into `halfmoon.py`, and change the report to call it with the dot. Run the report before and after. The output shouldn't change by a single character, and that's the test of whether you moved it correctly.
2. Add a constant `UNKNOWN = "unknown-color"` to the module and use it in `status_tally`. Then use `halfmoon.UNKNOWN` in the thin script too. How many places hold that word now?
3. Rename `halfmoon.py` to `Halfmoon Tools.py` and run `import halfmoon` again. Why does it still work? Now run `importlib.reload(halfmoon)` and read the error. Then try `import Halfmoon Tools` and read that one. Which of the two errors comes from Python looking for a file, and which comes before it looks at all? Put the name back when you're done.

## Next

`widest_glyph(font)` always looks at every glyph. Mira wants it to look at only the selected ones, sometimes. Chapter 34 gives functions arguments that you may leave out.
