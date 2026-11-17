---
this_file: src_docs/md/part2-a-toolbox/038-read-the-traceback.md
---

# 38. Read the traceback

Tuesday. On Monday evening Mira did exercise 1 of chapter 35. She added a fifth field to every row, the width of the black shape, and she was pleased with it. This morning she runs `widest_first.py`, and after the table the panel fills with a traceback:

```text
Traceback (most recent call last):
  File "<string>", line 23, in <module>
  File "<string>", line 12, in report
  File "<string>", line 17, in print_lopsided
  File "/Users/mira/Library/Application Support/FontLab/FontLab 9/python/3.11/site-packages/halfmoon.py", line 58, in lopsided
    name, lsb, width, rsb = row
    ^^^^^^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 4)
```

In chapter 3 an error message was three lines long, and you learned to read the last one. This one has eight lines, counting the row of little arrows, and mentions two files and four line numbers. Mira's first instinct is to open line 58 of `halfmoon.py` and stare at it, and line 58 is fine. It hasn't changed since Friday.

Error messages got longer when you started writing functions and modules, and they got longer for a good reason. Today you learn to read all of one. It tells you a story if you read it in the right order.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `halfmoon.py` and `widest_first.py` from [chapter 36](036-sort-by-anything.md).
- Step 1 below changes both files. Do it whether or not you did the exercise in chapter 35, so that your files match mine.

## Step 1: Break it the way Mira did

In `halfmoon.py`, change `metrics_rows` so that each row has a fifth field, the width of the black shape. Two lines change: the width gets a box of its own, and the `append` line uses it.

```python
            lsb = measured.getLSB()
            rsb = measured.getRSB()
            width = int(glyph.width)
            rows.append((glyph.name, lsb, width, rsb, width - lsb - rsb))
```

Then replace `widest_first.py` with the listing below. It's the script as Mira has it this week. She split it into two functions so that each job has a name. I've left out the heading row and the check for an empty list, to keep today's trail short.

```python
#FLM: Widest First
# Prints the metrics of the selected glyphs, widest first.
from fly import fl
import halfmoon

HOW_MANY = 3


def report(rows):
    for name, lsb, width, rsb, black in sorted(rows, key=halfmoon.by_width, reverse=True):
        print(f"{name:<8}{lsb:>5}{width:>7}{rsb:>5}{black:>7}")
    print_lopsided(rows)


def print_lopsided(rows):
    print("Most lopsided:")
    for row in sorted(rows, key=halfmoon.lopsided, reverse=True)[:HOW_MANY]:
        print(f"  {row[0]:<6}{halfmoon.lopsided(row):>3}")


font = fl.CurrentFont()
rows = halfmoon.metrics_rows(font, only_selected=True)
report(rows)
```

She remembered to unpack five names in `report`. Select a few glyphs, reload the module and run it. You get the table, the words `Most lopsided:`, and then the traceback from the top of this chapter. Your line number in `halfmoon.py` won't be 58, and the path will have your name in it. FontLab's Output panel may also lay the lines out a little differently. The parts are the same.

## Step 2: The last line first

You already know this part. The last line is the complaint itself:

```text
ValueError: too many values to unpack (expected 4)
```

It has the kind of error, a colon and the detail. You met this exact message in chapter 35: a row had more items than there were boxes to put them in. Four boxes were waiting, so the row had five or more.

Always read this line first, and read all of it. It's tempting to see the word `Error` and start changing things. Often the last line is enough.

## Step 3: The lines above are a trail

Now the middle. Each line that begins with `File` is one step on the way to the accident, and they're in the order things happened. Read them from the top down:

```text
  File "<string>", line 23, in <module>
```

"In the script you ran, at line 23, at the top level." `<string>` is the name you saw in chapter 3: it stands for the script in the Scripting panel's window. `<module>` means the line isn't inside any function. Line 23 is `report(rows)`. So the script called `report`.

```text
  File "<string>", line 12, in report
```

"In the same script, line 12, inside the function `report`." Line 12 is `print_lopsided(rows)`. So `report` called `print_lopsided`.

```text
  File "<string>", line 17, in print_lopsided
```

Line 17, inside `print_lopsided`. That's the `sorted` line with `key=halfmoon.lopsided`. So `print_lopsided` asked `sorted` to do its work, and `sorted` called the key function.

