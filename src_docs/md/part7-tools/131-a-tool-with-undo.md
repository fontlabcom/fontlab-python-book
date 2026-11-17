---
this_file: src_docs/md/part7-tools/131-a-tool-with-undo.md
---

# 131. A tool people can trust

Tuesday, 29 December. Ines took yesterday's three clicks back with three trips to **Edit > Undo**, which worked, and then she wrote Mira an email with three numbered complaints.

One: the window stays armed after a real change, so a second click does the change again. Two: she typed `n ncaron`, the label said `Didn't work.` and something about an auto layer, and she could not tell whether her `n` had moved. Three: she typed two names wrong, and the tool told her about the first one only.

Mira answered from her mother's kitchen in four words: "She's right. Fix it." Today's script is the Shift tool from chapter 129, hardened. Every change it makes is still one step in **Edit > Undo**. What's new is everything around that step: what the tool checks before it, what it says, and the state it leaves the window in.

## What you need

`Plum-practice` open with the Font window in front, Fly installed, `halfmoon.py` with chapter 129's settings functions, and `shift_tool.py` from chapter 129.

I haven't run this chapter in FontLab 9. The whole script ran against the stand-in widgets and the stand-in font from chapter 123, with a stand-in for Fly's commit that can be told to refuse or to fail half-way. The refusal texts are copied from Fly's source; the text of a write that failed half-way is built the way Fly's source builds it, around an error I made up.

## Step 1: Ask the cheap questions first

Read chapter 129's `shift` from the top and count how much work it does before it finds out that there's nothing to do. It measures every glyph and builds every line, and only then does the commit discover a problem. A careful tool turns that round. It asks the questions that cost nothing, in order, and leaves at the first bad answer:

```python
def shift(text, left, right, rehearse):
    font = fl.CurrentFont()
    if font is None:
        return "Open a font first.", False
    if left == 0 and right == 0:
        return "Left and Right are both 0, so there's nothing to do.", False
```

Two things changed here. The first message used to be `No font is open.` That states a fact and leaves the person to work out the remedy. `Open a font first.` is the remedy. When you write a message, write the next thing the person should do.

The second change is the comma. `shift` now gives back two values: the text for the label, and `True` or `False` for "did the font change?" A `return` with a comma gives back a tuple, as functions have done since chapter 42, and the caller takes it apart in one line: `text, changed = shift(...)`. The window needs that second value in step 4.

Complaint three is the next question. Chapter 123's `plan_rows` raised an error at the first name it couldn't find. Collect them all instead:

```python
font_names = ["n", "o", "H"]
names = ["n", "zz", "o", "qq"]
missing = [name for name in names if name not in font_names]
print(f"Not in this font: {' '.join(missing)}.")
```

```text
Not in this font: zz qq.
```

In the script the test is `font[name] is None`, as it has been since chapter 51. One sentence, every bad name, and Ines fixes both in one go.

## Step 2: Ask Fly what it would refuse

Complaint two. `ncaron` was built in chapter 56 from `n` and `caron`, and its layers are auto layers: FontLab rebuilds them from the parts. Fly refuses to commit an edit to one, because touching it would make FontLab rebuild every auto layer in the font. The refusal is correct. What's wrong is finding out about it from an error, after the click.

Fly will tell you in advance. The facts you've been passing to `history.commit` since chapter 55 can be asked directly:

```python
facts = history.scan_auto_facts(package)
refused = history.refusals(facts, names, "geometry", allow_bases=True)
print(refused)
```

```text
{'ncaron': 'has auto layers'}
```

`refusals` takes the facts, the names, the kind of edit and the same `allow_bases` you'd give the commit, and returns a dictionary: each name Fly would refuse, with the reason. An empty dictionary means every name is welcome.

Now the tool has a choice, and it's a design choice more than a Python one. It could refuse the whole click. Or it could leave `ncaron` alone, change the rest, and say so. For sidebearings the second is right: when `n` gets wider, `ncaron` follows by itself, which is the point of an auto layer. So the script plans rows only for the names that aren't in `refused`, and adds a line for each one that is:

```python
lines += [f"Left alone: {name} ({refused[name]})" for name in refused]
```

Looping over a dictionary gives its keys, as in chapter 22.

One more question belongs here, because it needs the plan. A big negative number can ask for a glyph narrower than nothing. Any row whose new width is under zero stops the click, with the names.

## Step 3: Two kinds of going wrong

Here's the slot every tool has had since chapter 122, and it's today's mistake:

```python
def on_go(self, *args):
    try:
        self.label.setText(self.work())
    except Exception as problem:
        self.label.setText(f"Didn't work.\n{type(problem).__name__}: {problem}")
```

