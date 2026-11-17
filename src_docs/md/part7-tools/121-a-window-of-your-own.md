---
this_file: src_docs/md/part7-tools/121-a-window-of-your-own.md
---

# 121. A window of your own

Tuesday of week twenty-four. Oskar is on holiday until January, and Mira has a train to catch on Thursday. That leaves Ines alone with a font, a publisher and a folder of scripts she has never run.

"Show me once," Ines says, and Mira opens the Scripting panel. Ines looks at it for a while. "No. I'm not going to type into that. If you want me to change a number, give me a box with the number in it. If you want me to run something, give me a button."

It's a fair request. Everything you've written so far is driven by text: you edit a name at the top of a script, you run it, you read what it prints. Chapter 39 added small boxes that ask one question and go away. A tool for somebody else needs more than that. It needs a window that stays on the screen, shows something, and waits to be clicked.

This chapter makes the window. It shows three facts about the open font, and it has a button that does nothing yet.

## What you need

`Plum-practice` open, Fly installed, and the Scripting panel. Nothing in the font changes.

I haven't run this chapter in FontLab 9. I ran the script in plain Python with stand-in widgets that record what was asked of them, and with the real code of the Fly function that shows the window. So I can tell you what the script asks for and in which order. I can't tell you what the window looks like on your screen.

## Step 1: The smallest window

Type this and run it:

```python
import fly.ap.core.scripting as scripting
from fly import qt

def build(parent):
    label = qt.QtGui.QLabel("Hello, Ines.", parent)
    label.setWindowFlags(qt.QtCore.Qt.Tool)
    return label

scripting.show_script_dialog(build, "halfmoon.hello")
```

A small window should appear over FontLab with the words `Hello, Ines.` in it. Click in the Font window behind it. Select a glyph. FontLab answers, and the small window is still there. That is the difference from chapter 39, where nothing else responded until you clicked OK. Close the small window with its close button when you've seen enough.

Now the words. The whole of what you see on the screen, with its windows and buttons and menus, is called a graphical user interface, or GUI. Each thing in it is a **widget**: a piece of text is a widget, a button is a widget, the box you type a number into is a widget, and a window is a widget that holds other widgets. A widget is an object, so it's one more wardrobe with drawers, like the glyph in chapter 6. You make one, and then you open its drawers to tell it how to look and what to say.

FontLab is built with a kit of widgets called Qt, and Fly hands you the same kit as `qt`. You met it in chapter 39 as `qt.QtGui`, the drawer where the widgets are. `qt.QtGui.QLabel` makes a **label**, a piece of text that the user can read and can't change. Every name in the kit starts with a capital Q.

The label gets two things: its text, and `parent`. A parent is the widget that a new widget belongs to. Here the parent is FontLab's main window, and you don't have to find it: `show_script_dialog` calls your `build` function and passes the main window in.

A widget with a parent is normally drawn inside that parent. You don't want your text painted in a corner of FontLab's main window, so the next line says otherwise. `setWindowFlags(qt.QtCore.Qt.Tool)` turns the label into a small window of its own that floats over its parent. `Tool` is Qt's word for a little helper window.

## Step 2: Who shows it, and who keeps it

Look at the last line again:

```python
scripting.show_script_dialog(build, "halfmoon.hello")
```

You wrote `build`, not `build()`. You're handing over the function, and Fly calls it when it's ready. Chapter 39 did this with the "recipe card" for the file box, and chapter 119 kept whole lists of functions that way.

`show_script_dialog` does four things with it. It calls `build` with FontLab's main window. It asks for the window you returned to stay in front of other windows. It shows it. And it writes the window down in a list that lives as long as FontLab is open, under the name you gave as the second thing, `"halfmoon.hello"`.

Your script ends a moment after the window appears. Python tidies up after a script, and a window that nothing refers to any more can be thrown away with the rest. The list is what keeps yours. Chapter 127 looks at this properly.

The name has a second use. Run the script again without closing the window. You don't get two windows. Fly finds the old one under `"halfmoon.hello"`, closes it, and opens the new one. In my stand-in run the list held one window after two runs.

## Step 3: A program that waits

Add one line to the end of the script and run it:

```python
print("The script has ended. The window hasn't.")
```

The Output panel shows the sentence, and the window is on the screen at the same time.

```text
The script has ended. The window hasn't.
```

Here is what is going on. FontLab spends nearly all of its time waiting. When you click, press a key or move the mouse, it wakes up, works out which widget that was meant for, lets that widget do its job, and goes back to waiting. This round of wait, wake, work, wait is called the **event loop**, and every program with windows has one.

Until now your scripts were one piece of work inside one turn of that loop. You pressed Run, FontLab ran your lines from top to bottom, and only then went back to waiting. That is why a script that takes a minute makes FontLab look dead for a minute.

A window changes the bargain. The script builds the window, hands it over and ends. The window then belongs to FontLab's loop like any other. FontLab draws it, moves it when you drag it, and closes it when you click the close button, and none of your lines are running while it does. Your code will run again only when somebody clicks something you have connected to a function. That is chapter 122.

One rule follows, and I'll state it once. You never start a loop of your own, and you never create an "application" object, whatever a Qt tutorial on the web tells you to do. FontLab already has both. You make widgets and hand them over.

## Step 4: More than one widget

A label alone is a poor window. To hold two widgets you need a third, plain one to put them in, and something that arranges them:

```python
def build(parent):
    panel = gui.QWidget(parent)
    panel.setWindowFlags(core.Qt.Tool)
    layout = gui.QVBoxLayout(panel)
    layout.addWidget(gui.QLabel("GG Plum", panel))
    layout.addWidget(gui.QPushButton("Look again", panel))
    return panel
```

