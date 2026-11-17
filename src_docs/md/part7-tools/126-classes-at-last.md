---
this_file: src_docs/md/part7-tools/126-classes-at-last.md
---

# 126. Classes, at last

Thursday, twenty to twelve. Mira has her coat on. She scrolls through `shift_dialog.py` once more, top to bottom, and stops at the line that calls `arrange` with seven things in the brackets.

"That line is the tool telling you it wants to be one thing," she says. "It has a panel, two number boxes, a field, a tick box, a button and a label, and you're carrying them from function to function in your hands."

Since chapter 6 you've opened drawers in wardrobes other people built: a glyph has a `name`, a layer has shapes, a label has `setText`. Today you build a wardrobe. It's the last large piece of Python in this book.

## What you need

`Plum-practice` open with the Regular showing, Fly installed, `halfmoon.py`, and `shift_dialog.py` from chapter 124. The tool does the same work as before and gains one small thing: it counts its own runs.

I haven't run this chapter in FontLab 9. The small examples in the first three steps are plain Python, and I ran them as printed. The whole script ran against the stand-in widgets and the stand-in font from chapter 123.

## Step 1: A wardrobe with one drawer

Type this into the Scripting panel and run it:

```python
class Counter:
    def __init__(self):
        self.count = 0


first = Counter()
second = Counter()
first.count = 5
print(first.count, second.count)
```

```text
5 0
```

`class Counter:` starts a **class**. A class is the drawing for a wardrobe: it says which drawers every wardrobe of this kind has. It isn't a wardrobe yet. `Counter()`, with brackets, builds one from the drawing, and you can build as many as you like. Each one is called an **object**, and the two here are separate pieces of furniture. Putting 5 in the first one's drawer does nothing to the second.

The function inside is where the drawers are made. Its name is `__init__`, with two underscores on each side, and Python calls it for you each time a wardrobe is built. You never call it yourself. Its one parameter, `self`, is the wardrobe being built. So `self.count = 0` reads: in this new wardrobe, make a drawer labeled `count` and put 0 in it.

That's the same dot you've written since chapter 6. `glyph.name` opens a drawer in a wardrobe FontLab built. `self.count` opens one in a wardrobe you're building.

## Step 2: A wardrobe that does things

A drawer can hold a function. Add one to the class and run it again:

```python
class Counter:
    def __init__(self):
        self.count = 0

    def click(self):
        self.count += 1
        return self.count


first = Counter()
second = Counter()
print(first.click(), first.click(), second.click())
print(first.count, second.count)
```

```text
1 2 1
2 1
```

A function that lives in a class is called a **method**. You've been calling methods for months: `name.split(".")`, `label.setText(...)`, `groups.clear()`. Now you know what they are.

Look at how `click` is written and how it's called. It's written with one parameter, `self`. It's called with nothing in the brackets. The object in front of the dot goes in as `self`. When you write `first.click()`, Python hands `first` to `click`, so inside it `self.count` is the first counter's drawer. With `second.click()` the same lines work on the second counter.

This settles the trouble from chapter 125, and from chapter 122's third exercise if you did it. `count += 1` inside a nested function fails, because it tries to put a new box outside, and the way round is a list of one number. A method doesn't need the trick. `self.count += 1` changes what's in a drawer of an object the method was handed, and that has always been allowed.

## Step 3: The mistake

Write a method the way you'd write any function that takes nothing:

```python
class Counter:
    def __init__(self):
        self.count = 0

    def click():
        self.count += 1
        return self.count


first = Counter()
print(first.click())
```

```text
TypeError: Counter.click() takes 0 positional arguments but 1 was given
```

You gave it nothing, and Python says you gave it one. It's chapter 122's message, with the cause turned round. There the button handed over a value nobody asked for. Here Python does: the object in front of the dot always goes in first, and the method had no parameter to catch it.

Every method starts with `self`. When you see "takes 0 positional arguments but 1 was given" and the function lives in a class, that's the first thing to check. Put `self` back.

## Step 4: The tool as one object

Now the Shift window. Three changes turn chapter 124's script into a class, and none of them changes what the tool does.

Every widget that was a box inside `build` becomes a drawer: `left` becomes `self.left`, `label` becomes `self.label`. They're made in `__init__`, since that's where drawers are made.

