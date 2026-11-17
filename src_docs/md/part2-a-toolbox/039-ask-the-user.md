---
this_file: src_docs/md/part2-a-toolbox/039-ask-the-user.md
---

# 39. Ask before you act

Wednesday. The publisher has changed its mind again about the alternates, and this time Mira is at the dentist. Ines opens `rename_suffix.py`, looks at the two lines at the top that say `OLD_SUFFIX = ".alt"` and `NEW_SUFFIX = ".ss01"`, looks at `DRY_RUN = True`, and closes it without touching anything. When Mira gets back there's a note on her keyboard: *I don't open the hood. Can't it ask me?*

It's a fair request. Until now, every script in this book has taken its orders from lines you edit before you run it. That's fine for the person who wrote the script. For anyone else, a script should ask its questions on the screen, in a small window with buttons, as every other program does.

Today's script asks three things: which suffix, what to change it to, and "Rename 4 glyphs?" It does nothing until the answer is Yes.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `rename_suffix.py` from [chapter 31](031-dry-run.md).
- An empty window in the Scripting panel for Steps 3 to 5. Save it as `questions.py`. Each step adds functions to the top and a test to the bottom.
- The four glyphs that chapter 30 renamed: `a.ss01`, `g.ss01`, `y.ss01` and `ampersand.ss01`. Today the publisher wants them to end in `.ss02`. When the finished script asks, type `.ss01` over the first suggestion and `.ss02` over the second, and the count in the last question will be 4. `zero.alt` is still in the font from chapter 31, and the script goes on leaving it alone.

I couldn't run these windows on FontLab 9 while writing this chapter. The calls are taken from the helper's own source and from scripts that use it, so I describe what the windows should look like, and I show no pictures of them.

## Step 1: Say something in a window

Start with the simplest window there is, one that says a thing and waits for you to click OK:

```python
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

box = qt.QtGui.QMessageBox

run_standard_message_box(qt, fl.MainWindow(), "Halfmoon", "Hello, Ines.", "Information", box.Ok)
```

Run it. A small window should appear over FontLab with the words `Hello, Ines.` and an OK button. Nothing else in FontLab responds until you click it. Then the script goes on, and as this was its last line, it ends.

That call has six slots, which is a lot. Take them in order.

`qt` is new in the first line. It's another of Fly's short names, like `fl`. It stands for the kit of parts that FontLab's own windows are built from: buttons, text fields, checkboxes, whole windows. The helper needs to be handed the kit, so you pass it in the first slot.

`fl.MainWindow()` is FontLab's main window. The message window needs a parent, which is the window it belongs to and sits in front of. Give it the main window and it will appear over FontLab and not behind it.

Then there are two pieces of text. `"Halfmoon"` is the title of the small window, and `"Hello, Ines."` is the message. On a Mac the title may not be shown, so don't put anything important in it.

`"Information"` picks the little picture beside the message. The other words you can use here are `"Question"`, `"Warning"` and `"Critical"`.

And `box.Ok` says which buttons the window has. `box` is a short name I made on the line above for `qt.QtGui.QMessageBox`, which is the part of the kit that knows about message windows, and `Ok` is one of its drawers.

You typed all that to make a window say hello. In Step 3 we'll wrap it so you never have to type it again.

## Step 2: A question with two buttons

A message with one button tells. A message with two asks:

```python
answer = run_standard_message_box(
    qt, fl.MainWindow(), "Halfmoon", "Rename 4 glyphs?", "Question", box.Yes | box.No
)

if answer == box.Yes:
    print("Renaming.")
else:
    print("Left alone.")
```

Two things changed. The buttons slot now holds `box.Yes | box.No`. The upright bar is the same sign that joined two sets in chapter 25. Here it joins two buttons into one value that means "both of these".

And this time we catch what the function hands back. When you click a button, the window closes and the call returns a value that says which one. Compare it with `box.Yes` to find out.

Run it twice, and click a different button each time.

```text
Renaming.
```

```text
Left alone.
```

There's a trap here that prints no error, so I'll warn you about it now. It's tempting to write this:

```python
if answer:
    print("Renaming.")
```

Chapter 31 taught you that `if` accepts anything and treats empty things and zero as false. But the answer isn't `True` or `False`. It's a code for a button, and the code for No isn't zero either. So `if answer:` is true whichever button was clicked, and the script would rename the glyphs when Ines said No. Always compare the answer with the button you mean.

Notice also what the `else` covers. It runs for No, and it also runs for anything else that might come back, such as the window being closed with the ++esc++ key. That's deliberate. Only an explicit Yes changes the font, and everything else leaves it alone. Write your questions so that the safe thing happens by default. It's the idea behind `DRY_RUN` again.

## Step 3: Wrap it once

Nobody wants to type six slots every time they ask a question. You know what to do about that: a function. Start `questions.py` with these lines:

```python
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box, run_text_dialog

TITLE = "Halfmoon Type"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes
```