```text
  File "/Users/mira/.../site-packages/halfmoon.py", line 58, in lopsided
    name, lsb, width, rsb = row
```

"In the file `halfmoon.py`, line 58, inside the function `lopsided`." Here Python can show you the line itself, because the file is on disk where it can read it. That's where it fell over.

So the story reads: the script called `report`, which called `print_lopsided`, which had `sorted` call `lopsided`, and inside `lopsided` a row wouldn't fit into four boxes. Each function was waiting for the next one to finish when the last one failed. That chain of waiting functions is what the first line, `Traceback (most recent call last)`, announces. It says the calls are listed in order, with the newest at the bottom.

In chapter 3 I called an error message a letter of complaint. A traceback is the same letter with the route on the envelope. Picture a relay team. The baton passes from runner to runner, and the fourth runner drops it. The traceback names all four in order, so that you can ask whether the fourth was clumsy or was handed a baton too slippery to hold.

## Step 4: Where it fell isn't where the mistake is

In this case the baton was slippery. Line 58 is the place where Python noticed the problem. It isn't the place where the problem was made.

Line 58 says "unpack a row into four boxes". That was correct on Friday and it's correct in itself today. What changed is the rows. `metrics_rows` now makes them with five fields. Mira changed the maker and forgot one of the users.

The traceback can't tell you that directly, because `metrics_rows` isn't in it. It ran and finished long before the error. It handed back a perfectly good list of rows with five fields, and by the time `lopsided` choked on one, `metrics_rows` was no longer waiting for anything. A traceback only lists the functions that were still in the middle of their work.

What the traceback does give you is the right question: where did this row come from? Walk the trail backward. `lopsided` got the row from `sorted`. `sorted` got its rows from `print_lopsided`, which got them from `report`, which got them from line 21 of the script: `rows = halfmoon.metrics_rows(font, only_selected=True)`. That's the maker. Open it, and the fifth field is there to see.

You met this pattern in chapter 19, in a smaller form. A box was filled with `None` on one line, and the complaint came from a later line that tried to use it. "Don't stare at the line it points to. Look upward for the box that was filled with nothing." This is the same rule on a larger scale: when the line it points to looks innocent, follow the data back to where it was made.

The fix is one line in `lopsided`:

```python
def lopsided(row):
    name, lsb, width, rsb, black = row
    return abs(lsb - rsb)
```

There's a habit that would have saved the morning, too. When you change what a function hands back, look for everybody who uses it before you run anything. In chapter 35, exercise 1 asked "which other lines, in which files, have to change?" Now you know why I asked.

## Step 5: Whose file is it?

Your scripts now stand on a stack of other people's work. A script calls `halfmoon`, which calls Fly's helpers, which call FontLab. When something fails low in the stack, the trail runs through files you didn't write. Close every font, and run these three lines:

```python
import fly.ap.glyphs.names.model as names

facts = names.scan()
```

```text
Traceback (most recent call last):
  File "<string>", line 3, in <module>
  File "/Users/mira/.../site-packages/fontlabapp/glyphs/names/model.py", line 94, in scan
    raise ValueError("Open a font first.")
ValueError: Open a font first.
```

The trail has two steps. The first is yours: line 3 of your script. The second is in a file called `model.py`, deep in a folder you've never opened, and the line it shows begins with the word `raise`.

`raise` is how a piece of Python code makes an error on purpose. Somebody who wrote that helper thought about what should happen when no font is open, decided the helper couldn't go on, and wrote a line that stops with a message for you. So this isn't a crash. It's a refusal, and you've seen these before: `Refused.` in chapter 29, and the statuses in chapter 30.

The rule for a trail that runs through other people's files is simple. Find the last line of the trail that's in a file of yours. Start there.

The error was noticed in `model.py`, but `model.py` has been run by many people, and line 94 of it is doing exactly what its author meant. The newest thing in the whole stack is your script, written this morning. That's where to look first. What did line 3 ask for, and what was true at that moment? It asked for a scan, and no font was open.

Only when your own line is beyond suspicion is it worth reading the stranger's file. You're allowed to. The path is right there in the message, the file is plain Python, and reading the ten lines above a `raise` often tells you exactly what the helper wanted. But read your own line first.

## Step 6: Errors that come from FontLab

