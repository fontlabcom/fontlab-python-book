---
this_file: src_docs/md/part1-first-words/004-pack-the-toolbag.md
---

# 4. Pack the toolbag

Wednesday. Mira finds a folder on the studio server called `chores`. Inside are Oskar's scripts, dozens of them, with names like `width_report.py` and `mark_empty.py`.

She opens the first one in the Scripting panel. The top line reads:

```python
from fly import fl
```

She clicks the triangle. An error. This time she reads it from the bottom, the way she learned yesterday.

```text
ModuleNotFoundError: No module named 'fly'
```

She messages Oskar: *What is fly and why don't I have it?*

The answer comes an hour later. *My fault. Fly is the toolbag. Every script I wrote reaches into it. It was on my machine, not yours. Install it once and forget about it.*

Today you install things. No glyph gets counted until the last five minutes. But every chapter after this one starts with the line that failed on Mira's screen, so this is the day that makes the rest possible. Put the kettle on.

## What you need

- FontLab 9, and `Plum-practice` from [chapter 1](001-the-list-oskar-left.md).
- An internet connection.
- About twenty minutes.

## Why a toolbag at all

In chapter 2 you used `print`. Nobody installed it. `print` is part of Python, in the same way that the letter *a* is part of every text font.

FontLab adds its own words to Python: words for fonts, glyphs, contours, kerning. They are built into the app too. But they were made for the programmers who build FontLab, and they show it. Asking for a simple thing in those words can take five lines and some knowledge of how FontLab is put together inside.

So over the years, people who script FontLab have written friendlier words on top. One line where there were five. Sensible names. Protection against the usual accidents. These friendly words live in **packages**. A package is a folder of Python files that somebody else wrote, tested, and gave a name, so that your script can borrow from it.

There are several of these packages, written by different people for different jobs. That could mean learning ten names and remembering which word lives where. **Fly** solves that. Fly is one small package that holds the door to all the others. You ask Fly, and Fly fetches.

Here is what is in the bag. You don't need to remember any of it today.

| You write | You get | Good for |
|---|---|---|
| `fl` | FontLab's own words | fonts, glyphs, layers, the app itself |
| `fg` | FontLab's font storage | names, Unicode values, kerning, font info |
| `ap` | the FontLab app helpers | everyday chores done safely, with Undo |
| `tr` | TypeRig | work on outlines and nodes |
| `qt` | the window-building kit | dialogs, buttons, panels |
| `qs` | a second window-building kit | the same, with different spelling |
| `pr` | the command bridge | driving FontLab's own commands |
| `gp` | a Glyphs-style dialect | running scripts written for Glyphs |
| `fp` | a UFO-style dialect | running scripts written for RoboFont and friends |
| `pens` | the drawing pens | drawing outlines from numbers |

For most of this book you will use three or four of them. The others wait in the bag until a chore needs them.

## Step 1: Install uv

Some of the packages need helpers from the internet, and FontLab has no way to fetch them by itself. A small free program called **uv** does the fetching. You install it once, and after that you never start it yourself. The installer finds it.

On a Mac, open the **Terminal** app. You will find it in **Applications > Utilities**, or press ++cmd+space++ and type `Terminal`.

A window opens with a line of text ending in `%` or `$`. That is the **prompt**. It is the same idea as the Scripting panel, with one difference: here you are talking to macOS, not to FontLab. Paste this line and press ++return++:

```text
curl -LsSf https://astral.sh/uv/install.sh | sh
```

That line downloads the uv installer from the people who make uv and runs it. A few lines scroll by. When the prompt comes back, check that it worked:

```text
uv --version
```

You should get an answer that starts with `uv` and a version number. If Terminal says `command not found`, close the Terminal window, open a new one, and ask again. A new window picks up what the installer changed.

On Windows, the uv website at `https://docs.astral.sh/uv/` gives the matching line for PowerShell.

You can close Terminal now. That was the only time this chapter needs it.

## Step 2: Put the packages side by side

Make a new folder somewhere you won't delete it by accident. Your home folder is a good place. Call it `fontlab-scripting`.

Into that folder you will put eight packages, each in its own folder. Seven come from the `fontlabcom` account on GitHub. TypeRig comes from its author's account, `kateliev`.

| Folder | What it is |
|---|---|
| `fontlab-fly` | Fly, the door to the rest |
| `fontlab-echopy` | lets Fly reach `fl`, `fg` and `pr` |
| `fontlab-fontlabapp` | the app helpers, `ap` |
| `fontlab-python-pens` | drawing tools that the app helpers use |
| `TypeRig` | `tr` |
| `pythonqtside` | `qs` |
| `fontlab-glyport` | `gp` |
| `fontlab-fontport` | `fp` |

For each one, open its page on GitHub, click the green **Code** button, and choose **Download ZIP**. Unzip it and drag the folder into `fontlab-scripting`. GitHub adds `-main` to the folder name. You can leave that or remove it. The installer doesn't go by folder names.

What matters is that the eight folders are neighbors, all directly inside `fontlab-scripting`, like this:

```text
fontlab-scripting/
    fontlab-echopy/
    fontlab-fly/
    fontlab-fontlabapp/
    fontlab-fontport/
    fontlab-glyport/
    fontlab-python-pens/
    pythonqtside/
    TypeRig/
```

Here is why. When you install Fly in the next step, it looks at the folders next to its own and installs every neighbor it needs. One step, eight packages. If a folder is nested one level too deep, or sitting on your desktop, Fly won't see it.