Look at the last line of `ask`. The comparison `answer == box.Yes` is itself a value, `True` or `False`, as chapter 13 said, so the function can hand it straight back. All the business with button codes stays inside the function. From outside, `ask` takes a question and returns a yes or a no. Below the functions, the script can now say:

```python
if ask("Rename 4 glyphs?"):
    print("Renaming.")
```

That reads almost like the note on Mira's keyboard, and now `if` on the answer is safe, because `ask` really does return `True` or `False`. The trap from Step 2 is dealt with in one place, and no script that uses `ask` can fall into it.

This is the best use of a function that I know. You find something awkward, you get it right once with care, and you give it a plain name. After that you use the plain name, and when a script needs it you paste the same few lines in. Chapter 40 keeps a clean copy of them for exactly that.

## Step 4: Ask for a word

A yes or a no won't tell the script which suffix. For that you need a window with a text field. Add this below `ask`:

```python
def ask_text(label, start=""):
    return run_text_dialog(qt.QtGui, label, start, TITLE)
```

`run_text_dialog` takes the kit, the label beside the field, the text that's in the field to begin with, and the window's title. It returns what the person typed. Try it:

```python
old = ask_text("Suffix to replace:", ".alt")
print(old)
```

A window should appear with a field that already contains `.alt`. Click OK and you get:

```text
.alt
```

Giving the field a sensible starting value is a kindness. Most of the time Ines will only have to press ++return++.

Now tidy up what comes back, because people type spaces by accident. Chapter 27 has the tool for that. Replace the test lines at the bottom of `questions.py` with this one:

```python
old = ask_text("Suffix to replace:", ".alt").strip()
```

Run it, and this time click Cancel.

```text
Traceback (most recent call last):
  File "<string>", line 24, in <module>
AttributeError: 'NoneType' object has no attribute 'strip'
```

Read it as chapter 38 taught you, last line first. Something was `None`, and the script asked it to `strip`. The trail has one step, and it's in your script. So what on that line could be `None`? It can only be whatever `ask_text` handed back.

That's how the helper reports a Cancel. When the person clicks OK, it returns the text, and an empty field gives an empty string `""`. When the person clicks Cancel, there's no text to return, so it returns `None`. It's the same signal `font["Nope"]` gave you in chapter 19, and it needs the same care: check for `None` before you do anything with the answer.

```python
old = ask_text("Suffix to replace:", ".alt")
if old is None:
    print("Cancelled.")
else:
    old = old.strip()
    print("Replacing", old)
```

A person who clicks Cancel is telling you something clear, and the script should stop and change nothing. If it shows a traceback at that point, or carries on with a guess, it has got that wrong.

## Step 5: Choose a file

The third kind of question is "which file?" Every program you use asks it the same way, with the system's own file window, and your scripts can too. In chapter 27 the glyph list had to be called `smallcaps.txt` and sit next to the font. Now Ines can pick any list from anywhere.

Add one more import and two more functions. The import goes at the top with the others, the functions below `ask_text`:

```python
from fly.ap.ui.dialogs import run_file_dialog


def text_files_only(kind, dialog):
    dialog.setNameFilters(["Text files (*.txt)"])


def choose_text_file(caption, folder=""):
    paths = run_file_dialog(qt.QtGui, text_files_only, caption, folder)
    if paths is None:
        return None
    return paths[0]
```

`run_file_dialog` wants the kit, then a function, then the caption for the window and the folder to start in. The function in the second slot is a recipe card, as in chapter 29. The helper makes the file window, and before it shows the window it calls your function and hands it two things: the part of the kit that knows about file windows, and the window itself. Your function gets one chance to set the window up. Ours tells it to show only files that end in `.txt`. It doesn't use `kind` at all, but the slot has to be there because the helper fills it.

The helper returns a list of paths, because a file window can allow several files to be picked, or `None` for Cancel. We want one file, so `choose_text_file` hands back the first item and passes a `None` along untouched.

```python
from pathlib import Path

font = fl.CurrentFont()
folder = str(Path(font.path).parent)
path = choose_text_file("Choose a glyph list", folder)
if path is not None:
    print(Path(path).name)
```

```text
smallcaps.txt
```

What comes back is a string that holds the full path. Wrap it in `Path(...)` and you have everything chapter 26 taught you about paths.

Chapter 26 said a Save dialog would come. Here's that other file window, the one that asks where to save. It's the same helper with a different recipe card, and this card does use `kind`:

```python
def for_saving(kind, dialog):
    dialog.setAcceptMode(kind.AcceptSave)
    dialog.setNameFilters(["Text files (*.txt)"])


def choose_save_file(caption, folder=""):
    paths = run_file_dialog(qt.QtGui, for_saving, caption, folder)
    if paths is None:
        return None
    return paths[0]
```

`setAcceptMode(kind.AcceptSave)` turns the window into a Save window, with a field for typing a new name. Choosing a path doesn't write anything. It only gives your script a path, and the `with open(...)` lines from chapter 26 do the writing.

## When not to ask

Now that you know how to put up a window, you'll want to put up a lot of them. Hold back.

A script that asks five questions in a row is worse than one with five lines to edit. Ask only what changes from one run to the next, and give each field a good starting value. Things that never change belong at the top of the script as constants.

