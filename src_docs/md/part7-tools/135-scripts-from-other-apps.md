---
this_file: src_docs/md/part7-tools/135-scripts-from-other-apps.md
---

# 135. Scripts from other apps

It's Tuesday 5 January. A friend of Mira's, who draws type in Glyphs, has sent her a file called `Find Stray Points.py` with a one-line message: "This saved me last month. Does it run in yours?"

A stray point is a path with a single node. It prints as nothing, and it can turn up later as a dot in somebody's PDF. Mira would like to know whether Plum has any. She opens the file, sees `from GlyphsApp import Glyphs` on line six, and passes it across the desk to you.

Today you read a script written for another program, ask a tool what it needs before you run it, and then run it without changing a character of it.

## What you need

`Plum-practice` open, Fly installed, and `halfmoon.py`. Type the friend's script from step 1 and save it as `Find Stray Points.py` in your Downloads folder. That's where a file somebody sends you lands.

I haven't run this chapter in FontLab 9. The part that reads the friend's script without running it works outside FontLab, and I ran it as printed: the reports below are what it said. I also ran the friend's script, unchanged, through the same translating layer on the small test font that layer ships with, which has one glyph. What I haven't seen is that script walking Plum inside FontLab.

## Step 1: Read it before you run it

Here is the whole of what arrived:

```python
#MenuTitle: Find Stray Points
# -*- coding: utf-8 -*-
__doc__ = """
Lists glyphs that have a path with a single node.
"""
from GlyphsApp import Glyphs

font = Glyphs.font
found = []
for glyph in font.glyphs:
    for layer in glyph.layers:
        for path in layer.paths:
            if len(path.nodes) == 1:
                found.append((glyph.name, layer.name))

Glyphs.clearLog()
for name, layer_name in found:
    print("%s (%s)" % (name, layer_name))
print("%d stray points." % len(found))
Glyphs.showMacroWindow()
```

You have never seen this dialect, and you can read most of it anyway. That's worth noticing: after 134 chapters, an unfamiliar script is mostly familiar.

Go through it the way chapter 38 went through a traceback, one line at a time, sorting each into "I know this", "I can guess this" and "I must look this up".

The first line is a comment that plays the part of your `#FLM` line: the name for the other program's menu. The second is a note about the file's text encoding, left over from older Pythons. `__doc__` is a name holding a description; the three quote marks start a string that may run over several lines. None of these three does anything when the script runs.

The middle you know. An empty list, three loops one inside the next, a test with `len`, and a tuple appended for each hit. `font.glyphs` you've used since chapter 7. A layer that has `paths`, and a path that has `nodes`, are a guess you'd get right.

Two lines near the end look odd:

```python
name, layer_name = "A", "Regular"
print("%s (%s)" % (name, layer_name))
print("%d stray points." % 3)
```

```text
A (Regular)
3 stray points.
```

This is how Python filled strings before f-strings. Each `%s` is a gap for a value and `%d` is a gap for a whole number; the values come after the lone `%`, in a tuple when there's more than one. You'd write `f"{name} ({layer_name})"`. You don't need to write the old form, only to recognise it, because a great many scripts in the world still use it.

That leaves the lines to look up: the import, and the three things asked of `Glyphs`. `Glyphs.font` must be the current font, the other program's `fl.CurrentFont()`. `clearLog` and `showMacroWindow` sound like emptying and showing its Output panel.

So you can say what this script does before running it. It reads every layer of every glyph, changes nothing, and prints a list. That's the first question to ask of any script from somewhere else, and you answer it by reading.

## Step 2: Why it can't run, and what an adapter is

Paste it into the Scripting panel and it stops at line six. FontLab has no module called `GlyphsApp`.

You could translate it by hand. `Glyphs.font` becomes `fl.CurrentFont()`, the layers and paths become whatever FontLab calls them, and in half an hour you'd have your own version. Then the friend fixes a mistake in hers, and you have two scripts that have drifted apart.

