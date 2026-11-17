---
this_file: src_docs/md/part7-tools/137-drive-it-from-outside.md
---

# 137. Drive FontLab from outside

It's Thursday 7 January, and tomorrow is a Friday. Ines has run the Friday build more than once now, and each time it began the same way: find FontLab among the open windows, open the Scripts menu, find Halfmoon, click.

"I have a terminal window open all day," she says. "I type one line and things happen. Can the build be one line?"

Some of it can. Today a Python script that isn't inside FontLab asks FontLab to do things and reads the answers. You'll also find the limit: FontLab gives a job from outside five seconds, and the Friday build was never a five-second job.

## What you need

FontLab open with `Plum-practice` in front. The Friday scripts from chapters 114 to 119, where FontLab can import them. `uv` from chapter 4, and a copy of Remopy, which comes as a folder called `fontlab-remopy` from the same place as Fly.

Two things about today are different from every other chapter, and I'd like them said before any code.

The script you write today doesn't run in FontLab. It runs in the Terminal, in an ordinary Python that has never heard of FontLab. So it can't start with `from fly import`, and it doesn't: it's the one script in this book that imports another package by name. The rule since chapter 4 was about scripts inside FontLab, and that rule stands.

And I have run less of this chapter than of any other. I ran `friday.py` against a stand-in that answers the way Remopy's own code says FontLab answers: a value and the printed text on success, an error with a type and a message on failure, and no answer at all when time runs out. The lines `friday.py` prints are from those runs. I haven't seen it talk to a real FontLab. How long each Friday step takes on Plum, which decides whether this chapter works for you, I can't tell you.

## Step 1: Two programs

Until now there was one program. Your script ran inside FontLab, as a guest in its house, and could touch anything.

Today there are two. FontLab is one. The other is a plain Python started from the Terminal. They don't share names, modules or memory. All that passes between them is text: one sends a request, the other sends back an answer.

The usual words are client and server. The server is the program that waits to be asked, and here that's FontLab. The client is the one that asks. A waiter and a kitchen work this way. The waiter can't cook and can't see the stove; he hands in a slip and gets back a plate, or a message that the fish is off.

FontLab has to agree to be asked. It's a preference, which Remopy's documents call `mcp.enabled`, that lets programs outside FontLab send it requests. Remopy can switch it on for you. In the Terminal, in the folder that holds `fontlab-remopy`:

```text
uv run --with ./fontlab-remopy fontlab-remopy setup
```

`uv run --with` means "run this with that package available, for this one run". Nothing is installed for good.

## Step 2: Ask one question

Save this as `ask.py`, beside the `fontlab-remopy` folder:

```python
from fontlab_remopy import FontLab

with FontLab() as app:
    print(app.eval("1 + 1"))
```

And run it from the Terminal:

```text
uv run --with ./fontlab-remopy ask.py
```

```text
2
```

That's an unimpressive result with a strange history. The text `1 + 1` went from your script to FontLab; FontLab's Python worked it out; the answer came back as text and was turned into a number again. `FontLab()` in a `with` block opens the line and closes it when the block ends.

`eval` is for one expression. For several lines there's `run`, which takes a whole piece of Python as a string. Whatever that code puts in a variable called `result` comes back to you:

```python
from fontlab_remopy import FontLab

CODE = """
from fly import fl

font = fl.CurrentFont()
print("counting")
result = len(font.glyphs)
"""

with FontLab() as app:
    done = app.run(CODE)
    print(done.value)
    print(done.stdout)
```

The code in the string is a FontLab script, and it does start with `from fly import`, because it runs in there. What comes back has two parts you'll use: `done.value` is what `result` held, and `done.stdout` is everything the code printed. Its `print` didn't go to FontLab's Output panel. It was caught and sent back to you.

The value must be something that survives being written down as text: a number, a string, `True`, `None`, a list or dictionary of those. A glyph can't cross. You can't bring the font to the Terminal, only facts about it.

## Step 3: One call for the whole build

Here is the tempting version, and the mistake. The Friday build is a function, so ask for it:

```python
from fontlab_remopy import FontLab

with FontLab() as app:
    app.run("import friday_build\nfriday_build.main()")
```