It catches everything, which was the right first lesson. But `Didn't work.` covers two very different days. On one, Fly looked at the request, refused it, and the font is untouched. On the other, the change began and something broke in the middle. Ines's question, "did my `n` move?", has a different answer on each, and one message for both answers neither.

Fly keeps them apart for you. When it refuses before writing, it raises a `ValueError`. When a write has started and can't be finished or checked, it raises a `RuntimeError`, and its message says that changes may remain. Chapter 99 used two `except` lines under one `try`. Do that here. These are the last five lines of `on_go`, under its `try`:

```text
except ValueError as problem:
    self.label.setText(f"{problem}\n{UNTOUCHED}")
except Exception as problem:
    self.label.setText(f"Stopped part-way: {problem}")
```

`UNTOUCHED` is the sentence `Nothing was changed.`, kept in one constant so that the tool always says it the same way. Python tries the `except` lines from the top and takes the first that fits. A `ValueError` fits the first. Anything else falls to the second, which admits what it doesn't know. It doesn't need to say what to do about it, because Fly's error for a write that stopped half-way ends with that advice.

The type name is gone from both messages. `ValueError:` helped you while you were writing the tool. It tells Ines nothing.

## Step 4: Leave the window safe

Complaint one, and the reason for the second value. After a real change, the slot ticks **Only show what would happen** again:

```python
            if changed:
                halfmoon.save_settings(KEY, {"left": left, "right": right})
                self.runs += 1
                self.rehearse.setChecked(True)
                text += f"\nChange {self.runs} from this window. Edit > Undo takes it back."
```

The next click, meant or not, is a rehearsal. To change the font a second time, Ines has to untick the box a second time, and that small chore is the whole safety. You might think of greying the button out while the tool works. It wouldn't help: as chapter 130 showed, clicks made while a slot runs wait in the queue, and they arrive after the slot has finished and the button is live again. What protects the font is the state the slot leaves behind.

The settings are now saved only after a real change, and the run counter counts only real changes, so the label can call it by its right name.

## The whole script

```python
#FLM: Shift Tool
# Adds to the sidebearings of the glyphs you name, or of the ones
# selected in the Font window, in the master that's showing.
# One click is one Undo step, and the tick box comes back after it.
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
DEFAULTS = {"left": 0, "right": 0}
UNTOUCHED = "Nothing was changed."


def read(owner, name):
    item = getattr(owner, name)
    return item() if callable(item) else item


def unique(names):
    found = []
    for name in names:
        if name not in found:
            found.append(name)
    return found


def plan_rows(font, master, names, left, right):
    rows = []
    for name in names:
        rich = halfmoon.rich(font, font[name])
        old = (rich.getLSB(master), rich.getAdvance(master), rich.getRSB(master))
        new = (old[0] + left, old[1] + left + right, old[2] + right)
        rows.append((rich, layer_of(rich.fl, master), old, new))
    return rows


def shift(text, left, right, rehearse):
    font = fl.CurrentFont()
    if font is None:
        return "Open a font first.", False
    if left == 0 and right == 0:
        return "Left and Right are both 0, so there's nothing to do.", False
    names = unique(text.split())
    if not names:
        names = scripting.names_selected_names()
    if not names:
        return "Type some glyph names, or select glyphs in the Font window.", False
    missing = [name for name in names if font[name] is None]
    if missing:
        return f"Not in this font: {' '.join(missing)}.\nCheck the spelling. {UNTOUCHED}", False

    package = scripting.current_package()
    master = package.master
    facts = history.scan_auto_facts(package)
    refused = history.refusals(facts, names, "geometry", allow_bases=True)
    rows = plan_rows(font, master, [name for name in names if name not in refused],
                     left, right)
    thin = [rich.name for rich, layer, old, new in rows if new[1] < 0]
    if thin:
        return f"Too far: {' '.join(thin)} would be narrower than nothing.\n{UNTOUCHED}", False

    lines = [f"{rich.name}: {old[0]} {old[1]} {old[2]} to {new[0]} {new[1]} {new[2]}"
             for rich, layer, old, new in rows[:SHOWN]]
    if len(rows) > SHOWN:
        lines += [f"and {len(rows) - SHOWN} more"]
    lines += [f"Left alone: {name} ({refused[name]})" for name in refused]
    if not rows:
        return "\n".join(lines + [UNTOUCHED]), False
    if rehearse:
        return "\n".join(lines + [f"{master}: {len(rows)} would change."]), False

    def change():
        for rich, layer, old, new in rows:
            metrics.shift_and_set(layer, left, new[1])

    layers = [layer for rich, layer, old, new in rows]
    owners = [rich.fl for rich, layer, old, new in rows]
    history.commit("Shift sidebearings", layers, owners, change,
                   operation="geometry", facts=facts, allow_bases=True)
    return "\n".join(lines + [f"{master}: {len(rows)} changed."]), True


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
        saved = halfmoon.load_settings(KEY, DEFAULTS)
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
            text, changed = shift(read(self.names, "text"), left, right,
                                  read(self.rehearse, "checked"))
            if changed:
                halfmoon.save_settings(KEY, {"left": left, "right": right})
                self.runs += 1
                self.rehearse.setChecked(True)
                text += f"\nChange {self.runs} from this window. Edit > Undo takes it back."
            self.label.setText(text)
        except ValueError as problem:
            self.label.setText(f"{problem}\n{UNTOUCHED}")
        except Exception as problem:
            self.label.setText(f"Stopped part-way: {problem}")


def build(parent):
    tool = ShiftTool(parent)
    return tool.panel


scripting.show_script_dialog(build, KEY)
```