`arrange` and `on_go` become methods. `arrange` loses its seven parameters and keeps one, `self`, because everything it needs is in the wardrobe it's handed.

And the button is connected to `self.on_go`. That's a method without its brackets, with its object attached. When the button calls it later, `self` is already filled in, and the button's own `False` lands in `*args` as before.

## The whole script

```python
#FLM: Shift Tool
# Adds to the sidebearings of the glyphs you name, or of the ones
# selected in the Font window, in the master that's showing.
import halfmoon
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.metrics.panel.model as metrics
from fly import fl, qt
from fly.pens import layer_of

core, gui = qt.QtCore, qt.QtGui
KEY = "halfmoon.shift"
LIMIT = 200
SHOWN = 8


def read(owner, name):
    item = getattr(owner, name)
    return item() if callable(item) else item


def plan_rows(font, master, names, left, right):
    rows = []
    for name in names:
        if font[name] is None:
            raise ValueError(f"No glyph called {name}.")
        rich = halfmoon.rich(font, font[name])
        old = (rich.getLSB(master), rich.getAdvance(master), rich.getRSB(master))
        new = (old[0] + left, old[1] + left + right, old[2] + right)
        rows.append((rich, layer_of(rich.fl, master), old, new))
    return rows


def shift(text, left, right, rehearse):
    font = fl.CurrentFont()
    if font is None:
        return "No font is open."
    package = scripting.current_package()
    master = package.master
    names = text.split()
    if not names:
        names = scripting.names_selected_names()
    if not names:
        return "Type some glyph names, or select glyphs in the Font window."
    rows = plan_rows(font, master, names, left, right)
    lines = [f"{rich.name}: {old[0]} {old[1]} {old[2]} to {new[0]} {new[1]} {new[2]}"
             for rich, layer, old, new in rows[:SHOWN]]
    if len(rows) > SHOWN:
        lines += [f"and {len(rows) - SHOWN} more"]
    if rehearse:
        return "\n".join(lines + [f"{master}: {len(rows)} would change."])

    def change():
        for rich, layer, old, new in rows:
            metrics.shift_and_set(layer, left, new[1])

    facts = history.scan_auto_facts(package)
    layers = [layer for rich, layer, old, new in rows]
    owners = [rich.fl for rich, layer, old, new in rows]
    history.commit("Shift sidebearings", layers, owners, change,
                   operation="geometry", facts=facts, allow_bases=True)
    return "\n".join(lines + [f"{master}: {len(rows)} changed."])


class ShiftTool:
    def __init__(self, parent):
        self.panel = gui.QWidget(parent)
        self.panel.setWindowFlags(core.Qt.Tool)
        self.panel.setWindowTitle("Shift")
        self.panel.setAttribute(core.Qt.WA_DeleteOnClose)
        self.label = gui.QLabel("", self.panel)
        self.names = gui.QLineEdit("", self.panel)
        self.left = gui.QSpinBox(self.panel)
        self.left.setRange(-LIMIT, LIMIT)
        self.right = gui.QSpinBox(self.panel)
        self.right.setRange(-LIMIT, LIMIT)
        self.rehearse = gui.QCheckBox("Only show what would happen", self.panel)
        self.rehearse.setChecked(True)
        self.go = gui.QPushButton("Shift", self.panel)
        self.runs = 0
        self.go.clicked.connect(self.on_go)
        self.arrange()

    def arrange(self):
        form = gui.QFormLayout()
        form.addRow("Glyphs", self.names)

        sides = gui.QHBoxLayout()
        sides.addWidget(gui.QLabel("Left", self.panel))
        sides.addWidget(self.left)
        sides.addWidget(gui.QLabel("Right", self.panel))
        sides.addWidget(self.right)

        bottom = gui.QHBoxLayout()
        bottom.addWidget(self.rehearse)
        bottom.addWidget(self.go)

        outer = gui.QVBoxLayout(self.panel)
        outer.addLayout(form)
        outer.addLayout(sides)
        outer.addLayout(bottom)
        outer.addWidget(self.label)

    def on_go(self, *args):
        try:
            text = shift(read(self.names, "text"), read(self.left, "value"),
                         read(self.right, "value"), read(self.rehearse, "checked"))
            self.runs += 1
            self.label.setText(f"{text}\nRun {self.runs} in this window.")
        except Exception as problem:
            self.label.setText(f"Didn't work.\n{type(problem).__name__}: {problem}")


def build(parent):
    tool = ShiftTool(parent)
    return tool.panel


scripting.show_script_dialog(build, KEY)
```