Two things go wrong, and neither is your code's fault.

First, there are two clocks. FontLab stops any code sent from outside after five seconds; that limit is FontLab's, and Remopy can't raise it. Remopy has a patience of its own, thirty seconds unless you ask for another number, after which it stops waiting and raises `TimeoutError`. I haven't seen what comes back when FontLab's five seconds run out: it may be an error with FontLab's own wording, or an answer Remopy can't read. The second half of the build writes two proofs and reads ten font files. I'd be surprised if that fits.

Second, and worse, is what you know afterwards. When the time runs out, the client gets no answer. No answer isn't "it failed". The work may have stopped half-way, or finished a moment after the line went quiet. Remopy's documents put it plainly: the outcome is unknown, so check FontLab before repeating.

This is new. Inside FontLab, a script that failed told you so. Between two programs there are three results: yes, no, and silence. Silence has to be treated as "go and look".

That changes how you cut the work up. Each request should be short, so that it fits. And a request whose silence would be dangerous shouldn't be sent at all. Chapter 119's last step gives the font its next version number. If that call went silent, you wouldn't know whether Plum is at 1.004 or 1.005, and running it again might make it 1.006. So that step stays inside FontLab, where the answer appears in front of you and Edit > Undo is one keystroke away. The steps that only read and report are safe to repeat, and those are the ones to drive from outside.

There's a third trap in the same call. `friday_build.main` opens a small window when no font is open, and so does any script that uses chapter 39's `ask` or `tell`. A window waits for a click. Nobody is there to click, and the call ends without a useful answer. Code you send from outside mustn't ask questions.

## The whole script

```python
# Runs the Friday build's checks in FontLab from a terminal window.
# FontLab must be open, with the font in front.
#     uv run --with ./fontlab-remopy friday.py
# This file runs outside FontLab, so it can't import fly.
from fontlab_remopy import FontLab, NativeExecutionError, ResultTransportError

WHICH_HALF = """
import export_family
import fly.ap.core.scripting as scripting
import friday_build
from fly import fl

result = "none"
font = fl.CurrentFont()
if font is not None and font.path:
    folder = export_family.export_folder(font, scripting.current_package())
    result = "before"
    if folder.exists() and friday_build.font_files(folder):
        result = "after"
"""

HALVES = {
    "before": [("Checks", "ship_check", "main")],
    "after": [
        ("Files", "export_family", "main"),
        ("Inspect", "inspect_export", "main"),
        ("Glyph proof", "proof_html", "main"),
        ("Text proof", "proof_text", "main"),
        ("Source copy", "friday_build", "keep_source"),
    ],
}


def code_for(module, function):
    return f"import {module}\nresult = {module}.{function}()"


def run_step(app, label, module, function):
    try:
        done = app.run(code_for(module, function))
    except NativeExecutionError as problem:
        error = problem.payload.get("error")
        if type(error) is dict:
            print(f"{label}: DID NOT RUN: {error['type']}: {error['message']}")
        else:
            print(f"{label}: DID NOT RUN: {problem}")
        return False
    except (TimeoutError, ResultTransportError):
        print(f"{label}: no answer. It may or may not have run. Look in FontLab.")
        return False
    if done.stdout:
        print(done.stdout.strip())
    if done.value != 0:
        print(f"{label}: stopped the build ({done.value})")
        return False
    print(f"{label}: ok")
    return True


def main():
    with FontLab() as app:
        half = app.run(WHICH_HALF).value
        if half == "none":
            print("Open a saved font in FontLab first.")
            return
        print(f"{half.capitalize()} the export.")
        for label, module, function in HALVES[half]:
            if not run_step(app, label, module, function):
                return
    if half == "before":
        print("Checks passed. Run Friday Build in FontLab, export, then run this again.")
    else:
        print("Files checked. Friday Build in FontLab gives the font its next number.")


if __name__ == "__main__":
    main()
```

Save it as `friday.py`, beside `ask.py`.

`WHICH_HALF` is a FontLab script kept in a string, in the triple quotes of chapter 98. It's chapter 119's own test, moved: no saved font gives `"none"`, a folder with font files in it gives `"after"`, and anything else gives `"before"`. It answers with a word and opens no window.

