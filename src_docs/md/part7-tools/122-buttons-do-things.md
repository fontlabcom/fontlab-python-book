---
this_file: src_docs/md/part7-tools/122-buttons-do-things.md
---

# 122. Buttons do things

Wednesday of week twenty-four. Ines opens the window from chapter 121, opens another font, and clicks **Look again**. The window still says GG Plum. She clicks harder.

"It's broken."

"It isn't connected to anything," Mira says. "It's a picture of a button."

A button is a widget that knows it was clicked. What it doesn't know is what you want done about it. This chapter tells it, and adds a second button that runs a small report: which glyphs have no character.

## What you need

`Plum-practice` open, Fly installed, and `hello_window.py` from chapter 121 to copy from. Nothing in the font changes.

I haven't run this chapter in FontLab 9. I ran the script in plain Python with stand-in widgets, where a stand-in button can be "clicked" from code and hands its function one value, as FontLab's buttons are documented to do. The label texts below are what the script wrote into the stand-in label, for a font with the glyphs yours should have after Part 5.

## Step 1: A function without its brackets

Type this and run it:

```python
def greeting():
    return "Hello, Ines."

print(greeting())
print(greeting)
```

```text
Hello, Ines.
<function greeting at 0x1298f4c20>
```

The digits at the end will differ on your machine. The first `print` has brackets after the name, so Python calls the function and prints what comes back. The second has none, so Python doesn't call anything. It prints the function itself, the way it would print a list or a number.

A function is a value. You can put it in a box, put it in a list, or hand it to another function. You've done all three without my making a fuss. Chapter 39 handed `run_file_dialog` a function it should call later. Chapter 119 put `ship_check.main` in a list, without brackets, so that the build could call it when its turn came. Chapter 121 handed `build` to `show_script_dialog`.

The pattern is the same every time: here is a function, call it when you're ready. A button needs that from you.

## Step 2: Connect

A button has a drawer called `clicked`. It isn't a number or a text. It's a **signal**: a thing that happens, with a list of functions to call when it does. The list starts empty, which is why Ines's button did nothing. You add to it with `connect`:

```python
def on_again():
    label.setText(font_text())

again.clicked.connect(on_again)
```

These lines go inside `build`, after the label and the button are made. `setText` replaces what a label shows. `on_again` has no brackets in the last line, for the reason in Step 1: you aren't calling it now, you're handing it over. A function connected to a signal is called a **slot**.

Nothing in your script calls `on_again`. FontLab's event loop does, each time the button is clicked, long after your script has ended. That is the bargain from chapter 121: your lines run again only when somebody does something to a widget of yours.

`on_again` uses `label`, and nobody hands it one. It's written inside `build`, so it can see `build`'s boxes, as `change` could see `set_width`'s in chapter 49. That is also why `label` and `again` now have names of their own. In chapter 121 you made the widgets and added them to the layout in one line each, because nothing needed to find them later.

## Step 3: The mistake

Run the script with those lines in, and click **Look again**. In my stand-in run the label didn't change, and this came out instead:

```text
TypeError: build.<locals>.on_again() takes 0 positional arguments but 1 was given
```

I can't tell you where FontLab shows that message, or whether it shows it at all. Look in the Output panel.

Somebody gave `on_again` a value it didn't ask for. It was the button. A signal can carry facts about what happened, and `clicked` carries one: whether the button is now checked, for the kind of button that stays pressed in. Yours isn't that kind, so the fact is always `False`, and it's handed over anyway.

You could write `def on_again(checked):` and ignore `checked`. But other signals carry two facts, or none, and the book's rule for slots is simpler than learning each one:

```python
def on_again(*args):
    label.setText(font_text())
```

The star is new. A parameter with a star in front takes however many values arrive, none or one or five, and collects them in a tuple. The name `args` is a habit, not a keyword. This slot never looks inside it. Write every slot with `*args` and this mistake can't happen to you again.

## Step 4: A slot must not fall over

Chapter 100 wrapped each check in `try`, so that one broken check couldn't stop the others. A slot needs the same care for a different reason. When a script fails, you're sitting in front of the Scripting panel and the traceback is under your nose. When a slot fails, the person in front of the window is Ines, the panel may be closed, and from where she sits a button has stopped working.

So the slot catches whatever goes wrong and says so in the window:

```python
def show(make_text):
    try:
        label.setText(make_text())
    except Exception as problem:
        label.setText(f"Didn't work.\n{type(problem).__name__}: {problem}")
```

`show` takes a function, calls it, and puts the answer in the label. If the function fails, the label gets the name of the error and its message, the two pieces chapter 119 wrote into the build log. Both buttons use `show`, each handing it a different function. That is Step 1 again: `show(font_text)`, without brackets.

## The whole script

Save it as `button_report.py` in your Scripts folder.

