---
this_file: src_docs/md/part7-tools/125-lists-and-choices.md
---

# 125. Lists and choices

Thursday, eleven o'clock. Mira's bag is by the door and her train is at noon. Ines has the Shift window open and is typing `a.ss01 g.ss01 y.ss01` into the names field for the third time.

"Why am I telling it what's in the font? It has the font."

She's right. A field is for things only the person knows, like how many units to add. The glyph names are already in the file, and a window that makes you type them is asking you to do its reading for it. Today's window reads the font, works out which suffixes its glyph names carry, and offers them in a list to pick from. Pick one and it shows the glyphs that have it.

## What you need

`Plum-practice` open, Fly installed, and `shift_dialog.py` from chapter 124 to copy from. Today's script changes nothing in the font.

I haven't run this chapter in FontLab 9. I ran the script in plain Python with stand-in widgets, for a font with the glyphs yours should have after Part 5. The two widgets that are new today are used the same way in the tools that come with Fly, so the calls are copied from working code, but I haven't watched them work.

## Step 1: Group the names

Before any window, the data. You want a dictionary with one key for each suffix, and under each key the list of glyph names that end in it. That's the grouping from chapter 100 again:

```python
from fly import fl


def by_suffix(names):
    groups = {}
    for name in names:
        parts = name.split(".")
        if len(parts) < 2 or parts[0] == "":
            continue
        suffix = parts[-1]
        if suffix not in groups:
            groups[suffix] = []
        groups[suffix].append(name)
    return groups


font = fl.CurrentFont()
groups = by_suffix([glyph.name for glyph in font.glyphs])
for suffix in sorted(groups):
    print(suffix, len(groups[suffix]))
```

```text
dnom 10
numr 10
sc 10
ss01 4
zero 1
```

`split(".")` is from chapter 9. It cuts `a.sc` into `["a", "sc"]`, and it leaves a name without a dot in one piece, so `len(parts) < 2` means "no suffix here". The second half of that line is for one glyph. `.notdef` splits into `["", "notdef"]`: an empty piece, then the name. Its dot is at the front and belongs to the name, so the function skips it.

`parts[-1]` is the last piece, from chapter 10. A name can carry two suffixes, as `A.ss01.alt` would, and this script files the glyph under the last one.

Notice that `by_suffix` takes a list of names and gives back a dictionary. It doesn't know there's a font, and it will never know there's a window. That's the habit from chapter 123: the part that thinks stays apart from the part that shows.

## Step 2: Empty the box and fill it again

The window will need to do this more than once. Ines adds a glyph, clicks **Look again**, and the groups have to be rebuilt. The plain way to rebuild is `groups = by_suffix(...)`, and inside `build` that won't work. The reason is a rule that chapter 122's third exercise ran into: a function inside a function can change what's in a box it finds outside, but it can't put a new box there.

So the script keeps one dictionary for the whole life of the window and changes what's in it. Two new methods do that:

```python
groups = {"sc": ["a.sc", "b.sc"]}
groups.clear()
print(groups)
groups.update({"ss01": ["a.ss01"], "zero": ["zero.zero"]})
print(groups)
```

```text
{}
{'ss01': ['a.ss01'], 'zero': ['zero.zero']}
```

`clear` takes everything out and leaves the same dictionary, empty. `update` takes another dictionary and copies each of its keys and values in. Together they say: empty the box, then fill it from this. You'll use the same two moves three times today, on the dictionary, on the list of choices and on the list of names, and every time in that order.

## Step 3: A box of choices

A `QComboBox` is the widget that shows one choice and drops open to show the rest when you click it. You fill it from a list of texts with `addItems`, and you ask what it's showing with `currentText`:

```python
choice = gui.QComboBox(panel)
choice.addItems(sorted(groups))
print(read(choice, "currentText"))
```

```text
dnom
```

That fragment belongs inside a `build`, where `panel` exists. `sorted(groups)` gives the dictionary's keys in order, as it has since chapter 43. The box shows the first one until somebody picks another. `read` is the small function from chapter 123, here because I can't tell you from source alone whether `currentText` is a value or a function in FontLab's Qt.

