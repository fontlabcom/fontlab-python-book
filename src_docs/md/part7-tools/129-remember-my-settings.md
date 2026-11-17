---
this_file: src_docs/md/part7-tools/129-remember-my-settings.md
---

# 129. Remember my settings

Monday of week twenty-five, 28 December. The studio is half empty and Ines has the Light to herself. She opens the Shift tool, types 12 into **Left**, types 12 into **Right**, names three glyphs and clicks. She closes it to look at a proof. She opens it again, and both boxes say 0. By eleven she has typed 12 twenty times, and she has typed 21 once and not noticed until the `H` looked wrong.

A window forgets everything when it closes, and so does a script when it ends. Chapter 127 kept a panel alive in a drawer of `sys`, but that drawer empties when FontLab quits. The only thing that outlasts FontLab is a file. Today the Shift tool gets one: a few lines of JSON that it reads when it opens and writes when Ines clicks.

## What you need

`Plum-practice` open with the Light showing, Fly installed, and `shift_tool.py` from chapter 126.

I haven't run this chapter in FontLab 9. The settings functions are plain Python, and I ran them as printed against a folder of my own, with good files and damaged ones. The whole script ran against the stand-in widgets and the stand-in font from chapter 123. The one line I couldn't check is the one that asks FontLab where its data folder is.

## Step 1: Where the file lives

A settings file needs a home that isn't the font's folder (the settings belong to Ines, not to Plum) and isn't the Scripts folder (which chapter 133 will replace wholesale). FontLab keeps a folder of its own for each person who uses it, and Fly knows where it is. In `shift_tool.py`, make sure the top has `import json` and that `ap` is among the names on the `from fly import` line, and then add:

```python
def settings_path():
    return ap.app.paths.userDataFolder / "tool-settings.json"
```

`userDataFolder` is a `Path`, and the `/` joins a file name to it, as it did in chapter 112. On a Mac I'd expect `FontLab/FontLab 9` inside your own `Library/Application Support`, though a FontLab preference can put it elsewhere. Print `ap.app.paths.userDataFolder` once in the Scripting panel, after `from fly import ap`, so that you know where to look.

One file will do for every tool you write. Inside, each tool has its own drawer, under the key it already has:

```text
{
    "tools.shift": {
        "left": 12,
        "right": 12
    }
}
```

That's a dictionary of dictionaries, the shape `family-info.json` had in chapter 99, one level deeper.

## Step 2: Read it, and the mistake

The first version writes itself:

```python
def load_settings(key):
    with open(settings_path(), encoding="utf-8") as f:
        return json.load(f)[key]
```

Call it from the tool and the tool doesn't open at all. The Output panel says:

```text
FileNotFoundError: [Errno 2] No such file or directory: '/Users/ines/Library/Application Support/FontLab/FontLab 9/tool-settings.json'
```

There is no file yet. Nobody has clicked, so nothing has been saved, and a tool that can't open until it has been used can never be used. This is the mistake that every settings reader makes once: it treats the file as something the script owns. The script doesn't own it. The file can be missing, because this is the first run or a new computer. It can be half written, because the laptop lid closed at the wrong moment. A person can have opened it in a text editor and changed 12 to "12". It can be a perfectly good file with no drawer for this tool in it.

So a settings reader has one rule: **the file may suggest, and the script decides.** Whatever happens, the tool opens.

## Step 3: Defaults first

The way to keep that rule is to start from values the script trusts and let the file replace them one at a time. In the tool:

```python
DEFAULTS = {"left": 0, "right": 0}
```

And beside `settings_path`, in the same script:

```python
def read_settings_file():
    try:
        with open(settings_path(), encoding="utf-8") as f:
            stored = json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    if not isinstance(stored, dict):
        return {}
    return stored


def load_settings(key, defaults):
    values = dict(defaults)
    mine = read_settings_file().get(key)
    if not isinstance(mine, dict):
        return values
    for name in defaults:
        if name in mine and type(mine[name]) == type(defaults[name]):
            values[name] = mine[name]
    return values
```

