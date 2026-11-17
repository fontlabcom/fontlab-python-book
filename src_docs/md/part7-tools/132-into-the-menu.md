---
this_file: src_docs/md/part7-tools/132-into-the-menu.md
---

# 132. Into the menu

Wednesday, 30 December. Ines has written out how she starts the Shift tool, step by step, and pinned it to the studio board: open the Scripting panel, open a file, look for `shift_tool.py` among forty others, press Run. Underneath, in red: "Four steps to start one tool."

She's right. A tool you have to hunt for is a tool you'll stop using. Today the Shift tool moves into the **Scripts** menu under a name she'd say aloud, the Halfmoon tools get one tidy place there, and the tool gets a key. The key takes more work than you'd hope, and I'll show you where the limit is.

## What you need

FontLab 9 with Fly installed, `halfmoon.py` with `keep` from chapter 127, and `shift_tool.py` from chapter 131. No font has to be open to follow the steps.

I haven't run this chapter in FontLab 9. I ran the three files in plain Python against stand-ins for the windows and for FontLab's menu bar. What the real menu shows, and whether the key works on your keyboard, are things I haven't seen.

## Step 1: Two folders, two jobs

You've used two folders since chapter 33, and it's time to say plainly what each is for.

The **Scripts folder** is FontLab's. Chapter 18 put your first file there. Every `.py` file in it becomes a line in the **Scripts** menu, a folder inside it becomes a submenu, and the `#FLM:` line at the top of a file is the name the menu shows. FontLab reads the folder when it starts and when you choose **Scripts > Refresh Scripts**.

The **module folder** is Python's. It's the `site-packages` folder you found in chapter 33, where `halfmoon.py` lives. Python looks there when a script says `import`. FontLab's menu never looks there.

So a file in the Scripts folder can be started and can't be borrowed from. A file in the module folder can be borrowed from and can't be started from the menu. Chapter 114 moved `preflight.py` from one to the other for that reason, and it left the menu when it went.

The Shift tool has to be both. Ines wants to start it from the menu, and in step 4 a second script will need to borrow it. One file can't live in two folders. Two files can.

## Step 2: The tool becomes a module

Move `shift_tool.py` out of the Scripts folder and into the module folder, beside `halfmoon.py`. Then change its last line. It was this:

```python
scripting.show_script_dialog(build, KEY)
```

Make it this:

```python
def open_tool():
    scripting.show_script_dialog(build, KEY)


if __name__ == "__main__":
    open_tool()
```

The window-opening line now has a name, `open_tool`, so that other files can ask for it. The last two lines are chapter 114's guard: they open the window when you run the file from the Scripting panel, and do nothing when another file imports it. You can still work on the tool the way you have all month.

The first line of the file was `#FLM: Shift Tool`. A module isn't in the menu, so that line now says nothing to anybody. Change it to a plain comment, such as `# shift_tool.py: the Shift tool, as a module other scripts import.`

## Step 3: A launcher with a good name

In the Scripts folder you have a folder named `Halfmoon`, from chapter 18. Make a new file in it, `Shift Sidebearings.py`:

```python
#FLM: Shift Sidebearings
import shift_tool

shift_tool.open_tool()
```

That's the whole file. It's called a launcher: it owns nothing and decides nothing. It finds the tool and starts it. Choose **Scripts > Refresh Scripts**, and the menu has **Scripts > Halfmoon > Shift Sidebearings**. Ines's four steps are two clicks.

The launcher is three lines for a reason. When you mend the tool, you mend `shift_tool.py`, in one place, and the menu line never needs touching. The name in the menu and the code that does the work can now change without each other.

That leaves the naming, which is most of what makes a menu pleasant. Three rules have served the studio:

- **Name the job, not the code.** `Shift Sidebearings` says what will happen to the font. `shift_tool` says what the file is. The first belongs in the menu and the second in the module folder.
- **Start with the verb.** `Shift Sidebearings`, `Copy Sidebearings`, `Open Up Bold`. A menu is a list of things to do, and a verb first lets the eye run down it.
- **One folder for one studio.** Everything Halfmoon wrote goes in `Halfmoon`. If that grows past a dozen lines, sort by what the tools work on, with the folder names in title case: `Halfmoon Spacing`, `Halfmoon Checks`. Keep it one folder deep. I've seen FontLab's own script collections go one level down and no further, and I haven't seen what the menu does with a folder inside a folder.

## Step 4: A key for the tool

Now the hard part. Ines wants a key: one press, and the window is there.

Here is what I can tell you honestly. I searched Fly, the helpers under it and FontLab's scripting names for a way to give a line in the **Scripts** menu a keyboard shortcut from a script, and found none. FontLab has its own place for shortcuts in its settings, and whether Scripts-menu lines appear there is something to look for in your copy; I haven't seen it.

What a script can do is add a menu of its own, and that menu's lines can have keys. Fly has a helper for it, `OwnedMenus`. "Owned" means the helper remembers every line it added, so that it can take them all away again:

```python
from fly import fl, qt
from fly.ap.qt.menus import OwnedMenus


def report(error, owner):
    print(f"Halfmoon menu: {type(error).__name__}: {error}")


menus = OwnedMenus(qt, fl, error_sink=report, owned_title="Halfmoon")
```

`OwnedMenus` is Fly's own Python, so keyword arguments are fine here; the no-keywords rule from chapter 121 is for Qt's widgets. `error_sink` is a function you hand over, as you handed slots to buttons in chapter 122. When a menu line's work raises an error, Fly calls `report` with it, and the error goes to the Output panel. `owned_title` is the name of the new menu in FontLab's menu bar.