Never ask inside a loop. "Rename `a.alt`? Rename `g.alt`? Rename `y.alt`?" is how you train a person to click Yes without reading. Show the whole plan and ask once.

Don't confirm things that are harmless. A report needs no "Are you sure?" Keep the question for the moment before a script changes the font or writes over a file.

And these windows stop everything else. While one is open, Ines can't click on the font to check something. For a quick question that's right. For a tool that someone keeps open and uses all afternoon, you want a small panel that sits beside the font and stays out of the way. That's a larger piece of building, and Part 7 is where we do it.

## The whole script

Here is `ask_first.py`. It's `rename_suffix.py` from chapter 31 with the two suffixes and the dry-run switch replaced by three questions. It carries its own `tell`, `ask` and `ask_text`, copied from Steps 3 and 4, so it runs by itself:

```python
#FLM: Rename Suffix
# Renames glyphs from one suffix to another, after asking.
from fly import fl, qt
import fly.ap.glyphs.names.model as names
from fly.ap.glyphs.identity_tools.glyph_identity.batch_rename import (
    plan_renames,
    apply_renames,
)
from fly.ap.ui.dialogs import run_standard_message_box, run_text_dialog

TITLE = "Halfmoon Type"
SKIP = {"zero.alt"}


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes


def ask_text(label, start=""):
    return run_text_dialog(qt.QtGui, label, start, TITLE)


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return

    old = ask_text("Suffix to replace:", ".alt")
    if old is None:
        return
    new = ask_text("Replace it with:", ".ss01")
    if new is None:
        return
    old = old.strip()
    new = new.strip()
    if not old:
        tell("Type the suffix to replace.")
        return

    pairs = []
    for glyph in font.glyphs:
        if glyph.name.endswith(old) and glyph.name not in SKIP:
            pairs.append([glyph.name, glyph.name.removesuffix(old) + new])

    if not pairs:
        tell(f"No glyph name ends in {old}.")
        return

    facts = names.scan()
    problems = 0
    for before, after, status in plan_renames(facts, pairs):
        print(f"{before:<18}{after:<18}{status}")
        if status != "ok":
            problems += 1

    if problems > 0:
        tell(f"{problems} of {len(pairs)} renames can't be done. The list is in the Output panel.")
        return

    if not ask(f"Rename {len(pairs)} glyphs from {old} to {new}?"):
        return

    done = apply_renames(None, qt.QtCore, facts.package_id, pairs)
    tell(f"Renamed {len(done)} glyphs. Edit > Undo takes it back in one step.")


main()
```

It has the same four parts as before: collect, plan, show, apply. What changed is where the orders come from and where the news goes.

Count the `return`s. There are seven ways out of this script before it touches the font, and only one way through: a font is open, two questions were answered, something matched, every status is `ok`, and somebody clicked Yes. Chapter 19 called these guard clauses, and a script that other people will run needs plenty of them.

Notice what it still prints. The plan goes to the Output panel and not into a window, because twenty rows of names don't belong in a message box. A window is for one sentence and a decision. Anything you'd want to read slowly, copy or keep belongs in the Output panel or a file.

And notice the final message. It says what happened, in numbers, and it says how to take it back.

Look at the guard after the two `strip` lines. Every name ends with the empty string, so an empty answer would have asked to rename the whole font. `SKIP` stays at the top, because it never changes from one run to the next.

Save it as `Rename Suffix.py` in the `Halfmoon` folder inside `Scripts`, and choose **Scripts > Refresh Scripts**. Its first line gives it its name in the menu. Ines runs it that afternoon without opening anything.

## What you learned

A message box tells or asks in a small window, and its answer is a button code that you compare with the button you mean. A text dialog returns what was typed, a file dialog returns a list of paths, and both return `None` for Cancel, which you check before anything else. The awkward calls go in a function once, behind plain names like `ask`, `tell` and `ask_text`, and the script carries the functions it uses. Ask once, right before the change, and let anything but Yes leave the font alone.

## Try it yourself

1. Add `warn(text)` to `ask_first.py`. It's `tell` with `"Warning"` in the picture slot. Use it in `ask_first.py` for the message about renames that can't be done.
2. Write `ask_number(label, start)` in `questions.py`. It calls `ask_text`, hands a `None` straight back, and otherwise returns `int(...)` of the text. Then type `fifteen` into its window and read the traceback. Chapter 19 showed you `try` and `except` in one simple form. Use it so that a word in place of a number makes `ask_number` return `None` as well. Then paste it, with `ask_text`, into `safe_edit.py` from chapter 29, so that Ines can type her own amount.
3. Change `read_glyph_list.py` from chapter 27 so that it calls `choose_text_file` in place of the fixed name. Paste in `text_files_only` and `choose_text_file` from Step 5, with the imports they need. What should the script do if the answer is `None`? What if the chosen file turns out to be empty?

## Next

It's Friday again, and Ines wants to know what seven weeks of this have bought the studio. Chapter 40 puts the toolbox on the table and counts.