`read_settings_file` has three ways to give up, and each one gives back an empty dictionary: no file, a file that isn't JSON, and a file that is JSON but isn't a dictionary. The two `except` lines are the pair from chapter 99. There, a damaged file stopped the script with a message, because the script was about to write into a font. Here it only costs Ines a 12, so the script shrugs and carries on.

`load_settings` copies the defaults with `dict(defaults)`, which does for a dictionary what `list(caps)` did for a list in chapter 51, so that the tool's own `DEFAULTS` is never touched. Then it walks the names in the defaults, not the names in the file. That direction matters. A name in the file that the tool doesn't know is ignored without any code to ignore it. A name the tool knows and the file lacks keeps its default.

The last test is `type(mine[name]) == type(defaults[name])`. The default for `left` is 0, a whole number, so the stored value has to be a whole number too. Text like `"12"` is refused, and so is 12.5, and so is `true`. The defaults do double duty: they say what the value is when nothing is stored, and what kind of thing it has to be when something is.

## Step 4: Write it

```python
def save_settings(key, values):
    stored = read_settings_file()
    stored[key] = values
    with open(settings_path(), "w", encoding="utf-8") as f:
        json.dump(stored, f, indent=4, ensure_ascii=False)
```

Saving reads the file first. One file serves every tool, so the Shift tool has to put its drawer back among the others, not replace the whole file with its own two numbers. Read everything, change one key, write everything.

Two decisions go into the tool, and neither is about Python. When to save: after a click that worked. A click that raised an error saves nothing. A click the tool turned down with a sentence of its own still saves the boxes. And what to save: the two numbers, and not the tick box. A tool that remembers being armed opens armed. **Only show what would happen** starts ticked every time, whatever happened yesterday. The glyph names aren't saved either. They change with every click, and a field that fills itself with last week's names invites a click on the wrong glyphs.

## The whole script

```python
#FLM: Shift Tool
# Adds to the sidebearings of the glyphs you name, or of the ones
# selected in the Font window, in the master that's showing.
import json

import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.metrics.panel.model as metrics
from fly import ap, fl, qt
from fly.pens import layer_of
from fly.tr.proxy.fl.objects.glyph import pGlyph

core, gui = qt.QtCore, qt.QtGui
KEY = "tools.shift"
LIMIT = 200
SHOWN = 8
DEFAULTS = {"left": 0, "right": 0}


def settings_path():
    return ap.app.paths.userDataFolder / "tool-settings.json"


def read_settings_file():
    try:
        with open(settings_path(), encoding="utf-8") as f:
            stored = json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    if not isinstance(stored, dict):
        return {}
    return stored


def load_settings(key, defaults):
    values = dict(defaults)
    mine = read_settings_file().get(key)
    if not isinstance(mine, dict):
        return values
    for name in defaults:
        if name in mine and type(mine[name]) == type(defaults[name]):
            values[name] = mine[name]
    return values


def save_settings(key, values):
    stored = read_settings_file()
    stored[key] = values
    with open(settings_path(), "w", encoding="utf-8") as f:
        json.dump(stored, f, indent=4, ensure_ascii=False)


def read(owner, name):
    item = getattr(owner, name)
    return item() if callable(item) else item


def plan_rows(font, master, names, left, right):
    rows = []
    for name in names:
        if font[name] is None:
            raise ValueError(f"No glyph called {name}.")
        rich = pGlyph(font, font[name])
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
        saved = load_settings(KEY, DEFAULTS)
        self.left.setValue(saved["left"])
        self.right.setValue(saved["right"])
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
            left = read(self.left, "value")
            right = read(self.right, "value")
            text = shift(read(self.names, "text"), left, right,
                         read(self.rehearse, "checked"))
            save_settings(KEY, {"left": left, "right": right})
            self.runs += 1
            self.label.setText(f"{text}\nRun {self.runs} in this window.")
        except Exception as problem:
            self.label.setText(f"Didn't work.\n{type(problem).__name__}: {problem}")


def build(parent):
    tool = ShiftTool(parent)
    return tool.panel


scripting.show_script_dialog(build, KEY)
```