Save it over `shift_tool.py`. `unique` drops a name given twice and keeps the order, which was exercise 3 in chapter 123. `plan_rows` lost its `raise`, because `shift` has already checked every name before calling it. Every early `return` carries `False`. Only the last line, after the commit, carries `True`.

## Run it

Type `n ncaron n`, set both boxes to 10, and click **Shift** with the box ticked:

```text
n: 70 523 66 to 80 543 76
Left alone: ncaron (has auto layers)
Regular: 1 would change.
```

One `n`, though you typed two. Untick the box and click:

```text
n: 70 523 66 to 80 543 76
Left alone: ncaron (has auto layers)
Regular: 1 changed.
Change 1 from this window. Edit > Undo takes it back.
```

The box is ticked again. Click once more without touching it, and the label ends `Regular: 1 would change.` with the numbers starting from 80. Nothing moved. Choose **Edit > Undo** once and the `n` is at 70, 523, 66.

Now the three kinds of "no". Type `n zz qq`:

```text
Not in this font: zz qq.
Check the spelling. Nothing was changed.
```

Type `hyphen`, set both boxes to −200:

```text
Too far: hyphen would be narrower than nothing.
Nothing was changed.
```

Set both boxes to 0 and the tool says there's nothing to do. Each of these returns before the plan is used, so none of them can have touched the font, and the tool says which.

The third kind I can only show from the stand-in. Told to fail half-way, it printed the tool's two words and then a sentence of the shape Fly builds: the name of the commit, what went wrong, and what to do. The middle part here is my stand-in's invention:

```text
Stopped part-way: Shift sidebearings did not finish: the stand-in was told to fail. Native changes may remain; use Edit > Undo.
```

## Break it on purpose

Delete the line `self.rehearse.setChecked(True)`. Untick the box and click twice. The label says `Change 2 from this window.` and the `n` has moved twice: chapter 123's accident is back. One line stood between Ines and that.

Put the line back. Now swap the two `except` blocks, so that `except Exception` comes first. Open a Glyph window, so that it's in front, untick the box and click. Fly refuses to commit from there, with a `ValueError`. But `Exception` fits every error, it comes first, and Python never reaches the second block. The label says `Stopped part-way`, and the sentence `Nothing was changed.` is gone. Nothing was written, yet Ines is told the opposite, and if she reaches for Undo it takes back whatever she did before. That's a worse fault than the one the message was written for. Order the `except` lines from the narrowest to the widest, always.

## What you learned

A tool earns trust by asking its cheap questions first and leaving at the first bad answer, with a message that says what to do next. `history.refusals` tells you before the click what the commit would refuse, so a refusal becomes a line in the report. Two `except` lines keep "nothing was changed" apart from "something may have changed", and the narrow one goes first. After a real change, the slot puts the window back in its safe state.

## Try it yourself

1. When the names field is empty, the tool uses the selection without saying so. Add a line to the label for that case, such as `Using the 12 selected glyphs.`
2. Give the tool a limit: with more than 40 rows and the box unticked, return a message that asks for a rehearsal first, and `False`. Decide how the tool should know that a rehearsal has happened.
3. Change `shift` so that a refused name stops the whole click. Run `n ncaron` both ways and write down which behaviour you'd want for sidebearings, and which for a script that deletes contours.

## Next

The tool is fit to hand over. Ines still starts it by opening the Scripting panel, finding the file and pressing Run, and she has said what she thinks of that. Chapter 132 puts the tools where the rest of FontLab's commands live: in the **Scripts** menu, sorted, under names she'd recognise.