```python
#FLM: Button Report
# A small window with two buttons. One reads the font again,
# the other counts the glyphs that have no character.
import fly.ap.core.scripting as scripting
from fly import fl, qt

core, gui = qt.QtCore, qt.QtGui
KEY = "halfmoon.report"
SHOWN = 8


def font_text():
    font = fl.CurrentFont()
    if font is None:
        return "No font is open."
    package = scripting.current_package()
    info = package.info
    version = f"{info.versionMajor}.{info.versionMinor:03d}"
    lines = [
        info.familyName,
        f"Version {version}",
        f"{len(font.glyphs)} glyphs, {len(package.masters)} masters",
    ]
    return "\n".join(lines)


def bare_text():
    font = fl.CurrentFont()
    if font is None:
        return "No font is open."
    names = [glyph.name for glyph in font.glyphs if glyph.unicode is None]
    lines = [f"{len(names)} glyphs have no character."]
    lines += names[:SHOWN]
    if len(names) > SHOWN:
        lines += [f"and {len(names) - SHOWN} more"]
    return "\n".join(lines)


def build(parent):
    panel = gui.QWidget(parent)
    panel.setWindowFlags(core.Qt.Tool)
    panel.setWindowTitle("Halfmoon")
    panel.setAttribute(core.Qt.WA_DeleteOnClose)
    label = gui.QLabel(font_text(), panel)
    again = gui.QPushButton("Look again", panel)
    bare = gui.QPushButton("No character", panel)

    def show(make_text):
        try:
            label.setText(make_text())
        except Exception as problem:
            label.setText(f"Didn't work.\n{type(problem).__name__}: {problem}")

    def on_again(*args):
        show(font_text)

    def on_bare(*args):
        show(bare_text)

    again.clicked.connect(on_again)
    bare.clicked.connect(on_bare)
    layout = gui.QVBoxLayout(panel)
    layout.addWidget(label)
    layout.addWidget(again)
    layout.addWidget(bare)
    return panel


scripting.show_script_dialog(build, KEY)
```

`bare_text` is new, and there's nothing new in it. `glyph.unicode is None` is chapter 115's test for a glyph without a character. `SHOWN` caps the list, because a label that tries to show thirty-nine names is taller than Ines's screen. `lines += names[:SHOWN]` adds the first eight, with the slice from chapter 10.

The two slots are two lines each, and they look as if they could be one function. They can't yet. Each must remember which text to make, and a slot is called with a `False` and nothing else. Chapter 126 gives you a tidier place to keep such things.

The key is a new one, `"halfmoon.report"`. With chapter 121's key, running this script would close that chapter's window. With its own key, the two can be open side by side.

## Run it

The window opens with the three lines you know. Click **No character**:

```text
39 glyphs have no character.
.notdef
a.sc
b.sc
c.sc
d.sc
e.sc
f.sc
g.sc
and 31 more
```

Now do what Ines did. Open another font and click **Look again**. For the second font, my stand-in played one of Oskar's:

```text
Oskar Grotesk
Version 2.010
412 glyphs, 2 masters
```

Click **No character** again and the report is about that font:

```text
3 glyphs have no character.
.notdef
f_i
f_l
```

Each click asks `fl.CurrentFont()` afresh. The window holds no font. It holds a label and two functions that go and look. Between the clicks it shows whatever the last click wrote, which is why, for a moment after you switched fonts, the label was about the wrong one. Chapter 128 deals with that.

Close every font and click **Look again**. The label says `No font is open.`, because `font_text` checks before it reads, and the window stays up.

## Break it on purpose

Put brackets where they don't belong:

```python
again.clicked.connect(on_again())
```

Run the script. Now Python calls `on_again` on the spot, while the window is being built, and hands `connect` what came back, which is `None`. In my stand-in the window opened, and **Look again** was a picture of a button again. FontLab may refuse a `None` with an error instead; I haven't seen which. Either way the brackets turned "call this later" into "call this now". Take them out.

Then break the report. In `bare_text`, change `glyph.unicode` to `glyph.unicod`, run, and click **No character**:

```text
Didn't work.
AttributeError: 'flGlyph' object has no attribute 'unicod'
```

The window is still there and **Look again** still works. The spelling of the object's type is my guess at what FontLab will print; the rest is from the run. Without the `try` in `show`, Ines would have seen nothing happen. Put the letter back.

## What you learned

A function's name without brackets is the function itself, a value you can hand to something that will call it later. A button's `clicked` is a signal, and `connect` adds a function to the list it calls on each click. A slot is written with `*args`, which accepts whatever the signal hands over. A slot catches its own errors and reports them in the window, because the person who clicked can't see a traceback.

## Try it yourself

1. Add a third button, **Suffixes**, that shows how many glyphs have a dot in their name, and the first eight of them. Write `suffix_text`, write `on_suffix`, connect it, add the button to the layout.
2. Inside `on_again`, add `print(args)` as the first line. Click the button and read the Output panel. You should see a tuple with one `False` in it.
3. Make **No character** count its own clicks. Put `count = [0]` in `build`, and in `on_bare` add one to `count[0]` and print it. Then try it with `count = 0` and `count += 1`, and read the error. A function inside a function can read the outer boxes, and it can change what is in a list it finds there, but it can't put a new value in the box itself.

## Next

Ines can click. She still can't say how much. Chapter 123 puts a field for a number in the window, reads it when a button is clicked, and deals with what happens when the field holds something that isn't a number.