`HALVES` lists the steps for each half as a label, a module and a function. They're chapter 119's lists with two differences. Each step is named in text, because the functions themselves live in FontLab and can't be mentioned out here. And "Next version" is missing, for the reason in step 3.

`code_for` writes the two-line script for one step. Chapter 119 arranged for every one of these functions to return its count of problems, and that count is what crosses back as `done.value`.

`run_step` has the three results in it. An error inside FontLab arrives as `NativeExecutionError`, whose `payload` carries the type and message of what went wrong in there. When FontLab's wording isn't the usual pair of type and message, the script prints whatever the error says of itself. `type(error) is dict` is chapter 11's `type` put to work: is this thing a dictionary? Silence arrives as `TimeoutError`, or as `ResultTransportError` when something came back that Remopy couldn't read, and the line it prints says the one true thing about both. The brackets after `except` hold two kinds of error for one block, as in chapter 99. Otherwise there's an answer: the step's own printed lines are shown, and anything but zero stops the build, as in chapter 119.

After a silence, `main` stops. It doesn't try the next step, and Remopy wouldn't let it: once a call has timed out, the line is closed until you open a new one.

## Run it

Before the export:

```text
uv run --with ./fontlab-remopy friday.py
```

```text
Before the export.
...
Checks: ok
Checks passed. Run Friday Build in FontLab, export, then run this again.
```

Where I've put three dots you'll see the lines `ship_check.py` prints, the table from chapter 114. They were printed inside FontLab and carried out to your Terminal.

Ines still has to go to FontLab once, and that isn't new: chapter 119 already had a manual step in the middle, because the export is hers to do. After the export, the same line again:

```text
After the export.
...
Files: ok
...
Inspect: ok
...
Glyph proof: ok
...
Text proof: ok
Source copy: ok
Files checked. Friday Build in FontLab gives the font its next number.
```

If one of those steps takes longer than five seconds on your machine, I expect one of two lines in its place, and the run ends there. Either a `DID NOT RUN` line carrying FontLab's words, or this:

```text
Glyph proof: no answer. It may or may not have run. Look in FontLab.
```

Then look. If the proof file is in today's folder with the right time on it, the step ran. And tell me which step it was. A step that can't fit has to be cut smaller inside its own script, and that's a change to chapter 116 or 117.

Ines gets most of what she asked for. It's one line, typed twice, with one visit to FontLab between and one after.

## Break it on purpose

In `HALVES`, change `"ship_check"` to `"ship_chek"` and run it:

```text
Before the export.
Checks: DID NOT RUN: ModuleNotFoundError: No module named 'ship_chek'
```

The error happened in FontLab. Its type and its message travelled back as text and your script printed them. That's the "no" of the three results, and it's as clear as an error inside FontLab ever was. Put the name back.

Now close FontLab and run it again. I can't show you these lines, because my stand-in is never closed. Remopy looks for FontLab's side of the line and, depending on what it finds, raises `FileNotFoundError` or times out on the first call, the one that asks which half. Notice that `main` has no `try` around that call. Add one in exercise 2.

## What you learned

Two programs that can't see inside each other can still work together by passing text: a client asks and a server answers. What crosses is plain data, so you send code as a string and get numbers, words and printed lines back. A request can end in yes, in no, or in silence, and silence means the outcome is unknown. So work driven from outside is cut into short requests, opens no windows, and leaves out any step that would be dangerous to repeat.

## Try it yourself

1. Write `count.py`, which prints the number of glyphs in the current font and the font's family name, using one `run` and a dictionary as the `result`.
2. Wrap the `WHICH_HALF` call in `main` so that a `TimeoutError` or `FileNotFoundError` prints "FontLab isn't answering. Is it open?" and ends the script.
3. Before the steps of either half, print the font's version number, so the Terminal shows which build this is. Chapter 96 has the name to ask for. Send it as code and bring the answer back as `result`.

## Next

The release notes for 1.004 need pictures: the specimen line, and the `n` with its new sidebearing numbers under it. Mira has been taking them by hand, cropping each one. Chapter 138 has FontLab take its own pictures.