The other way is an adapter. A travel adapter doesn't change your charger or the wall; it sits between them with one shape on each face. A software adapter is a module with the names one program expects on its front and calls to another program at its back. Chapter 4 listed one in the toolbag and left it there: Glyport, `gp` in Fly. It supplies a `GlyphsApp` module whose `Glyphs.font` is FontLab's current font, wearing the other program's names.

Its own documents are blunt about the edges, and you should be too. It covers the common model: fonts, glyphs, layers, paths, nodes, anchors, components. It doesn't claim to be the other program. Scripts that build that program's own kind of dialog, or that paint in its edit view, or ask an instance for a ready-made interpolated font, are refused with an error that names what was missing. A refusal is the adapter working as it should; one that guessed would be worse.

## Step 3: Ask what it needs

Before running a stranger's script, you can have Glyport read it:

```python
from pathlib import Path

from fly.gp import inspect_source

SCRIPT = Path.home() / "Downloads" / "Find Stray Points.py"

report = inspect_source(str(SCRIPT))
print(report.required_capabilities)
for item in report.dependencies:
    print(item.line, item.module)
```

```text
('glyphs:model',)
6 GlyphsApp
```

`inspect_source` opens the file as text. It doesn't run it. It finds the imports and works out which parts of the adapter the script would lean on. Here the answer is one: the model, which is the part Glyport covers. `dependencies` lists each import with its line.

The report also carries `diagnostics`, which are notes with a `severity` of `"info"`, `"warning"` or `"error"`, and a `message`. For this script there's a warning that nothing in the file says which version of the other program it was written for, so Glyport will assume the newest.

## Step 4: Believe the report too much

Here is the mistake. The report said `glyphs:model` and nothing else, so you conclude the script will work. To see why that's too much, add a line to the end of the friend's script that asks for one of the refused things:

```python
shown = font.instances[0].interpolatedFont
```

Inspect it again:

```text
('glyphs:model',)
6 GlyphsApp
```

The report hasn't changed. The inspector reads imports and broad areas; it doesn't follow every name on every line, and it can't know what a font will hold when the script meets it. Glyport's own report says so in a note of its own: "Imports and capabilities are observations; runtime behavior is unexecuted."

It's chapter 93 again. There, "the features compile" didn't mean "the features are right". Here, "nothing it needs is missing" doesn't mean "it runs". An inspection can tell you no. It can't tell you yes. Only a run can, and for a script that changes things, only a run on a copy. Take the extra line out again.

## The whole script

```python
#FLM: Try A Glyphs Script
# Reads a script written for Glyphs, says what it needs, and runs it
# through Glyport if you agree. What the other script does is its business.
from pathlib import Path

import halfmoon
from fly.gp import inspect_source, run_script

SCRIPT = Path.home() / "Downloads" / "Find Stray Points.py"
KNOWN = ["glyphs:model"]


def findings(report):
    lines = []
    for item in report.dependencies:
        lines.append(f"line {item.line}: imports {item.module}")
    for item in report.diagnostics:
        if item.severity != "info":
            lines.append(f"{item.severity}: {item.message}")
    return lines


def unknown(report):
    return [name for name in report.required_capabilities if name not in KNOWN]


def stops(report):
    return [item.message for item in report.diagnostics if item.severity == "error"]


def main():
    if not SCRIPT.is_file():
        halfmoon.tell(f"There's no file at {SCRIPT}.")
        return
    report = inspect_source(str(SCRIPT))
    print(SCRIPT.name)
    for line in findings(report):
        print(line)
    print("needs:", ", ".join(report.required_capabilities))

    if stops(report):
        print("Python can't read it. Not run.")
        return
    extra = unknown(report)
    if extra:
        print(f"Needs something this script doesn't know: {', '.join(extra)}. Not run.")
        return
    if not halfmoon.ask(f"Run {SCRIPT.name} on the current font?"):
        return
    handle = run_script(str(SCRIPT))
    print("Ran.")
    handle.close()


main()
```