Save it as `shift_tool.py`. `read`, `plan_rows` and `shift` are still plain functions above the class, unchanged since chapter 123. They don't need anything from the window, so they don't belong in it.

Read `__init__` as a list of what the tool owns. Eight drawers: the panel, the answer label, the five widgets Ines works with, and `runs`. Anyone opening this file can now answer "what does this tool keep?" by reading one function.

Some names in the class have no `self.` in front: `form`, `sides`, `bottom`, `outer`, `text`. Those are ordinary boxes that live for the length of one method. The rule for choosing: if another method will need it, or the next click will, it's a drawer. If it's used up before the method ends, it's a box.

`self.runs` is the new thing the class makes cheap. The tool remembers how many times it has run since the window opened. With loose functions you'd have needed chapter 122's list of one number.

`build` has shrunk to two lines. `show_script_dialog` wants a function that takes the parent and returns a widget, so `build` makes the tool and returns its panel. The tool itself isn't the window. It owns the window, in the drawer `panel`.

One thing here I'm inferring. `build` ends, and its box `tool` goes with it. What keeps the tool from being thrown away is the button: it holds `self.on_go`, and that method holds its object. That's how Python works, and it held in my stand-in. Whether FontLab's Qt holds the method as firmly, I haven't seen. If your button goes dead a moment after the window opens, this is why, and chapter 127 keeps tools in a way that doesn't depend on it.

## Run it

Type `n o H`, set both numbers to 10, leave the tick in, and click **Shift**:

```text
n: 70 523 66 to 80 543 76
o: 38 520 38 to 48 540 48
H: 76 672 70 to 86 692 80
Regular: 3 would change.
Run 1 in this window.
```

Click again and the last line says `Run 2 in this window.` Type `n zz` and click:

```text
Didn't work.
ValueError: No glyph called zz.
```

The failed click isn't counted, since `self.runs += 1` comes after the line that failed. Run the script again from the Scripting panel and the count starts at 1: a new window is a new object with a new `runs` drawer.

Mira reads the label over Ines's shoulder, says "good", and goes for her train.

## Break it on purpose

In `__init__`, take `self.` off the front of one line, so it reads `label = gui.QLabel("", self.panel)`. Run it:

```text
AttributeError: 'ShiftTool' object has no attribute 'label'. Did you mean: 'panel'?
```

No window opens. `label` without `self.` is a box in `__init__`, gone when `__init__` ends, and `arrange` went looking for a drawer that was never made. This is the commonest slip in a class, and the message names it plainly: this object has no such drawer. The suggestion at the end is Python guessing, and it's a wrong guess here. Put `self.` back.

Then change the connection to `self.go.clicked.connect(on_go)`:

```text
NameError: name 'on_go' is not defined
```

Inside a class there's no loose function called `on_go`. There's a drawer of that name in each tool, and you reach a drawer through its wardrobe: `self.on_go`. Change it back.

## What you learned

A class is the drawing for a kind of object, and calling it builds one, with `__init__` run on the new object to make its drawers. A method is a function in a class; it's written with `self` first and called without it, because the object in front of the dot goes in as `self`. What a tool must keep between clicks goes in `self.` drawers, and what one method uses up stays in plain boxes. A window written as a class has one place that lists everything it owns, and its methods reach those things without being handed them.

## Try it yourself

1. Add a method `reset(self)` that sets both number boxes to 0 with `setValue(0)` and empties the label, and a **Reset** button connected to it. Remember `*args`.
2. Add a drawer `self.last = ""` and store the names field's text in it after each run that works. When a run fails, show `Last good run: n o H` under the error.
3. Turn chapter 125's `suffix_picker.py` into a class `SuffixPicker`. The dictionary `groups` becomes `self.groups`. Then look at `fill_choice`: now that it's a method, could it say `self.groups = by_suffix(...)` and do without `clear` and `update`? Try it, and say in one sentence why it works here and didn't in chapter 125.

## Next

Ines is on her own now. The first thing she does is drag the Shift window out of the way of the glyph she's looking at, and the second is lose it behind another window. Chapter 127 gives a tool a place in FontLab's own frame: a panel that docks at the side and stays.