`QWidget` is the plainest widget there is: an empty rectangle. It's the window now, so it takes the `Tool` flag. `QVBoxLayout` is a **layout**. You don't see a layout. It stacks the widgets you give it from top to bottom (the V is for vertical) and works out their sizes, so you never write a position in pixels. `QPushButton` is a button with its text. The label and the button both name `panel` as their parent, because that is where they live.

`gui` and `core` are short names, set once at the top of the script:

```python
core, gui = qt.QtCore, qt.QtGui
```

Two names get two values in one line, the way chapter 35 gave four names to the four parts of a row.

## Step 5: The mistake

Mira wants it to be clear which of the two things in the brackets is the parent, so she names it, as she has named `encoding="utf-8"` and `allow_bases=True` a hundred times:

```python
layout.addWidget(gui.QLabel(font_text(), parent=panel))
```

No window appears. The Output panel has a traceback that ends in a `ValueError`, and the message ends with the words `called slot does not support kwargs`. I didn't see that message myself. Fly's notes on Qt record it from FontLab 9, for labels, buttons, layouts and a dozen other widgets.

"Kwargs" is short for keyword arguments, the `name=value` kind. FontLab's Qt kit doesn't accept them, anywhere. Every value goes in by position, in the order the kit expects: the text first, the parent last.

```python
layout.addWidget(gui.QLabel(font_text(), panel))
```

This will catch you again, because the rest of Python has taught you that naming an argument is the careful thing to do. With Qt widgets inside FontLab it's the one thing that never works.

## The whole script

Save this as `hello_window.py` in your Scripts folder.

```python
#FLM: Hello Window
# Opens a small window that says which font is open.
# The button doesn't do anything yet. Chapter 122 wires it up.
import fly.ap.core.scripting as scripting
from fly import fl, qt

core, gui = qt.QtCore, qt.QtGui
KEY = "halfmoon.hello"


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


def build(parent):
    panel = gui.QWidget(parent)
    panel.setWindowFlags(core.Qt.Tool)
    panel.setWindowTitle("Halfmoon")
    panel.setAttribute(core.Qt.WA_DeleteOnClose)
    layout = gui.QVBoxLayout(panel)
    layout.addWidget(gui.QLabel(font_text(), panel))
    layout.addWidget(gui.QPushButton("Look again", panel))
    return panel


scripting.show_script_dialog(build, KEY)
print("The script has ended. The window hasn't.")
```

`font_text` has nothing to do with windows. It builds a string from things you know: the family name and version from chapter 95 and chapter 97, the glyph count from chapter 4, the masters from chapter 101. Keeping it apart from `build` means you can test it with `print(font_text())` and no window at all.

Two lines in `build` are new. `setWindowTitle` puts a word in the window's title bar. `setAttribute(core.Qt.WA_DeleteOnClose)` decides what the close button means. Without it, closing a window only hides it, and it goes on existing where nobody can see it. With it, a closed window is gone.

`KEY` is the name the window is kept under. Give every tool its own. A good habit is your studio's name, a dot, and the tool's name.

## Run it

With `Plum-practice` open, the script asked my stand-in for a window titled `Halfmoon` holding this text and a button marked `Look again`:

```text
GG Plum
Version 1.004
274 glyphs, 3 masters
```

The version is 1.004 because Friday's build raised it after shipping 1.003. Your glyph count may differ from mine if your practice font does.

Close every font and run it again. The window says `No font is open.` That is the early `return` in `font_text`. A tool for somebody else is run in all the situations you would never put yourself in, and the first of them is always "nothing is open".

Mira calls Ines over. Ines reads the three lines and clicks **Look again**. The button goes down and comes up, and nothing happens. She clicks it again.

"It's not connected to anything yet," says Mira.

"Then why is it there?"

## Break it on purpose

Delete the line `return panel` and run the script.

```text
AttributeError: 'NoneType' object has no attribute 'setWindowFlags'
```

Chapter 24 showed that a function with no `return` hands back `None`. `build` made a perfectly good window and then kept it to itself. Fly got `None`, tried to open one of its drawers, and Python refused. The traceback points into Fly's file, not yours, which is unhelpful, so remember the shape of this one: `'NoneType' object has no attribute` right after you call somebody else's function with a function of your own usually means your function forgot to return. Put the line back.

Now change `KEY` to `"halfmoon.hello2"` and run the script without closing the window. You have two windows. Fly looked for an old window under the new name, found none, and left the first alone. Close both and change the name back.

Last, with the window open, open another font and bring it to the front. The window still says GG Plum. It read the font once, while `build` ran, and a label doesn't know where its text came from. This is what the button is for.

## What you learned

A window is a widget that holds other widgets, and a layout arranges them so that you never write a position. Your script builds the window, hands it to `show_script_dialog` and ends, and from then on FontLab's event loop looks after it. The name you pass keeps the window alive and replaces an older window of the same tool. Inside FontLab, Qt widgets take their values by position only, never as `name=value`.

## Try it yourself

1. Add a second label under the first that shows the name of the font's file. The path is `font.path`, and chapter 26's `Path(...).name` cuts the folder off. Decide what it should say when the font has never been saved.
2. Change `QVBoxLayout` to `QHBoxLayout` and run it. Describe in one sentence what the H stands for.
3. Put the button first and the label second. You only need to swap two lines, and you never touch a position.

## Next

Ines has a window and a button that does nothing. Chapter 122 connects the button to a function, so that a click reads the font again.
