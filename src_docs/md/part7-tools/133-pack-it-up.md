---
this_file: src_docs/md/part7-tools/133-pack-it-up.md
---

# 133. Pack it up

Thursday, 31 December. The studio shuts at one. At ten Oskar's cousin Rita rings again from Porto: she has FontLab 9, she has two people who space type all day, and she would like the Shift tool and the Suffix Picker before the year is out. Ines starts writing her an email. It has eleven steps by the time she stops: find this folder, make that folder, copy these two files here and those two there, mind the capital letters.

Eleven steps is eleven places to go wrong, and Rita will go wrong at step three, as anyone would. Today you put the tools in one folder, laid out so that one file in it can do all eleven steps. Then you write a short script that checks the folder before it leaves the building.

## What you need

`shift_tool.py` and the two launchers from chapter 132, and `suffix_picker.py` with its launcher, from chapter 132's first exercise. If you skipped that exercise, leave those two files out, and your output will have no Suffix Picker lines. You also need a copy of `install.vfpy`. It comes with Fly: it's in the folder you downloaded in chapter 4, next to Fly's own `pyproject.toml`.

I haven't run this chapter in FontLab 9. The checking script is plain Python and I ran it as printed, on a folder built the way this chapter describes. I also loaded the real `install.vfpy` in plain Python and asked its own checks about the same folder; they agreed with the script every time. What the installer does once it starts copying, I've read in its source and haven't watched.

## Step 1: What the installer wants

`install.vfpy` is one file, the same file in every FontLab tool that uses it. You don't edit it. You put a copy in your folder, and it reads what to do from a second file beside it, `pyproject.toml`.