So far, every message has been Python's or a Python helper's. FontLab itself is not written in Python, and when you reach it directly, problems can look different. I haven't been able to run these on FontLab 9 for you, so take this step as a description of what to expect and not as a transcript.

Sometimes FontLab does what Python does and you get an ordinary traceback whose last line names a kind of error.

Sometimes the last line is a `TypeError` with a long list of what the call would have accepted. That means you put the wrong kind of thing in a slot of one of FontLab's own functions, and FontLab is showing you every way the function can be called. Read the first lines of it, find your call among them and compare the slots one by one.

And sometimes nothing is printed at all. The script runs to its end, no error appears, and the font hasn't changed. Chapter 14 showed you one cause: a misspelled drawer name on the left of an equals sign. Chapter 29 showed you another: a change made without telling FontLab's history, so that the windows didn't know to redraw. A script that fails without a message is harder to fix than one that prints twenty lines of traceback, because it gives you no trail to follow. That's a strong reason to prefer the helpers that refuse out loud.

If FontLab itself closes while a script runs, that isn't an error message, and it isn't your fault in the ordinary sense. Write down the last thing the script did and tell FontLab's support. Meanwhile, the font you saved before running the script is still on disk, and saving first was for exactly this.

## A field guide

You've now met most of the errors you'll see in a year of scripting. Here they are in one place, with what each usually means in a font script:

| Last line starts with | What it usually means | First thing to check |
|---|---|---|
| `SyntaxError`, `IndentationError` | Python couldn't read the script, and nothing ran | the line it names and the one above: a missing colon, bracket or quote, or crooked indents |
| `NameError` | a word Python doesn't know | spelling, a missing import, or quotes left off a string |
| `ModuleNotFoundError` | `import` found no such file | the file's name and its folder (chapter 33) |
| `AttributeError: 'NoneType' ...` | a box holds `None` where you expected an object | where the box was filled: no font open, no glyph by that name, empty selection |
| `AttributeError: ... has no attribute` | no drawer by that name | spelling and capitals; for your own module, a stale copy that needs a reload |
| `TypeError` | the wrong kind of thing, or the wrong number of things, in a slot | count the slots; look for a string where a number belongs |
| `ValueError` | the right kind of thing with an unusable value | unpacking counts; `int("wide")`; a helper's refusal, which says why |
| `KeyError` | a dictionary has no such key | print the keys; use `get` with a fallback (chapter 22) |
| `IndexError` | a list is shorter than you thought | print its `len`; an empty list has no `[0]` |
| `FileNotFoundError` | no file at that path | print the path; is the font saved? (chapter 26) |
| `ZeroDivisionError` | you divided by zero | a count that came out 0, often from an empty selection |

Look how often an empty selection or a missing font turns up in the right-hand column. Most errors in font scripts aren't about Python at all. The script assumed the world was in a certain state and it wasn't. That's why chapter 19 taught you to check for a font at the top, and why chapter 36's script checked that `rows` wasn't empty before it printed anything.

## What you learned

A traceback is a trail of calls in the order they happened, and each `File` line names a file, a line number and the function that was waiting there. Read the last line first for the complaint, then the trail from the top for the story. The line where Python fell over often isn't where the mistake was made, so follow the data back to its maker. When the trail runs through other people's files, start at the last line that's in a file of yours.

## Try it yourself

1. In `widest_first.py`, change `HOW_MANY = 3` to `HOW_MANY = "3"`, with quotes. Before you run it, predict the kind of error, and how many `File` lines the trail will have. Then run it and compare. Put the number back.
2. In `widest_first.py`, change `only_selected=True` to `only_selected=False`. Close every font and run it. I expect a trail that ends inside `halfmoon.py` with an `AttributeError` about `NoneType`, though I haven't seen FontLab print it. Read whatever you get aloud as a story, in the manner of Step 3: who called whom, and where did it fall? Then say where the fix belongs. It isn't in the line the trail ends on. Put `True` back.
3. Open `halfmoon.py`, take the colon off the end of any `def` line and save it. Put a `print("start")` above the `import halfmoon` line of a script that reloads the module, and run it. Does `start` print? Put the colon back. Now take a colon off a `def` in the script itself and run again. Does `start` print this time? Why the difference? Put that colon back too.

## Next

Mira's scripts refuse when something's wrong, and they print when something's right. What they can't do yet is ask. Chapter 39 puts a question on the screen and waits for the answer.
