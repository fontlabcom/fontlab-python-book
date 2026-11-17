---
this_file: src_docs/md/part7-tools/127-a-panel-that-stays.md
---

# 127. A panel that stays open

Thursday afternoon. Mira is on a train and Ines is alone with the Light. She has the Shift window from chapter 126, and she has lost it twice: once behind the Glyph window, once behind FontLab itself. What she wants today is smaller than Shift and more constant. She wants to see a glyph's sidebearings while she looks at the glyph, without asking.

A thing you look at all day shouldn't float about. FontLab's own panels sit at the edge of its frame, and a script can ask for a place there. Getting the place takes one line. Keeping it is the lesson of this chapter: a script ends a moment after it starts, and anything the script made has to be held by something that lasts longer.

## What you need

`Plum-practice` open with the Light showing, a Glyph window on `n`, Fly installed, and `halfmoon.py`, which gets one small addition in step 4. The panel reads and changes nothing.

I haven't run this chapter in FontLab 9. I ran the script against stand-in widgets and a stand-in panel maker that keeps a list of what was opened and closed. No script I could read calls Fly's panel maker the way this chapter does, so treat every sentence about what the panel looks like as a claim to check.

## Step 1: Three kinds of window

You've met two kinds already. Chapter 39's message box is the first kind: while it's up, nothing else in FontLab answers. You can't click a glyph, you can't open a menu, and the script itself waits on the line that showed the box. That kind is called *modal*. It's right for a question that must be answered before anything else happens.

The windows since chapter 121 are the second kind. They open, the script ends, and FontLab goes on working around them. That's why Ines could lose one.

The third kind is a *panel*: not a window of its own but a strip of FontLab's frame, with a title bar you can drag to another edge. It behaves like the second kind, in that nothing waits for it, and it has an address.

## Step 2: Ask Fly for a panel

Fly has a maker for panels. Put this in a new script:

```python
from fly import ap, qt

gui = qt.QtGui


def build(content):
    layout = gui.QVBoxLayout(content)
    layout.addWidget(gui.QLabel("n in Light", content))


ap.FontLab().create_panel("Sidebearings", build, area="right")
```

Two things differ from `show_script_dialog`. There, your `build` made the panel and handed it back. Here, Fly has already made an empty widget inside the new strip, and `build` receives it as `content` and fills it. Nothing is returned from `build`.

And look at `area="right"`. Since chapter 121 the rule has been: no named arguments. That rule is about Qt's calls, the ones on `gui` and `core` objects. `create_panel` is a Python function that Fly's authors wrote, and it insists on the name: the four areas are `"left"`, `"right"`, `"top"` and `"bottom"`.

Run it. A strip titled Sidebearings should appear at the right edge with the one line in it. Fly's source says that when FontLab keeps its main frame hidden, the panel floats as a small window that stays on top instead. I can't tell you which of the two you'll see.

## Step 3: Run it again

Run the script a second time. In my stand-in, the list of open panels now reads:

```text
panel 1 "Sidebearings" docked right
panel 2 "Sidebearings" docked right
```

Two panels, and a third if you run it again. `show_script_dialog` never did this, because it kept every window under its key and closed the old one before opening the new. `create_panel` doesn't swap an old panel for a new one. It hands back an object that owns the panel, and the script above dropped that object on the floor: no name was given to it, the script ended, and now your scripts have no way left to ask the first panel to close. You close it by hand, with the cross in its title bar.

So give it a name:

```python
owner = ap.FontLab().create_panel("Sidebearings", build, area="right")
```

That's better for as long as the script runs, which is no time at all. Every run of a script starts with empty boxes. `owner` from the first run is gone before the second run starts, so the second run can't close what the first one opened.

!!! note "Who is holding it?"
    Every object in Python lasts while something refers to it: a name, a list it sits in, another object's drawer. When the last reference goes, the object goes. A script's names all go when the script ends. That's the whole of the problem.

## Step 4: A place that outlasts the script

You already own something that lasts longer than a script: `halfmoon.py`. Chapter 33 showed that Python loads a module once and then hands every later `import halfmoon` the same loaded module, which is why you needed `importlib.reload` after editing it. A dictionary inside that module lives until FontLab quits.

Add these lines to `halfmoon.py`, after the functions that are there:

```python
KEPT = {}


def keep(key, things):
    if key in KEPT:
        KEPT[key][0].close()
    KEPT[key] = things
```

`KEPT` is the shelf. `keep` takes a key and a list of things to hold. If the shelf has that key already, the first thing in the old list is asked to close, and then the new list takes the place. The object `create_panel` hands back has a `close` method, so it goes first in the list.

Run `importlib.reload(halfmoon)` once in the Scripting panel, as in chapter 33, so that FontLab sees the new lines. Then the end of the script becomes:

```python
owner = ap.FontLab().create_panel("Sidebearings", build, area="right")
halfmoon.keep("halfmoon.sidebearings", [owner])
```

Run it twice, and the stand-in's list reads:

```text
panel 1 "Sidebearings" docked right
panel 2 "Sidebearings" docked right
panel 1 closed
```

One panel is open, and it's the new one.

## Step 5: The panel as a class

The panel needs a label, a button and two methods, which is a small wardrobe of the kind chapter 126 built. There's one new wrinkle. `create_panel` calls `build`, and `build` returns nothing, so how does the object made inside `build` get out to be kept? The same way exercise 3 of chapter 122 counted clicks from inside an inner function: a list that the outer function owns.