The point of this widget is what it can't do. A field lets Ines type `ss1` or `SS01` or `.ss01`, and then your script has to decide what she meant. A box of choices holds only what the font holds. You've stopped checking the answer and started limiting the question, which is the same thing the number box did for you in chapter 123.

## Step 4: The mistake

Now the function that fills the box, written the way I first wrote it:

```python
def fill_choice():
    font = fl.CurrentFont()
    groups.clear()
    if font is not None:
        groups.update(by_suffix([glyph.name for glyph in font.glyphs]))
    choice.addItems(sorted(groups))
```

It opens well: five suffixes. Click **Look again** and open the box:

```text
dnom
numr
sc
ss01
zero
dnom
numr
sc
ss01
zero
```

Click again and there are fifteen. No error, no message, and each click makes it worse.

`addItems` adds. It does what its name says and has no idea that these are the same five as before. The dictionary got its `clear` and the box didn't. The cure is one line before the filling:

```python
    choice.clear()
    choice.addItems(sorted(groups))
```

Whenever you fill a widget from data, ask what was in it before. If the answer isn't "nothing", empty it first.

## Step 5: The list, and the signal that fills it

The glyph names go in a `QListWidget`, a box of rows with a scroll bar when there are too many to show. It fills one row at a time, and each row is a small object of its own, a `QListWidgetItem`, made from the text:

```python
def fill_list():
    names = groups.get(read(choice, "currentText"), [])
    listing.clear()
    for name in names:
        listing.addItem(gui.QListWidgetItem(name))
    label.setText(f"{len(names)} with this suffix.")
```

Empty, then fill, as before. `groups.get(..., [])` is chapter 22's careful lookup: if the box of choices is empty, its text is `""`, there's no such key, and you get an empty list back with no complaint.

What should call `fill_list`? Not a button. Ines has already said what she wants by picking, and a second click to confirm it would be the window being slow on purpose. The box of choices has a signal for this, `currentIndexChanged`, which fires whenever the choice it shows becomes a different one:

```python
choice.currentIndexChanged.connect(on_pick)
```

It's chapter 122's `connect` with another signal's name in front. And here is something useful: filling the box also changes what it shows, from nothing to its first choice. So the signal fires when `fill_choice` runs, and the list fills itself. One function fills the choices, the choices fill the list, and nothing in the script has to remember to do both.

## The whole script

```python
#FLM: Suffix Picker
# Lists the suffixes in the font's glyph names and shows the glyphs
# that carry the one you pick. Changes nothing.
import fly.ap.core.scripting as scripting
from fly import fl, qt

core, gui = qt.QtCore, qt.QtGui
KEY = "tools.suffixes"


def read(owner, name):
    item = getattr(owner, name)
    return item() if callable(item) else item


def by_suffix(names):
    groups = {}
    for name in names:
        parts = name.split(".")
        if len(parts) < 2 or parts[0] == "":
            continue
        suffix = parts[-1]
        if suffix not in groups:
            groups[suffix] = []
        groups[suffix].append(name)
    return groups


def build(parent):
    panel = gui.QWidget(parent)
    panel.setWindowFlags(core.Qt.Tool)
    panel.setWindowTitle("Suffixes")
    panel.setAttribute(core.Qt.WA_DeleteOnClose)
    groups = {}
    choice = gui.QComboBox(panel)
    listing = gui.QListWidget(panel)
    again = gui.QPushButton("Look again", panel)
    label = gui.QLabel("", panel)

    def safely(work):
        try:
            work()
        except Exception as problem:
            label.setText(f"Didn't work.\n{type(problem).__name__}: {problem}")

    def fill_list():
        names = groups.get(read(choice, "currentText"), [])
        listing.clear()
        for name in names:
            listing.addItem(gui.QListWidgetItem(name))
        label.setText(f"{len(names)} with this suffix.")

    def fill_choice():
        font = fl.CurrentFont()
        groups.clear()
        if font is not None:
            groups.update(by_suffix([glyph.name for glyph in font.glyphs]))
        choice.clear()
        choice.addItems(sorted(groups))
        if not groups:
            label.setText("No font is open, or its names have no suffixes.")

    def on_pick(*args):
        safely(fill_list)

    def on_again(*args):
        safely(fill_choice)

    choice.currentIndexChanged.connect(on_pick)
    again.clicked.connect(on_again)

    top = gui.QHBoxLayout()
    top.addWidget(gui.QLabel("Suffix", panel))
    top.addWidget(choice)
    top.addWidget(again)
    outer = gui.QVBoxLayout(panel)
    outer.addLayout(top)
    outer.addWidget(listing)
    outer.addWidget(label)
    fill_choice()
    return panel


scripting.show_script_dialog(build, KEY)
```

