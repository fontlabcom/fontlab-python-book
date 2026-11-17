---
this_file: src_docs/md/part7-tools/124-lay-it-out.md
---

# 124. Lay it out

Thursday morning of week twenty-four. Mira's train leaves at noon. Ines has the Shift window open beside a page proof, and she's looking at the window the way she looks at a page somebody else set.

"Nine things in a column," she says. "The word Left has a whole line to itself. The button is as wide as a headline."

She takes a pencil and draws what she'd have made: the names field with its word beside it, the two numbers side by side, the tick box and the button sharing the bottom line, and the answer underneath.

"That," says Mira, "is three boxes inside a box. You've drawn the program."

## What you need

`Plum-practice` open with the Regular showing, Fly installed, and `shift_dialog.py` from chapter 123. The script does the same work as yesterday. Only the arrangement changes.

I haven't run this chapter in FontLab 9. I ran the script in plain Python with stand-in widgets and stand-in layouts that record what was put into what, and the trees printed below come from those records. I can't show you how the window looks, and I won't describe pixels I haven't seen. The two warning texts in this chapter are Qt's own, written from memory.

## Step 1: Read the pencil sketch

Here is Ines's drawing, as an outline:

```text
column
    form:  Glyphs + names field
    row:   Left, left box, Right, right box
    row:   tick box, Shift button
    answer label
```

A layout is an object that owns a strip of the window and decides where the things in it go. You met one in chapter 121: `QVBoxLayout`, where the V is for vertical. It stacks. Yesterday you gave it nine widgets and it stacked nine.

There are two more kinds in the sketch. `QHBoxLayout`, H for horizontal, puts things side by side. If you did chapter 121's second exercise, you've tried it. `QFormLayout` makes lines of a word and a field, with the words lined up on one edge.

The new idea is the indentation in the outline. A layout can hold widgets, and it can hold other layouts. You've seen this shape before. Chapter 35 put lists inside a list to make a table, and the outer list didn't care what its rows held. It's the same here: the column holds four things, and three of them happen to be layouts with things of their own.

## Step 2: One row

Open `shift_dialog.py` and find the end of `build`, where the layout is made. Change the part that adds the tick box and the button:

```python
    bottom = gui.QHBoxLayout()
    bottom.addWidget(rehearse)
    bottom.addWidget(go)
    layout.addLayout(bottom)
```

Those four lines replace `layout.addWidget(rehearse)` and `layout.addWidget(go)`. Run the script.

Look at the first line. Yesterday's layout was made with `gui.QVBoxLayout(panel)`, and the panel in the brackets meant "you are this panel's layout". This one has empty brackets. It belongs to nobody yet. The last line gives it a home: `addLayout` puts a layout into a layout, as `addWidget` puts a widget into one.

In my stand-in, the record now reads:

```text
VBox (column)
  Label 'Glyphs'
  LineEdit
  Label 'Left'
  SpinBox
  Label 'Right'
  SpinBox
  HBox (row)
    CheckBox 'Only show what would happen'
    PushButton 'Shift'
  Label ''
```

Seven things in the column where there were nine, and one of the seven is a row with two things in it.

## Step 3: A row and a form

Do the same for the two numbers. Their labels have to be made first, since a row can only hold what exists:

```python
    sides = gui.QHBoxLayout()
    sides.addWidget(gui.QLabel("Left", panel))
    sides.addWidget(left)
    sides.addWidget(gui.QLabel("Right", panel))
    sides.addWidget(right)
    layout.addLayout(sides)
```

These replace the four lines that added Left, `left`, Right and `right` to the column.

The names field gets the third kind of layout:

```python
    form = gui.QFormLayout()
    form.addRow("Glyphs", names)
    layout.addLayout(form)
```

`addRow` takes the word and the field together. You hand it plain text, and it makes the label for you and stands it beside the field. So the two lines that added a Glyphs label and `names` go, and no `QLabel` is written for this line at all. A form with one line may look like a lot of machinery. It earns its place when the tool grows a second field, since every word in a form lines up with the others, and a row of loose labels doesn't.

The order of the `addLayout` lines is the order down the window. Put the form first, then `sides`, then `bottom`, then the answer label.

## Step 4: The mistake

You'll write this one sooner or later, since it's one word of habit. Change the form's first line to match the way the column was made:

```python
    form = gui.QFormLayout(panel)
```

Run it. My stand-in, which copies what Qt does here, prints the line below. I expect it in the Output panel, though I haven't seen where FontLab puts Qt's own complaints:

```text
QLayout: Attempting to add QLayout "" to QWidget "", which already has a layout
```

Which layout is turned away depends on which was made first. In your script as it stands the column came first, so the form is the one refused, and I haven't seen what the window does with a refused form. In the finished script below the form is made before the column. There the form takes the panel and the column is refused, and my record showed a panel whose whole layout was this:

```text
Form (form)
  'Glyphs' + LineEdit
```

One line in the window, and the rest of the widgets left with no place. Nothing stops, and no traceback appears. It's a warning, printed once, about a window that looks wrong.

A panel has one layout. That one is the outermost box of the sketch, and it's the only one that gets the panel in its brackets. Every other layout is made with empty brackets and is put into its parent with `addLayout`. Take `panel` out of the form's brackets again.

## Step 5: Give the arranging a function of its own

`build` now does three jobs: it makes the widgets, it wires the button, and it arranges. The arranging is the part you'll change most often, each time somebody like Ines looks at the window. Move it into a function named for the job, and `build` gets shorter and the sketch gets one place to live.

## The whole script

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


