---
this_file: src_docs/md/part2-a-toolbox/033-your-own-module.md
---

# 33. Your own module

Tuesday. Ines changes her mind about green. The approved glyphs are hard to tell from the yellow ones on her laptop, so from today "done" is a bluer green, number 151.

Mira opens `status_marks.py` and changes one line, which is what constants are for. Then she remembers that `mark_empty.py` has a `GREEN` in it too, and so does the script from the exercise in chapter 14, and so does something she wrote on a Friday afternoon and called `test2.py`. She pasted the same three lines into each of them. Now she has four copies of one fact, and three of them are out of date.

The same has happened to `widest_glyph` and `is_empty`. Every script that needs them carries its own copy, and the copies have started to differ.

Python's answer to copying between scripts is the module: one file that holds the shared parts, which other scripts borrow from. You've used modules since chapter 4 without calling them that. Today you find out how they work, write a small one, and see what it costs.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `status_marks.py` from [chapter 32](032-tags-and-marks.md).
- Your `Friday Report.py` from [chapter 18](../part1-first-words/018-save-it-run-it-again.md), for the first exercise.

## Step 1: You've been doing this since chapter 4

Look at the first line of nearly every script you've written:

```python
from fly import fl
```

In chapter 4 I asked you to type this line on trust. Here's what it does. Somewhere on your disk there's a folder called `fly` with Python files in it. Somebody wrote functions and boxes in those files, exactly as you write them. `import` finds the files, runs them once and hands you what they define.

A Python file that's meant to be borrowed from, and not run by itself, is called a **module**. `csv` is a module. So is `pathlib`. Neither is part of the language. They're files that came with Python, written by people, and you can open them and read them.

## Step 2: Two ways to borrow

There are two shapes of import, and you've met both. Here they are side by side, with two modules that come with Python:

```python
import json
from pathlib import Path

print(json.dumps({"done": 9}))
print(Path.home())
```

```text
{"done": 9}
/Users/mira
```

`import json` hands you the whole module under its own name. You reach inside it with a dot: `json.dumps` opens the drawer called `dumps` and calls what's in it. The dot is the same dot as always. A module is an object, and its drawers are the names its file defined.

`from pathlib import Path` reaches in once, takes out one name and puts it on your desk. After that you write `Path` and not `pathlib.Path`. That's the shape of `from fly import fl`, which you can now read in full: from the module `fly`, take the name `fl`.

A module can hold other modules, the way a folder holds folders. The long line from chapter 8 is a path of that kind:

```python
from fly.tr.proxy.fl.objects.glyph import pGlyph
```

Read it from the left. In `fly` there's `tr`, which is TypeRig. In TypeRig there's `proxy`, in that there's `fl`, then `objects`, and in that a file called `glyph.py`. From that file, take `pGlyph`. Every dot is one step into a folder, and the last step is a file.

When the path is long and you want the whole module and not one name from it, you can give it a short name with `as`. Chapter 15 did this:

```python
import fly.ap.core.scripting as scripting
```

That's the module `scripting`, four folders down inside FontLab's own app code, called `scripting` from here on.

Which shape is better? Use the dot when the name alone wouldn't tell a reader where it came from. `json.dumps` says it's JSON's. A bare `dumps` in line 60 of a script would send you hunting. Use `from` when the name is clear by itself, like `Path` or `pGlyph`, or when the dotted path is too long to write twice.

## Step 3: Where Python looks

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

Find the line that ends in `site-packages` and sits inside your own user folder. That's where the installer put Fly in chapter 4. It's a folder that belongs to you, FontLab's Python looks in it, and a FontLab update shouldn't empty it.

To open that folder without hunting for it, print it so you can copy it:

```python
import sys

for folder in sys.path:
    if folder.endswith("site-packages"):
        print(folder)
```

If that prints two lines, take the one with your name in it. On a Mac, copy the line, switch to the Finder, choose **Go > Go to Folder…** and paste. On Windows, paste it into the address bar of an Explorer window.