```python
def main():
    made = []

    def build(content):
        made.append(SidebearingPanel(content))

    owner = ap.FontLab().create_panel(TITLE, build, area="right")
    halfmoon.keep(KEY, [owner, made[0]])
```

`build` drops the new `SidebearingPanel` into `made`. After `create_panel` comes back, `made[0]` is that object, and it goes on the shelf beside the owner. Chapter 126 guessed that a tool survives because its button holds one of its methods. Now it doesn't matter whether the guess is right: the shelf holds the tool by name.

## The whole script

```python
#FLM: Sidebearing Panel
# A panel at the side of FontLab that shows the sidebearings of the
# current glyph in the master that's showing. Changes nothing.
import halfmoon
import fly.ap.core.scripting as scripting
from fly import ap, fl, qt

gui = qt.QtGui
KEY = "halfmoon.sidebearings"
TITLE = "Sidebearings"


def glyph_text():
    font = fl.CurrentFont()
    glyph = fl.CurrentGlyph()
    if font is None or glyph is None:
        return "No glyph is showing."
    master = scripting.current_package().master
    rich = halfmoon.rich(font, glyph)
    lines = [
        f"{rich.name} in {master}",
        f"Left {rich.getLSB(master)}",
        f"Width {rich.getAdvance(master)}",
        f"Right {rich.getRSB(master)}",
    ]
    return "\n".join(lines)


class SidebearingPanel:
    def __init__(self, content):
        self.label = gui.QLabel("", content)
        self.again = gui.QPushButton("Look again", content)
        self.again.clicked.connect(self.on_again)
        layout = gui.QVBoxLayout(content)
        layout.addWidget(self.label)
        layout.addWidget(self.again)
        self.refresh()

    def refresh(self):
        try:
            self.label.setText(glyph_text())
        except Exception as problem:
            self.label.setText(f"Didn't work.\n{type(problem).__name__}: {problem}")

    def on_again(self, *args):
        self.refresh()


def main():
    made = []

    def build(content):
        made.append(SidebearingPanel(content))

    owner = ap.FontLab().create_panel(TITLE, build, area="right")
    halfmoon.keep(KEY, [owner, made[0]])


main()
```

Save it as `sidebearing_panel.py`.

`glyph_text` is plain work with no window in it. It asks FontLab for the current font and the current glyph, wraps the glyph in `halfmoon.rich` as chapter 33 did, and reads the three numbers in the master that's showing. The class is two drawers and two methods. `refresh` fills the label and catches whatever goes wrong, as every slot since chapter 122 has. `on_again` is the slot, and all it does is call `refresh`; the split lets `__init__` fill the label once without pretending to be a click.

## Run it

With `n` in the Glyph window and the Light showing, the panel reads:

```text
n in Light
Left 84
Width 499
Right 80
```

Go to `o` in the Glyph window. The panel still says `n`. Click **Look again**:

```text
o in Light
Left 50
Width 494
Right 50
```

Close every Glyph window, click a blank part of the Font window so that no glyph is current, and click **Look again** once more:

```text
No glyph is showing.
```

I've used the Light because the Shift tool has been at work on the Regular since chapter 123, and your Regular's numbers depend on which of those clicks you undid.

Now drag the panel by its title bar to the left edge, or pull it loose so that it floats. FontLab does that part; your script has no say in it and needs none.

## Break it on purpose

Change `area="right"` to `area="middle"` and run:

```text
ValueError: Dock area must be left, right, top or bottom
```

That sentence is Fly's own, and it's a model of an error message: it says what was wrong and lists what would be right. No panel was made, so nothing needs closing. Put `"right"` back.

Next, take the name off: `create_panel(TITLE, build, "right")`.

```text
TypeError: FontLab.create_panel() takes from 2 to 3 positional arguments but 4 were given
```

The count includes `self`, as it did in chapter 126: `self`, the title and `build` make three, and your `"right"` was a fourth with nowhere to go. A function can demand that an argument be named, and this one does. Put `area=` back.

Last, in the Scripting panel, run `importlib.reload(halfmoon)` while the panel is open, and then run the script again. Two panels. The reload ran `KEPT = {}` again, which made a new, empty shelf, and the panel that the old shelf held is on nobody's list. Close it by hand. A shelf in a module is only as lasting as the module.

## What you learned

A modal window makes everything wait, a modeless one doesn't, and a panel is a modeless one with a place in FontLab's frame. An object lasts only while something refers to it, and a script's own names stop referring the moment the script ends. A dictionary in a module you import outlasts every script, so it can hold a panel's owner and close the old panel when a new one is asked for. A Python function can require an argument by name, which is a different matter from Qt's calls refusing names.

## Try it yourself

1. Open the panel at the bottom. One line changes. Then decide which edge suits a panel of four short lines, and say why.
2. Add a fifth line that says how far apart the two sides are: `Sides differ by 4` for the Light's `n`. Use `abs`, from chapter 36. A glyph with even sides should say `Sides match`.
3. `keep` asks the old owner to close and trusts that it can. Print what `close()` gives back, run the script twice, and then close the panel by hand and run it once more. Write down the three answers. I expect `True` each time, and I haven't seen it.

## Next

The panel is in its place and Ines has stopped losing it. What she's lost instead is patience with the button: every time she moves to another glyph, the panel shows the one before until she clicks **Look again**. Chapter 128 takes the button away. The panel will look for itself, five times a second, and change its text only when there's something new to say.