def arrange(panel, names, left, right, rehearse, go, label):
    form = gui.QFormLayout()
    form.addRow("Glyphs", names)

    sides = gui.QHBoxLayout()
    sides.addWidget(gui.QLabel("Left", panel))
    sides.addWidget(left)
    sides.addWidget(gui.QLabel("Right", panel))
    sides.addWidget(right)

    bottom = gui.QHBoxLayout()
    bottom.addWidget(rehearse)
    bottom.addWidget(go)

    outer = gui.QVBoxLayout(panel)
    outer.addLayout(form)
    outer.addLayout(sides)
    outer.addLayout(bottom)
    outer.addWidget(label)


def build(parent):
    panel = gui.QWidget(parent)
    panel.setWindowFlags(core.Qt.Tool)
    panel.setWindowTitle("Shift")
    panel.setAttribute(core.Qt.WA_DeleteOnClose)
    label = gui.QLabel("", panel)
    names = gui.QLineEdit("", panel)
    left = gui.QSpinBox(panel)
    left.setRange(-LIMIT, LIMIT)
    right = gui.QSpinBox(panel)
    right.setRange(-LIMIT, LIMIT)
    rehearse = gui.QCheckBox("Only show what would happen", panel)
    rehearse.setChecked(True)
    go = gui.QPushButton("Shift", panel)

    def on_go(*args):
        try:
            label.setText(shift(read(names, "text"), read(left, "value"),
                                read(right, "value"), read(rehearse, "checked")))
        except Exception as problem:
            label.setText(f"Didn't work.\n{type(problem).__name__}: {problem}")

    go.clicked.connect(on_go)
    arrange(panel, names, left, right, rehearse, go, label)
    return panel


scripting.show_script_dialog(build, KEY)
```

Save it. `read`, `plan_rows` and `shift` haven't changed by a character since chapter 123, which is what keeping them apart from the window bought you.

`arrange` reads like the pencil sketch, top to bottom: a form, a row, another row, and then the column that holds all three and the label. The inner layouts are made first, since the column can't be handed a row that doesn't exist yet. Only `outer` has `panel` in its brackets.

`build` makes the widgets, connects the button, and then calls `arrange` with all seven of them. Seven arguments is a long list, and you have to keep the order straight in two places. Leave it for now. Chapter 126 has a better home for a window's widgets than a line of arguments.

## Run it

Run the script. My stand-in's record of the finished window:

```text
VBox (column)
  Form (form)
    'Glyphs' + LineEdit
  HBox (row)
    Label 'Left'
    SpinBox
    Label 'Right'
    SpinBox
  HBox (row)
    CheckBox 'Only show what would happen'
    PushButton 'Shift'
  Label ''
```

Hold it against the outline in Step 1. Four things in the column, in Ines's order.

Type `n o H` in the names field, put 10 in both boxes, leave the tick in, and click **Shift**:

```text
n: 70 523 66 to 80 543 76
o: 38 520 38 to 48 540 48
H: 76 672 70 to 86 692 80
Regular: 3 would change.
```

The same answer as yesterday, for a font in the state Plum ships in. The arrangement has nothing to do with the arithmetic.

Ines pulls the window wider by its corner and watches. What I'd expect, and haven't seen, is that the names field takes the extra room and the button doesn't. Try it and note what each widget does. A layout decides that as well, and it's the reason to use one instead of telling each widget where to sit.

## Break it on purpose

In `arrange`, add a line that puts the left box into the bottom row as well:

```python
    bottom.addWidget(go)
    bottom.addWidget(left)
```

Run it. In my stand-in, which again copies Qt:

```text
QLayout::addChildWidget: QSpinBox "" is already in a layout; moved to new layout
```

and the record shows what "moved" means:

```text
  HBox (row)
    Label 'Left'
    Label 'Right'
    SpinBox
  HBox (row)
    CheckBox 'Only show what would happen'
    PushButton 'Shift'
    SpinBox
```

The left box has gone from its row and sits after the button. A widget is one thing in one place. Adding it a second time doesn't copy it. If you want two boxes, make two. Take the line out.

Then take out a different line: delete `outer.addWidget(label)`, run, and click **Shift**. In my record the label is in no layout at all. It still exists and it still gets the answer, so what Qt does is draw it where a widget with no layout goes, in the panel's top corner, across whatever is there. I haven't seen how that looks in FontLab. When text turns up on top of a field, look for the widget you made and never added. Put the line back.

## What you learned

A layout owns part of a window and places what's in it: `QVBoxLayout` in a column, `QHBoxLayout` in a row, `QFormLayout` in lines of a word and a field. Layouts go inside layouts with `addLayout`, the way chapter 35's lists went inside a list, and a pencil sketch of boxes in boxes is the plan. A panel has one layout, the outermost, and only that one is made with the panel in its brackets. A widget lives in one layout, and one that's in none is drawn in the corner.

## Try it yourself

1. Swap the two rows so the tick box and the button come before the numbers. Before you run it, write the outline you expect, as in Step 1. It's two lines of `arrange`.
2. Move Left and Right into the form: two more `addRow` lines, and `sides` goes. Count the layouts in the outline now. Decide which arrangement you'd give Ines, and why.
3. Put the answer label beside the widgets and not under them. The panel's layout becomes a row, with two things in it: a column holding the form and the two rows, and the label. Remember which layout gets `panel`.

## Next

Ines is content with the window and not with the names field. She has typed `n o H` four times this morning and `ncaron` wrong twice. Chapter 125 takes some of the typing away: the window reads the font, finds the suffixes in its glyph names, and offers them in a list to pick from.