Save it as `try_script.py`.

Three small functions read the report and `main` decides. `findings` turns imports and any note above "info" into lines for the Output panel. `unknown` lists what the script needs beyond `KNOWN`, the short list of things you have decided you trust the adapter with. `stops` collects the messages of errors, which mean Python couldn't read the file at all.

`main` has four ways to stop before running anything: no file, a file Python can't read, a need outside `KNOWN`, and you saying no. Only then does it call `run_script`, which runs the friend's file through the adapter as she wrote it, character for character. `run_script` runs the file and gives back a handle, an object that stands for that one run. `close()` tells Glyport you're done with it, so that whatever the other script held is let go. Glyport's own introduction shows the handle in a `with` block. The code doesn't support that, so the script calls `close()` itself.

The question in the prompt is plain on purpose. You've read this script and know it only reads. The next one somebody sends may not, and `try_script.py` can't tell the difference. The person who reads the script decides.

## Run it

```text
Find Stray Points.py
line 6: imports GlyphsApp
warning: No generation-specific evidence; runtime defaults to glyphs4 unless a profile is specified explicitly.
needs: glyphs:model
```

Then the prompt. Say yes, and the friend's script runs. On the one-glyph test font I ran it on, it printed:

```text
A (Regular)
1 stray points.
Ran.
```

On Plum I expect a longer wait, since it visits every layer of 274 glyphs, and with luck a count of zero. I can't print Plum's answer, because I haven't seen it. "1 stray points" is the friend's grammar, and it stays, because the file is hers.

Mira reads the Output panel, then goes to look at the one glyph it names in her own font. That's the right order: the script points, and a person looks.

## Break it on purpose

In the friend's script, add a line under the import:

```python
import vanilla
```

`vanilla` is the kit the other program's scripts build windows with. Run `try_script.py`:

```text
line 6: imports GlyphsApp
line 7: imports vanilla
needs: glyphs:model, ui:vanilla
Needs something this script doesn't know: ui:vanilla. Not run.
```

The inspector saw the import, named the area, and your script refused, because `ui:vanilla` isn't in `KNOWN`. Glyport does have an answer for some of those windows. Whether to trust it is a decision to make script by script, with the file open in front of you, and a short `KNOWN` list is how you make it on purpose. Take the line out.

Now change the friend's last `print` to the form Python 2 used, with no brackets:

```text
print "%d stray points." % len(found)
```

```text
error: Missing parentheses in call to 'print'. Did you mean print(...)? (Find Stray Points.py, line 19)
warning: Python 2 syntax suggests glyphs2; this is an era heuristic, not a declared app version.
needs:
Python can't read it. Not run.
```

Old scripts look like this. The report is empty after `needs:` because a file Python can't read has no imports to find. Glyport has a tool for adapting such files, and that's beyond this chapter. Put the brackets back.

## What you learned

You can read a script in a dialect you've never used by sorting its lines into known, guessable and to be looked up, and you should, before anything else, to learn whether it changes the font. An adapter puts one program's names in front of another program's objects, so a script can run unchanged and stay the same file its author maintains. An inspection that reads the file without running it can rule a script out, and can't rule it in. And an adapter that refuses what it can't do, by name, is one you can build on.

## Try it yourself

1. Add a count to `findings`: one line saying how many lines the friend's script has. `SCRIPT.read_text()` from chapter 133 and `splitlines` from chapter 87 are enough.
2. Translate the friend's two odd `print` and `%` lines into f-strings in a copy of her file, and check that the copy prints the same. Then decide which file you'd keep, and why.
3. Make `try_script.py` take a list of scripts and print the short report for each, running none. Which of the four stops still make sense?

## Next

The friend's script runs here because an adapter speaks her program's dialect. There's a wider agreement than that: a shared set of names, called fontParts, that several font editors accept. Chapter 136 writes one report that should run in more than one of them, and uses Fly's other adapter, `fp`, to run it in FontLab.
