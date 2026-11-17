---
this_file: src_docs/md/part7-tools/133-pack-it-up.md
---

# 133. Pack it up

Thursday, 31 December. The studio shuts at one. At ten Oskar's cousin Rita rings again from Porto: she has FontLab 9, she has two people who space type all day, and she would like the Shift tool and the Suffix Picker before the year is out. Ines starts writing her an email. It has eleven steps by the time she stops: find this folder, make that folder, copy these two files here and those two there, mind the capital letters.

Eleven steps is eleven places to go wrong, and Rita will go wrong at step three, as anyone would. Today you put the tools in one folder, laid out so that one file in it can do all eleven steps. Then you write a short script that checks the folder before it leaves the building.

## What you need

`shift_tool.py` and the two launchers from chapter 132, and `suffix_picker.py` with its launcher, from chapter 132's first exercise. If you skipped that exercise, leave those two files out, and your output will have no Suffix Picker lines. You also need Instamix 1.0.9 or newer, installed as in chapter 4. It will generate the current `install.vfpy` for this folder.

I haven't run this chapter in FontLab 9. The checking script is plain Python and I ran it as printed, on a folder built the way this chapter describes. The check below reads the project with Instamix's parser, without installing it. These checks do not establish that the windows and menus work in FontLab.

## Step 1: What the installer wants

`install.vfpy` is a generated entry point. You don't edit it. Instamix writes the current shared bootstrap into your folder; it reads what to do from a second file beside it, `pyproject.toml`. Older copies can have different bootstrap checks, so generate a new one for a new delivery.