Save it as `suffix_picker.py`.

Three things in `build` are worth a second look. `groups` is made once, empty, near the top, and the functions below it share it. `safely` is chapter 122's `show` with a new job: it runs a function that does the work and writes any error into the label, so both slots are one line each. And `fill_choice()` is called on the last line before `return`, after the signal is connected, so that the first filling sets off the first list.

## Run it

The window opens with **dnom** in the box, ten names in the list from `zero.dnom` to `nine.dnom`, and under it:

```text
10 with this suffix.
```

Pick **sc**. The list changes as soon as you let go: `a.sc` to `h.sc`, then `one.sc` and `zero.sc`, ten again. Pick **ss01** and there are four, the three letters and `ampersand.ss01`. Pick **zero** and there's one, `zero.zero`, the slashed zero that chapter 89 wrote a feature for.

Now close the font, leave the window open, and click **Look again**:

```text
No font is open, or its names have no suffixes.
```

The box and the list are both empty. Open the font, click once more, and they're back.

## Break it on purpose

In `by_suffix`, take out the second half of the test, so the line reads `if len(parts) < 2:`. Run it and open the box. There's a sixth choice, **notdef**, and picking it lists one glyph, `.notdef`. Nothing crashed. The window is now offering a suffix that isn't one, and Ines has no way to know that. Mistakes in the thinking part show up as wrong choices on the screen, which is a good reason to test that part alone, and chapter 139 will. Put the test back.

Then move the line `choice.currentIndexChanged.connect(on_pick)` down, to sit between `fill_choice()` and `return panel`. Run it. The box says **dnom** and the list is empty, with nothing in the label either. The first filling happened before anybody was listening. Pick **sc** and the window wakes up, because now the signal has a function to call. The order of lines in `build` hardly mattered until today. Once a widget's filling sets off a signal, connect first and fill afterward. Move the line back.

## What you learned

A widget that offers choices is filled from data, and the rule for filling is to empty it first, whether it's a dictionary (`clear`, then `update`), a `QComboBox` (`clear`, then `addItems`) or a `QListWidget` (`clear`, then `addItem` for each row). A box of choices can only answer with something that's in the font, so there's nothing to check afterward. Its `currentIndexChanged` signal fires when the choice changes, including when the box is first filled, so one filling can set off the next. The grouping itself lives in a function that knows nothing about windows.

## Try it yourself

1. **Look again** forgets what you'd picked and goes back to the first suffix. In `fill_choice`, read `currentText` into a variable before the `clear`. After `addItems`, if that text is in `groups`, find its place with `sorted(groups).index(text)` and hand the number to `choice.setCurrentIndex`. Pick **sc**, click **Look again**, and check it stays.
2. Put the number of suffixes in the window's title: `Suffixes (5)`. You'll need `panel.setWindowTitle` in `fill_choice`, and an f-string.
3. Copy `by_suffix` and the box of choices into `shift_dialog.py`, next to the names field. When a suffix is picked, write its names into the field, joined by spaces, with `names.setText`. I haven't seen `setText` on a field in FontLab; it's the same call the label has. Now Ines can pick **ss01**, read the four names, take one out by hand, and click **Shift**.

## Next

Mira looks at the script from the door. `build` has four functions inside it, a dictionary they share, and five widgets they all reach for. It works, and nobody could say where the tool keeps its things. "You've been using objects for twenty-four weeks," she says. "Time you made one." Chapter 126 does: a class of your own.