Save it over `shift_tool.py`. Next to chapter 126's version, four places changed. `import json` is new, and `ap` joins the `from fly import` line. `DEFAULTS` is new, with the four settings functions from steps 1 to 4 under it. `__init__` asks `load_settings` for the saved values and puts them in the two boxes with `setValue`, after `setRange`, so that the box already knows its limits when the number arrives. And `on_go` reads the two numbers into names of their own, because it now needs them twice: once for `shift` and once for `save_settings`, which sits after `shift` and so is skipped when `shift` raises.

## Run it

Open the tool. Both boxes say 0, since there's no file. Type `n o H`, set both boxes to 12 and click **Shift**:

```text
n: 84 499 80 to 96 523 92
o: 50 494 50 to 62 518 62
H: 88 612 84 to 100 636 96
Light: 3 would change.
Run 1 in this window.
```

That was a rehearsal, and it saved all the same: the numbers are what Ines chose, whether or not she has used them yet. Look in the folder from step 1. `tool-settings.json` is there, with the six lines shown above.

Close the tool. Run the script again. Both boxes say 12, the tick box is ticked, the names field is empty. Quit FontLab, start it, open the font, run the script: 12 and 12.

Then try a name that isn't in the font, with 30 in **Left**:

```text
Didn't work.
ValueError: No glyph called zz.
```

Open the tool again and the box says 12. The 30 went nowhere, so it wasn't kept.

## Break it on purpose

The file is yours to damage. Open `tool-settings.json` in a text editor and put quotation marks round the first number and a silly value in the second:

```text
{
    "tools.shift": {
        "left": "12",
        "right": 5000
    }
}
```

Run the script. **Left** says 0: `"12"` is text, the default is a number, and the type test turned it away. **Right** says 200. The number 5000 passed the test, because it is a whole number, and then the spin box cut it down to the top of its own range. The settings code checks the kind of value and the widget checks the size, and between them a wrong file can't put a wrong number in the box.

Now delete the last three lines of the file, so that it stops in the middle, and run the script again. Both boxes say 0. Inside `read_settings_file`, `json.load` raised `JSONDecodeError: Expecting property name enclosed in double quotes`, the second `except` caught it, and the tool opened on its defaults. Click **Shift** once and look at the file: it's whole again, written fresh. Notice what that cost. If other tools had drawers in the damaged file, they're gone, because the save started from an empty dictionary. For a file of spin-box numbers that's a fair price. For anything you'd mind losing, a reader should stop and say so, as chapter 99's did.

## What you learned

A tool remembers across sessions by writing a small JSON file in FontLab's user data folder, one file for all your tools with one dictionary per tool. Reading starts from defaults the script trusts and takes from the file only the names it knows, with values of the right type, so a missing, broken or edited file can never stop the tool opening. Saving reads the whole file, changes one key and writes it all back, and it happens only after a run that worked. What to remember is a design decision: the numbers, yes; the tick box that makes the tool safe, no.

## Try it yourself

1. Add a **Forget** button that saves `DEFAULTS` and sets both boxes back to 0. Which of the functions you already have does all the work?
2. Give the Sidebearings panel from chapter 128 a drawer of its own under its key, `tools.sidebearings`, holding the number of milliseconds between looks. Change it in the file by hand, run the panel, and check with `EVERY` printed that it took. What should the panel do with 0?
3. Change the 12 in the file to `true` and run the tool. The box says 0. Now change the test in `load_settings` to `isinstance(mine[name], type(defaults[name]))` and run it again. What does the box say, and what does that tell you about `True` and whole numbers?

## Next

With the numbers remembered, Ines grows bolder: she empties the names field, selects every glyph in the Font window, and clicks. FontLab stops answering for most of a minute, and she can't tell whether it's working or stuck. Chapter 130 shows her how far along it is, and gives her a way to say stop.