If Python goes through every folder on the list and finds nothing, you get this:

```python
import jsno
```

```text
ModuleNotFoundError: No module named 'jsno'
```

Read the name in quotes first. Nine times in ten it's a typing slip. The tenth time, the module really isn't in any folder on the list.

## Step 4: Write a small one

A module is a text file whose name ends in `.py`, in one of those folders. To see how that works from the inside, write a small one. In the Scripting panel, start a new script and type this:

```python
# Ines's status colors, for trying out modules.
RED = 1
YELLOW = 61
GREEN = 151

LEGEND = {
    0: "untouched",
    RED: "not-drawn",
    YELLOW: "needs-work",
    GREEN: "done",
}
```

Save it with the name `studio_marks.py` in the `site-packages` folder from Step 3. The name matters: all lowercase, no spaces, no hyphen, and not a name Python already uses. Call it `csv.py` and `import csv` will go on giving you Python's own, because that folder comes first in the list. Yours would never be found.

Now run it. Nothing is printed, and that's correct. The file defines three boxes and a dictionary, and then it ends. A module is a shelf, and running it only puts things on the shelf.

Start another new script and borrow from it:

```python
import studio_marks

print(studio_marks.GREEN)
print(studio_marks.LEGEND[studio_marks.GREEN])
```

```text
151
done
```

That's all a module of your own is. Nothing about `studio_marks.py` is different from `json` or `fly`, apart from who wrote it.

## Step 5: The edit that doesn't take

Ines's question from yesterday was whether the Friday report could count statuses. That's the tally loop from chapter 32. Open `studio_marks.py`, add two lines at the top and a function at the bottom, so that the whole file reads:

```python
# Ines's status colors, for trying out modules.
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


def status_tally(font):
    tally = {}
    for glyph in font.glyphs:
        status = LEGEND.get(pGlyph(font, glyph).mark, "unknown-color")
        tally[status] = tally.get(status, 0) + 1
    return tally
```

Notice the import at the top. A module does its own importing. `status_tally` needs `pGlyph`, so the module says so, and a script that borrows from it doesn't have to know.

Save it. Go back to the other script and use the new function:

```python
from fly import fl
import studio_marks

font = fl.CurrentFont()
print(studio_marks.status_tally(font))
```

```text
AttributeError: module 'studio_marks' has no attribute 'status_tally'
```

The function is in the file. You can see it. You saved. And Python says it isn't there.

Everybody who writes a module walks into this in the first hour. I said in Step 1 that `import` runs the file once. It means once. The first `import studio_marks` read the file and built the module. Every later `import studio_marks`, in this script or any other, gets the module that's already built. Python doesn't look at the file again. It does this for speed, and it's a sound rule for `json`, which doesn't change while you work. For a module you're in the middle of writing, it means FontLab is still holding the old copy.

A script in the Scripting panel is read each time you run it. A module isn't. That's why you've never met the problem before.

There are two ways out. Quitting FontLab and starting it again always works, since a new session has nothing built. The quicker way is to ask for a fresh read:

```python
from fly import fl
import importlib
import studio_marks

importlib.reload(studio_marks)

font = fl.CurrentFont()
print(studio_marks.status_tally(font))
```

```text
{'untouched': 197, 'unknown-color': 10, 'needs-work': 3, 'not-drawn': 3}
```

`importlib.reload(studio_marks)` reads the file again and rebuilds the module in place. `importlib` is one more module that comes with Python. Keep that line in while you're working on a module, and take it out when the module has settled.

The function is found. Now read what it found: ten glyphs in an unknown color and none done. That's correct too. The module says done is 151, and the nine green cells in your practice font were painted 121 in chapter 32. Ines's new green is a decision for the studio's Plum, where somebody will repaint the cells. Your practice font keeps the old one.

