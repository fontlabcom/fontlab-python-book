---
this_file: src_docs/md/part7-tools/123-ask-for-a-number.md
---

# 123. Ask for a number

Wednesday afternoon, week twenty-four. Ines has a page of the catalog on her screen, set in the Regular, and three letters on it look tight to her: `n`, `o` and `H`.

"Give them some air. Both sides."

"How much?"

"I don't know yet. Ten? Show me ten."

In Part 4 Mira would have opened `set_sidebearings.py`, changed two numbers at the top, and run it. Ines won't do that, and from tomorrow Mira isn't here. So the numbers have to move out of the script and into the window: a field for the glyph names, a field for each side, a tick box that says "don't change anything yet", and a button.

## What you need

`Plum-practice` open with the Font window in front and the Regular master showing, Fly installed, and `button_report.py` from chapter 122 to copy from. This chapter changes sidebearings, so save the font first.

I haven't run this chapter in FontLab 9. I ran the script in plain Python with stand-in widgets whose fields I could fill from code, and a stand-in font that holds Plum's sidebearings. The numbers below are Plum's Regular as it shipped. If Part 4 left yours different, your first three numbers on each line will differ and the sums will still hold.

## Step 1: A field, and what's in it

A field you can type in is a widget called `QLineEdit`. Take chapter 122's `build`, cut it down to one field, one button and one label, and make the button show what the field holds:

```python
def read(owner, name):
    item = getattr(owner, name)
    return item() if callable(item) else item


def build(parent):
    panel = gui.QWidget(parent)
    amount = gui.QLineEdit("12", panel)
    go = gui.QPushButton("Shift", panel)
    label = gui.QLabel("", panel)

    def on_go(*args):
        label.setText(read(amount, "text"))

    go.clicked.connect(on_go)
    layout = gui.QVBoxLayout(panel)
    layout.addWidget(amount)
    layout.addWidget(go)
    layout.addWidget(label)
    return panel
```

The field opens with `12` in it, because that's the first thing handed to `QLineEdit`. Click **Shift** and the label says `12`. Type `8` over it, click, and the label says `8`.

The new piece is `read`. A field keeps what you typed under the name `text`. In some versions of the Qt that FontLab carries, `amount.text` is the text itself, and in others it's a function you call to get the text. `read` takes either. `getattr`, from chapter 95, fetches whatever sits under that name. `callable` is a built-in function that answers `True` when the thing you hand it can be called with brackets. If it can, `read` calls it, and if not, `read` hands it back as it is. The scripts that come with Fly carry the same four lines, and from here on so does every window in this book.

Notice when the reading happens: inside `on_go`. The field is read at the moment of the click, each time. If you read it once in `build`, you'd get `12` forever, because `build` runs before anybody has typed.

## Step 2: The mistake

Ten units on a width of 523. Change `on_go` to do the sum:

```python
def on_go(*args):
    label.setText(str(523 + read(amount, "text")))
```

Click, and nothing happens. There's no `try` in this slot yet, so the error went wherever FontLab sends errors from slots, which I haven't seen. Chapter 122 said what to do about that. Wrap it:

```python
def on_go(*args):
    try:
        label.setText(str(523 + read(amount, "text")))
    except Exception as problem:
        label.setText(f"{type(problem).__name__}: {problem}")
```

```text
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

Chapter 23 used `int` to read text, and this is where you need it. What comes out of a field is text, always, even when every character in it is a digit. `"12"` is two characters. Had you written the sum the other way about, text plus text, Python would have said nothing and given you `"1212"`.

`int` reads text as a whole number, so `523 + int(read(amount, "text"))` gives 535. Then Ines types `a lot`:

```text
ValueError: invalid literal for int() with base 10: 'a lot'
```

The same for `12.5`, and the same for a field with nothing in it. You could catch the `ValueError` and write a kinder message, as `ask_factor` did in chapter 68. But look at what you'd be doing: letting a person type anything, then telling them off for it. A field that can't hold anything but a whole number would be kinder still.

## Step 3: A field that only holds numbers

That widget is `QSpinBox`. It shows a number with two small arrows beside it. You can type digits into it or click the arrows, and it won't accept a letter.

```python
left = gui.QSpinBox(panel)
left.setRange(-200, 200)
```

`setRange` says how far the number may go each way. A spin box keeps its number under the name `value`, and it's a number already:

```python
def on_go(*args):
    label.setText(str(523 + read(left, "value")))
```

No `int`, no `try` for bad text, and nothing for Ines to get wrong. That's the idea to keep from this chapter: choose the widget so that the wrong answer can't be typed. Use a line edit when the answer is words, as it will be for the glyph names.

## Step 4: Yes or no

Every script in this book that changes a font has had a `DRY_RUN` line since chapter 31. In a window, that line is a tick box, a `QCheckBox`:

```python
rehearse = gui.QCheckBox("Only show what would happen", panel)
rehearse.setChecked(True)
```

The text is its label, and `setChecked(True)` makes it open with the tick already in. It keeps its state under the name `checked`, and `read(rehearse, "checked")` gives `True` or `False`. Starting with the tick in means a first click shows numbers and changes nothing.

So three kinds of field give three kinds of value: text from a line edit, a whole number from a spin box, `True` or `False` from a tick box.

## The whole script

Save this in your Scripts folder as `shift_dialog.py`:

```python
#FLM: Shift Dialog
# Adds to the sidebearings of the glyphs you name, or of the ones
# selected in the Font window, in the master that's showing.
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.metrics.panel.model as metrics
from fly import fl, qt
from fly.pens import layer_of
from fly.tr.proxy.fl.objects.glyph import pGlyph