Open it in FontLab 9 (double-click it, or drop it on FontLab's window) and it does this, all inside FontLab's own data folder:

- It puts each **package** you list where Python looks for modules, the `site-packages` folder from chapter 33.
- It copies everything in your folder's `Scripts` folder into FontLab's Scripts folder, keeping the folders, so `Scripts/Halfmoon/Shift Sidebearings.py` lands in the **Halfmoon** submenu.
- It records the deployed files in its ownership ledger and adds list and uninstall commands under **Scripts > Instamix**. The extension payload stays under `Extensions/Library`; scripts run from their normal deployed locations.

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
version = "1.0.0"
dependencies = ["fontlab-fly>=1.3.0"]

[tool.fontlab-install]
id = "com.example.spacing-tools"
packages = ["spacing_tools"]
```

`[project]` holds the distribution name, this delivery's version and the distribution requirements. Here the tools need Fly 1.3.0 or later. `[tool.fontlab-install]` is the installer's own table. Its `id` is how FontLab's data folder will tell your tools from everyone else's, so it has to be yours alone, and the custom is to write it backwards from the general to the particular, with dots: kind of outfit, its name, the thing. `com.example` is the stand-in this book uses; put your own studio's web address there, backwards. Small letters, digits and hyphens only. `packages` lists the package folders. There's no line for the Scripts folder, because the installer looks for a folder called `Scripts`, with that capital, by itself.

Python can read TOML with a module that comes with it:

```python
import tomllib

text = """
[project]
name = "spacing-tools"
version = "1.0.0"
dependencies = ["fontlab-fly>=1.3.0"]

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

Now generate the installer from a terminal where Instamix is available:

```sh
uvx --from "fontlab-python-instamix>=1.0.9" fontlab-instamix stub spacing-tools
```

Run that command from the folder containing `spacing-tools`. It writes `spacing-tools/install.vfpy`. If a previous installer is there, inspect it first; add `--force` only when you intend to replace that file. The generated bootstrap checks the provider's migration and rollback capabilities before deploying the project.

## Step 4: The mistake that looks like a tidy-up

Here's the one I'd have made. The folder `spacing_tools` holds three files, and one of them has an odd name, holds one line that does nothing and looks like clutter. Delete `__init__.py`, and send the folder.

Your launchers import a package you no longer sent. Rita would write back "it doesn't work", and you'd be guessing from another country. Catch that missing file before sending anything, in a sentence that says which file and why. The check below reads Instamix's actual project contract, then checks the package and menu files you intend to deliver.

## The whole script

```python
#FLM: Check Package
# Reads a folder of tools and says whether install.vfpy has what it
# needs. Changes nothing.
from pathlib import Path

from fontlab_instamix.bootstrap import BootstrapError, read_project

FOLDER = Path.home() / "spacing-tools"


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

    try:
        project = read_project(folder)
    except BootstrapError as error:
        return [], [str(error)]

    lines = []
    for name in project.packages:
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

`check` asks the cheap questions first, as chapter 131's tool did: if either of the two files is missing there's nothing to read, so it says so and stops. `read_text()` is new: it opens the file, reads it all and closes it, the three lines of chapter 27 in one. `is_dir()` is the sibling of chapter 111's `is_file()`, true for a folder. `read_project` reads the same metadata the installer will use. It returns facts about the package without deploying any files. A malformed TOML file still raises Python's `TOMLDecodeError`.

`BootstrapError` describes a missing or unusable installer table, including an invalid reverse-domain id. The check reports that message instead of maintaining its own, slightly different rule for ids.

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

Line one makes the dependency explicit for Rita. The metadata also declares `fontlab-fly>=1.3.0`. Instamix can use a compatible sibling checkout or ask uv to resolve a distribution requirement; it refuses an incompatible source instead of silently changing it. Check the release instructions for any version not yet available from PyPI.

For a plain unzipped source folder, Instamix copies the package into FontLab's data folder. Rita's tools stay at the version you sent. A Git checkout can be installed editably, so its folder must stay in place. This example declares version `1.0.0`; increase it for the next delivery. Other projects can derive a version from their build metadata or Git history. There is no universal `0.0.0` rule.

### A source project or a ready extension?

This chapter sends a source project with `pyproject.toml`. Instamix also installs ready **extensions**: a reverse-domain folder such as `com.example.spacing-tools.fontlabext`, with `manifest.fontlabextj` at its root. A `.fontlabextz` is a ZIP containing one or more whole `.fontlabext` folders, including their folder names. Its download filename does not define their identities; each manifest id must match its enclosing folder.

For a single script, Instamix can build that second form without running the script:

```sh
fontlab-instamix wrap width_report.py --out dist --id com.example.width-report --name "Width Report" --version 1.0.0 --zip
```

That creates a manifest and a script deployment rule. It does not package the imported `spacing_tools` module automatically: send this chapter's complete source project when its launchers need that package. For several ready extensions, `fontlab-instamix pack` puts their whole folders into one `.fontlabextz`. Inside FontLab, `fontlab_instamix.gui.install_selected()` can select archives or manifests; `folder=True` selects an extension folder.

An upgrade can refuse an owner-edited or unowned conflicting path. Keep the files it names; do not delete them merely to make the installer green. Instamix 1.0.9 restores the project's earlier deployed files and receipts on failure. Separately installed dependencies can remain. If restoration fails, keep the recovery directory named in the error. A timeout is an unknown outcome, so inspect the installation before retrying.

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
  PROBLEM   [tool.fontlab-install] id must be a reverse-DNS id like com.example.tool
```

This is the installer's own metadata error, caught by the check before deployment. Put it right. Last, delete the closing bracket of the `packages` line:

```text
TOMLDecodeError: Unclosed array (at end of document)
```

That one isn't caught, and the script stops with Python's own error. It's readable enough for you, and you're the only one who runs this script, so I've left it. The rule from chapter 131 was about messages for people who didn't write the tool.

## What you learned

A package is a folder with an `__init__.py` in it, and Python imports it by the folder's name. `install.vfpy` reads `pyproject.toml` beside it, places the packages where Python looks, copies the `Scripts` folder into FontLab's menu, and records ownership so that removal can preserve edited files. TOML is tables of `name = value`, and `tomllib.loads` turns it into dictionaries. Before you send tools to someone who can't ask you questions, run the checks that their machine would run, and word the answers yourself.

## Try it yourself

1. Add `live_panel.py` from chapter 128 to the package and give it a launcher. The check should show three menu lines.
2. Make `check` complain when a launcher imports a module that isn't in the package. Reading the launcher's second line and looking for the word after `import` is enough for launchers shaped like yours.
3. Add a file `README.txt` to the folder with the three-line note in it, and make `check` report a problem when it's missing. Rita's colleagues will open the folder without the email.

## Next

Rita's reply comes at ten to one: both tools are in her menu. Mira, back on Monday, has left a request of her own on the board: she wants to see the sidebearing numbers in the Glyph window itself, beside the glyph, without a panel at all. Chapter 134 writes a function that FontLab calls each time it draws a glyph.