Open it in FontLab 9 (double-click it, or drop it on FontLab's window) and it does this, all inside FontLab's own data folder:

- It puts each **package** you list where Python looks for modules, the `site-packages` folder from chapter 33.
- It copies everything in your folder's `Scripts` folder into FontLab's Scripts folder, keeping the folders, so `Scripts/Halfmoon/Shift Sidebearings.py` lands in the **Halfmoon** submenu.
- It writes a log of every file it made, and adds two lines to **Scripts > Extensions**: one that lists what's installed and one that uninstalls yours.

Then it asks for a restart. So the folder you send needs four things in it:

```text
spacing-tools/
    install.vfpy
    pyproject.toml
    spacing_tools/
        __init__.py
        shift_tool.py
        suffix_picker.py
    Scripts/
        Halfmoon/
            Shift Sidebearings.py
            Suffix Picker.py
```

Two of those are new to you: the folder called `spacing_tools` with a file called `__init__.py`, and `pyproject.toml`. The names say what's inside: tools for spacing. The folder you send has a hyphen in its name, like a file name; the package inside has an underscore, because the package's name is what a script writes after `import`, and Python reads a hyphen there as a minus sign.

## Step 2: A module that is a folder

The installer doesn't place loose `.py` files where Python looks. It places packages. A **package** is a folder that Python treats as a module, and what makes a folder a package is one file inside it with a fixed name: `__init__.py`, with two underscores each side.

When a script says `import spacing_tools`, Python searches its folders for `spacing_tools.py` or for a folder `spacing_tools` that holds an `__init__.py`. If it finds the folder, it runs `__init__.py`, and what that file defines is what `spacing_tools.` followed by a name reaches. Your tools don't need anything defined there. Each of them carries its own helpers, so the file only has to exist. One line saying what the package is will do. Here is all of `__init__.py`:

```python
"""Halfmoon Type's spacing tools: the Shift tool and the Suffix Picker."""
```

A string on a line of its own at the top of a file is a **docstring**. Python keeps it as the module's description and does nothing else with it. So the move is small:

1. Make a folder `spacing_tools` inside `spacing-tools`.
2. Save that one line in it as `__init__.py`.
3. Copy `shift_tool.py` and `suffix_picker.py` in beside it.

The two modules now live inside the package, and a module inside a package is reached through it:

```python
#FLM: Shift Sidebearings
from spacing_tools import shift_tool

shift_tool.open_tool()
```

That's the launcher from chapter 132 with one line changed: `import shift_tool` has become `from spacing_tools import shift_tool`. The Suffix Picker's launcher changes the same way:

```python
#FLM: Suffix Picker
from spacing_tools import suffix_picker

suffix_picker.open_tool()
```

Nothing inside `shift_tool.py` or `suffix_picker.py` changes. Save both launchers into `spacing-tools/Scripts/Halfmoon`.

One thing to do on your own machine first. Your loose `shift_tool.py` and `suffix_picker.py` are still in `site-packages`, and a loose `shift_tool.py` left in that folder is what `import shift_tool` finds, so an old launcher would go on running the old one. Move them somewhere safe before you try the installer yourself. Rita's machine has neither, so she has nothing to move.

## Step 3: The file that says what's what

`pyproject.toml` is a settings file that Python tools agree to read. The format is called TOML. It looks like the JSON of chapter 129 with the brackets taken off: names in square brackets start a table, and under each one come lines of `name = value`.

```text
[project]
name = "spacing-tools"

[tool.fontlab-install]
id = "com.example.spacing-tools"
packages = ["spacing_tools"]
```

`[project]` holds the name the tools go by. `[tool.fontlab-install]` is the installer's own table. Its `id` is how FontLab's data folder will tell your tools from everyone else's, so it has to be yours alone, and the custom is to write it backwards from the general to the particular, with dots: kind of outfit, its name, the thing. `com.example` is the stand-in this book uses; put your own studio's web address there, backwards. Small letters, digits and hyphens only. `packages` lists the package folders. There's no line for the Scripts folder, because the installer looks for a folder called `Scripts`, with that capital, by itself.

Python can read TOML with a module that comes with it:

```python
import tomllib

text = """
[project]
name = "spacing-tools"

[tool.fontlab-install]
id = "com.example.spacing-tools"
packages = ["spacing_tools"]
"""
project = tomllib.loads(text)
print(project["tool"]["fontlab-install"]["packages"])
```

```text
['spacing_tools']
```

`tomllib.loads` takes text and gives a dictionary, as `json.load` gave you one from a file. A table is a dictionary, and the dot in `[tool.fontlab-install]` makes one inside another, so you go down through three keys to reach the list.

## Step 4: The mistake that looks like a tidy-up

Here's the one I'd have made. The folder `spacing_tools` holds three files, and one of them has an odd name, holds one line that does nothing and looks like clutter. Delete `__init__.py`, and send the folder.

On Rita's machine the installer stops with this:

```text
RuntimeError: pyproject.toml must list the wheel packages, each with __init__.py.
```

That's the installer's real sentence, and it's a fair one once you know what it means, but it names a file that Rita never heard of and a word, "wheel", that this book hasn't used. She would write back "it doesn't work", and you'd be guessing from another country. The fix isn't to explain the sentence to her. It's to catch the fault yourself, in words you chose, before the folder goes.

## The whole script

```python
#FLM: Check Package
# Reads a folder of tools and says whether install.vfpy has what it
# needs. Changes nothing.
import tomllib
from pathlib import Path

FOLDER = Path.home() / "spacing-tools"


def id_problem(text):
    parts = text.split(".")
    if len(parts) < 2 or "" in parts:
        return f"id is {repr(text)}. It needs two or more words joined by dots."
    if text != text.lower() or " " in text or "_" in text:
        return f"id is {repr(text)}. Use small letters, digits and hyphens only."
    return ""


def launchers(folder):
    found = []
    scripts = folder / "Scripts"
    if not scripts.is_dir():
        return found
    for category in sorted(scripts.iterdir()):
        if not category.is_dir():
            continue
        for path in sorted(category.iterdir()):
            if path.suffix == ".py":
                found.append(path)
    return found


def check(folder):
    problems = []
    for name in ["pyproject.toml", "install.vfpy"]:
        if not (folder / name).is_file():
            problems.append(f"{name} is missing.")
    if problems:
        return [], problems

    project = tomllib.loads((folder / "pyproject.toml").read_text())
    if "name" not in project.get("project", {}):
        problems.append("[project] needs a name.")
    table = project.get("tool", {}).get("fontlab-install", {})
    trouble = id_problem(table.get("id", ""))
    if trouble:
        problems.append(trouble)

    lines = []
    for name in table.get("packages", []):
        if (folder / name / "__init__.py").is_file():
            lines.append(f"package   {name}")
        else:
            problems.append(f"{name}/__init__.py is missing, so {name} isn't a package.")
    for path in launchers(folder):
        first = path.read_text().splitlines()[:1]
        if first and first[0].startswith("#FLM:"):
            lines.append(f"menu      {path.parent.name} > {first[0][5:].strip()}")
        else:
            problems.append(f"{path.name} has no #FLM line at the top.")
    return lines, problems


def main():
    lines, problems = check(FOLDER)
    print(FOLDER.name)
    for line in lines:
        print(f"  {line}")
    for problem in problems:
        print(f"  PROBLEM   {problem}")
    if problems:
        print(f"{len(problems)} to fix before you send it.")
    else:
        print("Ready to send.")


main()
```

Save it as `check_package.py`, and set `FOLDER` to where your `spacing-tools` is.

`check` asks the cheap questions first, as chapter 131's tool did: if either of the two files is missing there's nothing to read, so it says so and stops. `read_text()` is new: it opens the file, reads it all and closes it, the three lines of chapter 27 in one. `is_dir()` is the sibling of chapter 111's `is_file()`, true for a folder. The two `.get` calls with `{}` walk down the tables without tripping when one is absent, which is chapter 22's trick used twice in a row.

`id_problem` gives back a sentence, or an empty string for "no problem". It tests what the installer tests, more loosely: two or more parts between dots, none of them empty, nothing but small letters, digits and hyphens. The installer's own test is stricter in ways that rarely bite, such as refusing an id that starts with a digit.

`launchers` walks the Scripts folder two levels down, a loop inside a loop, because that's how deep the menu goes: categories, then scripts. For each launcher, `check` reads the first line and looks for `#FLM:`. `splitlines()[:1]` gives a list holding the first line, or an empty list for an empty file, so the test can't trip over a file with nothing in it. `path.parent` is the folder a path sits in, and `.name` of that is the category.

## Run it

```text
spacing-tools
  package   spacing_tools
  menu      Halfmoon > Shift Sidebearings
  menu      Halfmoon > Suffix Picker
Ready to send.
```

Three lines say what Rita will get: one module to import and two lines in her menu. Read them as she would. If a tool you meant to send isn't in the list, it isn't in the folder.

Now zip the folder and send it, with a note of three lines, not eleven:

```text
1. Install Fly first, from its own folder, the same way.
2. Unzip spacing-tools and double-click install.vfpy.
3. Restart FontLab. The tools are in Scripts > Halfmoon.
```

Line one matters. Your tools import `fly`, and the installer can fetch what a package depends on from the public package index, where Fly isn't. So Fly goes in first, by hand, with its own `install.vfpy`.

There's a difference between your copy and hers that's worth knowing. For a folder that's a plain unzipped copy, the installer copies the package into FontLab's data folder, and Rita's tools stay as they were on the day you sent them. To change them you send a new folder and she opens the new `install.vfpy`, which replaces the launchers at the same paths. The installer will call your tools version 0.0.0, because it reads version numbers from a place this book doesn't go. Put a date in the zip's name instead.

## Break it on purpose

Make the tidy-up from step 4: delete `spacing_tools/__init__.py`, and run the check.

```text
spacing-tools
  menu      Halfmoon > Shift Sidebearings
  menu      Halfmoon > Suffix Picker
  PROBLEM   spacing_tools/__init__.py is missing, so spacing_tools isn't a package.
1 to fix before you send it.
```

The same fault, caught on your side, in a sentence that says which file and why. Put it back.

Then change the `id` line to `id = "Spacing Tools"`:

```text
  PROBLEM   id is 'Spacing Tools'. It needs two or more words joined by dots.
```

The installer refuses that id too, with `pyproject.toml needs [tool.fontlab-install] id = "com.example.name".` Put it right. Last, delete the closing bracket of the `packages` line:

```text
TOMLDecodeError: Unclosed array (at end of document)
```

That one isn't caught, and the script stops with Python's own error. It's readable enough for you, and you're the only one who runs this script, so I've left it. The rule from chapter 131 was about messages for people who didn't write the tool.

## What you learned

A package is a folder with an `__init__.py` in it, and Python imports it by the folder's name. `install.vfpy` reads `pyproject.toml` beside it, places the packages where Python looks, copies the `Scripts` folder into FontLab's menu, and keeps a log so that it can take everything out again. TOML is tables of `name = value`, and `tomllib.loads` turns it into dictionaries. Before you send tools to someone who can't ask you questions, run the checks that their machine would run, and word the answers yourself.

## Try it yourself

1. Add `live_panel.py` from chapter 128 to the package and give it a launcher. The check should show three menu lines.
2. Make `check` complain when a launcher imports a module that isn't in the package. Reading the launcher's second line and looking for the word after `import` is enough for launchers shaped like yours.
3. Add a file `README.txt` to the folder with the three-line note in it, and make `check` report a problem when it's missing. Rita's colleagues will open the folder without the email.

## Next

Rita's reply comes at ten to one: both tools are in her menu. Mira, back on Monday, has left a request of her own on the board: she wants to see the sidebearing numbers in the Glyph window itself, beside the glyph, without a panel at all. Chapter 134 writes a function that FontLab calls each time it draws a glyph.