core, gui = qt.QtCore, qt.QtGui
KEY = "tools.shift"
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


def build(parent):
    panel = gui.QWidget(parent)
    panel.setWindowFlags(core.Qt.Tool)
    panel.setWindowTitle("Shift")
    panel.setAttribute(core.Qt.WA_DeleteOnClose)
    names = gui.QLineEdit("", panel)
    left = gui.QSpinBox(panel)
    left.setRange(-LIMIT, LIMIT)
    right = gui.QSpinBox(panel)
    right.setRange(-LIMIT, LIMIT)
    rehearse = gui.QCheckBox("Only show what would happen", panel)
    rehearse.setChecked(True)
    go = gui.QPushButton("Shift", panel)
    label = gui.QLabel("", panel)

    def on_go(*args):
        try:
            label.setText(shift(read(names, "text"), read(left, "value"),
                                read(right, "value"), read(rehearse, "checked")))
        except Exception as problem:
            label.setText(f"Didn't work.\n{type(problem).__name__}: {problem}")

    go.clicked.connect(on_go)
    layout = gui.QVBoxLayout(panel)
    layout.addWidget(gui.QLabel("Glyphs", panel))
    layout.addWidget(names)
    layout.addWidget(gui.QLabel("Left", panel))
    layout.addWidget(left)
    layout.addWidget(gui.QLabel("Right", panel))
    layout.addWidget(right)
    layout.addWidget(rehearse)
    layout.addWidget(go)
    layout.addWidget(label)
    return panel


scripting.show_script_dialog(build, KEY)
```

It's the longest listing in a while, and most of it is old. Read it in three parts.

`plan_rows` is chapter 62's arithmetic. For each name it measures the three numbers, and works out the three new ones: the left side grows by `left`, the right by `right`, and the width by both. A name that isn't in the font stops everything with a `raise`, as in chapter 97.

`shift` knows nothing about windows. It takes text, two numbers and a yes-or-no, and gives back the text for the label. An empty names field means "use the glyphs selected in the Font window", which is chapter 15's `names_selected_names`. When nothing is selected there either, that helper falls back to the current glyph. `package.master` is the master that's showing, from chapter 101. The change itself is chapter 62's: `shift_and_set` moves the outline by `left` and sets the new width, inside one `history.commit`, with `allow_bases=True` for the reason chapter 55 gave. One click, one step in **Edit > Undo**.

`build` is the only part that knows about widgets. It makes them, and `on_go` reads all four at the moment of the click and hands plain values to `shift`. Keeping the two apart costs nothing now and pays in chapter 139, when you'll test `plan_rows` without a window or a font.

The small labels `Glyphs`, `Left` and `Right` are made inside `addWidget`, with no box to keep them in, because nothing will ever read them again.

## Run it

Run the script. A window titled Shift opens: three fields stacked with their labels, a tick box, a button. Type `n o H` in the first field, set both numbers to 10, leave the tick in, and click **Shift**:

```text
n: 70 523 66 to 80 543 76
o: 38 520 38 to 48 540 48
H: 76 672 70 to 86 692 80
Regular: 3 would change.
```

Each line reads left side, width, right side, before and after. Ines looks at the numbers, nods, takes the tick out, and clicks again. The last line now says `Regular: 3 changed.` She looks at her page. It's better. She clicks once more, by accident:

```text
n: 80 543 76 to 90 563 86
o: 48 540 48 to 58 560 58
H: 86 692 80 to 96 712 90
Regular: 3 changed.
```

The window is still open and still armed, so a second click did the job a second time. **Edit > Undo**, once, takes back the second click, and the `n` is at 80, 543, 76 again. Each click was one step. Chapter 131 comes back to this: a tool that people use without reading should be harder to fire twice.

Now type `n zz` in the names field and click:

```text
Didn't work.
ValueError: No glyph called zz.
```

Nothing changed, not even the `n`, because `plan_rows` reads every name before `shift` touches anything.

## Break it on purpose

Delete the line `left.setRange(-LIMIT, LIMIT)` and run the script again. Try to type `-10` into **Left**. The minus sign won't go in. A spin box that hasn't been told its range allows 0 to 99, so Ines could widen and never tighten. The other field still takes -10. Put the line back.

Then, in `on_go`, change `read(left, "value")` to `read(left, "text")`. A spin box has a `text` as well, the digits as it shows them. Set 10 and 10, type `n o H`, click:

```text
Didn't work.
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

It's Step 2's error, reached from a widget that was meant to make it impossible. The widget keeps letters out of the field, but the script still has to ask it for the number and not for the text. Change it back.

## What you learned

A line edit holds text, a spin box holds a whole number within a range, and a tick box holds `True` or `False`; `read` fetches each by name. A slot reads its fields at the moment of the click, never earlier. Pick the widget that can't hold a wrong answer, and you write less checking. Keep the function that does the work free of widgets, so that it takes plain values and gives back text.

## Try it yourself

1. Add a second tick box, **Both sides the same**. When it's ticked, `on_go` should hand `shift` the left number twice and ignore the right field.
2. Make the last line of a rehearsal say how much wider the glyphs get in total: for the run above, `Regular: 3 would change, 60 units wider.`
3. Type `n n` in the names field with the tick in, and read the two lines. Then decide what the tool should do about a name given twice, and make `shift` do it. A set, from chapter 25, loses the order; a loop that skips names it has seen keeps it.

## Next

The tool works, and it looks like a pile: label, field, label, field, a button as wide as the window. Ines says it's ugly, and she's the one who lays out pages for a living. Chapter 124 arranges it in rows and columns.