Change `GREEN` back to 121 in `studio_marks.py`, save, and run the script again. The reload line is still in it, so the change takes:

```text
{'untouched': 197, 'done': 9, 'unknown-color': 1, 'needs-work': 3, 'not-drawn': 3}
```

The pairs come in the order the font first showed each status: `A` is green and comes before the odd `Q`, which comes before the yellow `a`.

??? info "Going deeper: lines that run only when a module is run directly"
    A module can hold a few lines that run only when you run the file directly, and not when another script imports it. You'll see them in other people's modules, looking like this:

    ```python
    if __name__ == "__main__":
        print(LEGEND)
    ```

    Python puts the name of each module in a box called `__name__`. For the file you ran, the box holds `"__main__"`. For a file that was imported, it holds the module's own name. People use those lines for a quick test of the module. You can leave them alone for now.

## Step 6: What a module of your own costs

Now look at what's left of `status_marks.py` when the module does the shared work:

```python
# Reports how many glyphs have each of Ines's statuses.
from fly import fl
import studio_marks

font = fl.CurrentFont()
tally = studio_marks.status_tally(font)

for status in studio_marks.LEGEND.values():
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

Seven lines and a comment. It's short, and the green lives in one place.

Now Mira sends this script to Ines, who runs it on her laptop:

```text
ModuleNotFoundError: No module named 'studio_marks'
```

Of course. `studio_marks.py` is in Mira's `site-packages` folder, not in Ines's. The thin script only works on a machine that has the module, and the module is a file you have to remember to copy along with it, and to copy again every time it changes. The same goes for anyone who picks up one of your scripts a year from now on a new computer.

So there's a trade. A module of your own keeps a fact in one place, and a script that carries its own copy runs anywhere Fly is installed. For a few scripts on one machine, the copies are easier. For a set of tools that a whole studio uses, a module is right, and chapter 133 shows how to pack one up properly so that it travels.

This book takes the first side until then. Every listing from here on carries the functions it needs, so you can open any chapter and run its scripts without anything from an earlier one. When a function comes back, I'll say where you first wrote it, and paste it again. Chapter 40 gathers the most useful ones in one place, ready to paste.

`studio_marks.py` was for learning. No later chapter imports it, and you can delete it from `site-packages` whenever you like.

In the studio's copies Mira changes `GREEN = 151` in four places, puts the constants at the top of each script where she'll see them next time, and repaints nine cells. Yours stay at 121, to match the cells you painted. Then she deletes `test2.py`.

## What you learned

A module is a Python file that other scripts borrow from with `import`. `import json` hands you the whole module and you reach in with a dot. `from pathlib import Path` takes one name out. Dots in an import path are steps into folders, and `as` gives a long path a short name. Python looks for modules only in the folders listed in `sys.path`, and says `ModuleNotFoundError` when it finds nothing. It reads each module once per session, so a module you've edited needs `importlib.reload` or a restart of FontLab, or you get an `AttributeError` for the name you just added. A module of your own has to travel with every script that imports it.

## Try it yourself

1. Copy `names_without_unicode(font)` from your Friday report into `studio_marks.py`, reload, and call it from a new script as `studio_marks.names_without_unicode(font)`. The output should match the report's line for line. Then ask yourself what Ines would need on her laptop to run that new script.
2. Add a constant `UNKNOWN = "unknown-color"` to the module and use it in `status_tally`. Then use `studio_marks.UNKNOWN` in the thin script too. How many places hold that word now?
3. Rename `studio_marks.py` to `Studio Marks.py` and run `import studio_marks` again. Why does it still work? Now run `importlib.reload(studio_marks)` and read the error. Then try `import Studio Marks` and read that one. Which of the two errors comes from Python looking for a file, and which comes before it looks at all? Put the name back when you're done.

## Next

`widest_glyph(font)` always looks at every glyph. Mira wants it to look at only the selected ones, sometimes. Chapter 34 gives functions arguments that you may leave out.