If you know Git, clone the eight repositories into the folder. The result is the same, and updating later takes one command per folder.

## Step 3: Run the installer

Open the `fontlab-fly` folder. Near the top is a file called `install.vfpy`.

A `.vfpy` file is a Python script that belongs to FontLab. It is a plain text file like `hello.py`, but macOS knows to hand it to FontLab when you open it.

Make sure FontLab is running and the **Output** panel is visible. Then double-click `install.vfpy`, or drag it onto the FontLab window.

The script starts at once. Watch the Output panel. Lines appear, one group for each package, as Fly works through its neighbors:

```text
Installing dependency fontlab-echopy>=0.1.0 from /Users/mira/fontlab-scripting/fontlab-echopy
```

A **dependency** is a package that another package needs. You will see that word a lot in the next minute. FontLab may stop responding while this runs. Leave it alone. A script and the FontLab window take turns, and while a script is busy, FontLab can't redraw itself or answer your clicks.

When everything is done, the last lines look like this:

```text
Installed fontlab-fly 0.1.0 as com.fontlab.fly (copied); log: /Users/mira/Library/Application Support/FontLab/FontLab 9/Extensions/com.fontlab.fly/install.log
Scripts > Extensions lists and uninstalls extensions. Use Refresh Scripts if needed.
Restart FontLab to load it.
```

Your version number and folder names will differ. The line to look for is the last one.

If you see `Install FAILED` in its place, the same line tells you where the log file is. The most common cause is a missing neighbor: the Output panel then names the package it could not find. Put that folder where it belongs and double-click `install.vfpy` again. Running the installer twice does no harm.

If you see `uv not found`, go back to step 1.

## Step 4: Restart FontLab

Do what the last line says. Quit FontLab and start it again.

FontLab reads its list of packages once, when it starts. Until you restart, it doesn't know that anything new arrived.

Open `Plum-practice` again, and bring back the **Scripting** and **Output** panels if they aren't showing.

## Step 5: Reach into the bag

Now type the line that failed for Mira this morning.

```python
from fly import fl
```

Run it.

Nothing happens. The Output panel stays empty.

That's the result you want. In Python, no news is good news. The line asked for something, got it, and had nothing to report.

Read the line as an English sentence: *from Fly, import fl.* **Import** means "bring this in so that I can use it." Before this line runs, your script knows Python and nothing else. After it, your script also knows `fl`, and `fl` knows FontLab.

You will type some version of this line at the top of every script from now on. If a chore needs the app helpers too, you ask for both, with a comma:

```python
from fly import fl, ap
```

Now make the mistake Mira would make.

```python
from fly import fontlab
```

```text
ImportError: cannot import name 'fontlab' from 'fly'
```

There may be a folder path at the end of your message. A new kind of error for the list on the wall, and it reads plainly: Fly has no tool by that name. The tools have the short names from the table near the top of this chapter. Fix the line and run it again.

## The first question

You have earned something for all that installing. Put this in the Scripting panel, with `Plum-practice` open:

```python
from fly import fl

font = fl.CurrentFont()
print("This font has", len(font), "glyphs")
```

Run it.

```text
This font has 205 glyphs
```

In chapter 2 you typed that 205 yourself. This time you didn't. FontLab looked at the font in front of you and counted.

Open a different font and run the same four lines. The number changes. You didn't change the script. That's the moment where a script stops being a typing exercise and starts being a tool: the same words, pointed at a different font, give a different and correct answer.

I have used two things here without explaining them: the `font =` line, and the dots. The next two chapters are about them. For today, read the script like this. Line 1 opens the bag. Line 3 asks FontLab for the font you are working on. Line 4 counts its glyphs and prints the count.

Save the script as `count.py` in your `scripting-book` folder.

Mira runs it, reads the number, and crosses out the first line on Oskar's sheet: *Count the glyphs and tell Ines.*

"Two hundred and five," she calls across the room.

"I know," says Ines. "But now you know how you know."

??? info "Going deeper: where it all went"
    The installer put everything inside FontLab's own data folder. On a Mac that is `~/Library/Application Support/FontLab/FontLab 9`. The packages are in `python/3.11/site-packages` there. Each package also gets a folder under `Extensions` with a file called `install.log`, which records every file the installer created.

    FontLab now has a new menu, **Scripts > Extensions**, with **List Extensions** and one **Uninstall** item for each package. Uninstalling removes what the installer created and nothing else.

    If you cloned the repositories with Git, the installer links to your folders and does not copy them. Move or delete `fontlab-scripting` and the packages stop working, so keep the folder where it is.

## What you learned

You can now install a FontLab package: open its `install.vfpy` in FontLab, then restart. Fly is the one package your scripts ask, and `from fly import fl` is how they ask. You also know two new errors apart: `ModuleNotFoundError` means the package isn't installed, and `ImportError` means the package is there but the name you asked for isn't.

## Try it yourself

1. Choose **Scripts > Extensions > List Extensions** and read the Output panel. Look for a line that mentions Fly. I haven't seen this list myself, so I can't tell you how many lines to expect.
2. Run `from fly import fl, ap, tr` as a one-line script. Then change `tr` to `tR` and run it again. Which error do you get, and which rule from chapter 3 did you break?
3. Open another font you have, any font, and run `count.py`. Write the number down. Then check it against what the Font window says. If the two numbers differ, look at how the Font window is filtered before you blame the script.

## Next

Chapter 5 takes the four lines of `count.py` apart and shows you what a font looks like from Python's side: a list of glyphs.