A line goes in with `add_action`, which wants the menu's name, the line's text, and the function to call:

```python
token = menus.add_action("Halfmoon", "Shift Sidebearings", shift_tool.open_tool)
```

Here is the mistake that's waiting. It's the one from chapter 122, in new clothes. Write `shift_tool.open_tool()` with brackets and Python calls the function there and then: the Shift window opens while the menu is being built, and what the menu line receives is `None`, the nothing that `open_tool` returns. In the stand-in, choosing the line then prints this:

```text
Halfmoon menu: TypeError: 'NoneType' object is not callable
```

No brackets. You're handing over the function, to be called later.

`add_action` gives back a number, a token, that stands for the new line. Ask for the line by its token and give it a key:

```python
menus.action(token).setShortcut(qt.QtGui.QKeySequence("Ctrl+Alt+Shift+S"))
```

The key is written as text, with the modifier keys spelled out and joined by `+`. On a Mac, Qt reads `Ctrl` as the Command key. Three modifiers is a mouthful, and that's deliberate: FontLab already uses most of the short combinations, and a script that takes one of them over has made an enemy.

One thing remains. `menus` is an object, and chapter 126 showed what happens to an object nobody holds: Python throws it away, and its menu lines go dead. `halfmoon.keep` from chapter 127 holds it. And `keep` closes whatever it held before under the same key, which here means that running the script twice gives you one Halfmoon menu, with the old one taken out first.

## The whole script

```python
#FLM: Halfmoon Menu
# Adds a Halfmoon menu to FontLab's menu bar, with a shortcut
# for the Shift tool. The menu lasts until FontLab closes.
import halfmoon
import shift_tool
from fly import fl, qt
from fly.ap.qt.menus import OwnedMenus

KEY = "halfmoon.menu"
MENU = "Halfmoon"
SHORTCUT = "Ctrl+Alt+Shift+S"


def report(error, owner):
    print(f"Halfmoon menu: {type(error).__name__}: {error}")


def main():
    menus = OwnedMenus(qt, fl, error_sink=report, owned_title=MENU)
    halfmoon.keep(KEY, [menus])
    token = menus.add_action(MENU, "Shift Sidebearings", shift_tool.open_tool)
    menus.action(token).setShortcut(qt.QtGui.QKeySequence(SHORTCUT))
    print(f"{MENU} menu added. {SHORTCUT} opens the Shift tool.")


main()
```

Save it as `Halfmoon Menu.py` in `Scripts/Halfmoon`. Notice the order inside `main`. `keep` comes straight after the menus object is made and before any line is added, so the old menu is gone before the new one is filled. Do it the other way round and, for a moment, two menus named Halfmoon exist, and `add_action` may put the new line in the old one.

## Run it

Refresh the menu and choose **Scripts > Halfmoon > Halfmoon Menu**. The Output panel says:

```text
Halfmoon menu added. Ctrl+Alt+Shift+S opens the Shift tool.
```

In the stand-in, the menu bar gained one menu, Halfmoon, with one line, and pressing the key opened one Shift window. Running the script a second time closed the first menu and left one.

The menu lasts until FontLab closes. Tomorrow it's gone, and Ines chooses **Halfmoon Menu** once to get it back. That's one click a day for a key that works all day, and she has agreed to it, with a look. FontLab can run a script of yours every time it starts, and that would spare her the click. I haven't seen it work for a script like this one, so the book leaves it there and Ines keeps her click.

## Break it on purpose

**Forget the guard.** In `shift_tool.py`, replace the last two lines with a bare `open_tool()`. Restart FontLab, so that Python reads the module afresh, and choose **Halfmoon Menu**. A Shift window opens, though nobody asked for one: the `import shift_tool` line at the top of the menu script ran the whole file, and the whole file now ends by opening a window. An import should give you names and do nothing else. Put the guard back.

**Leave the tool in the wrong folder.** Move `shift_tool.py` back into the Scripts folder and restart FontLab. Choose **Shift Sidebearings**:

```text
ModuleNotFoundError: No module named 'shift_tool'
```

The launcher asked Python for a module, and Python looked only where it looks. The file is in plain sight in the menu's folder and invisible to `import`. Move it back.

Both breaks needed a restart, and so will every change you make to `shift_tool.py` from now on, because Python reads a module once. While you're working on it, run the file itself from the Scripting panel, which the guard allows, or use `importlib.reload` from chapter 33.

## What you learned

The Scripts folder is for files you start, and the module folder is for files other scripts borrow from, so a tool that needs both becomes a module plus a three-line launcher. A menu name says the job, starts with a verb, and lives in one folder per studio. A script can't give a Scripts-menu line a key by any route I could find, but it can add its own menu with `OwnedMenus`, and those lines take keys. Whatever adds things to FontLab's menu bar must be kept, and must clear away the old before adding the new.

## Try it yourself

1. Give the Suffix Picker from chapter 125 the same treatment: a module with an `open_tool` function and a guard, a launcher named for the job, and a second line in the Halfmoon menu with its own key.
2. The live panel from chapter 128 has a `main` function and no window key. Decide what its `open_tool` should be, and add it to the menu without a shortcut. What does the menu script have to import?
3. Add a third line to the Halfmoon menu, `Remove This Menu`, whose function closes the menu. You'll need a small function of your own that calls `menus.close()`, and you'll need to think about where `menus` has to be for that function to see it.

## Next

The studio's tools now sit in two folders on one computer, put there by hand, file by file. Then Oskar's cousin rings from her studio in Porto: could she have them too? Chapter 133 packs the Halfmoon tools so that one file puts everything where it belongs, on any computer.
