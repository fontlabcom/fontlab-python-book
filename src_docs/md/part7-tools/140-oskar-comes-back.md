---
this_file: src_docs/md/part7-tools/140-oskar-comes-back.md
---

# 140. Oskar comes back

It's Monday 18 January, and Oskar is back from his holiday.

The wall over Mira's desk is bare. The sheet he left there in July had its eleventh line drawn through in December, and he took it down himself. There's a Halfmoon folder in the Scripts menu that wasn't there when he first went away, and a Halfmoon menu beside it. He opens the Scripts menu, reads down it, and runs the Friday Build on a Monday to see what happens. It runs its checks, then tells him to save, export and come back.

"Who wrote that?"

"I did," Mira says. "Ines made me put it in the menu."

On his keyboard there's one sheet of paper. It's in Mira's handwriting, and it has five lines.

## What you need

`Plum-practice` open, with a glyph in a Glyph window. Nothing new to install.

This chapter has one short script. I ran its plain-Python parts, and the outputs marked as such below are real. What it prints for a FontLab glyph I haven't seen, because I haven't run anything in FontLab 9, and this last time that's the point of the script: it's the one you run to find out what I couldn't tell you.

## The new list

Here's what Mira wrote:

1. *The variable font the publisher wants next.*
2. *Greek, properly: spacing and kerning for the freelancer's glyphs.*
3. *Rita wants the Shift tool in Portuguese.*
4. *Tests for `accentkit`.*
5. *Bold ellipsis: third dot outside the glyph.*

The fifth is the pencil line from chapter 49, still waiting. The fourth you could start this afternoon, with chapter 139 open beside you. The other three have something in common: this book doesn't cover them. There's no chapter on exporting a variable font, none that kerns a script Mira can't read, and nowhere did I show how a tool's labels change language.

That's how it will be from here. The list never ends, and the book does. So the last thing to learn is how to work on a line that nobody has written a chapter for. There are four moves, and you've made each of them already without its name.

## Step 1: Ask the object

Every chapter told you which drawers an object has: `glyph.width`, `glyph.name`. I knew because I'd read the documents. Python lets you ask the object itself.

```python
names = dir("Plum")
print(len(names))
print(names[-3:])
```

`dir` takes any object and returns a list of every name you can put after its dot. For a string, in the Python that FontLab 9 carries, I get:

```text
81
['translate', 'upper', 'zfill']
```

That's real output, and I ran it because I wasn't sure of the number. What I remember about an object and what the object says can differ, and the object is right.

Many of the 81 names start with an underscore. Those are the object's own plumbing, and by a convention every Python programmer keeps, a name that starts with an underscore says "not for you". Leave them out and a string has 47.

`dir` gives names and nothing more. To learn what one of them does, ask for its note:

```python
help("Plum".strip)
```

```text
Help on built-in function strip:

strip(chars=None, /) method of builtins.str instance
    Return a copy of the string with leading and trailing whitespace removed.

    If chars is given and not None, remove characters in chars instead.
```

That's real output. Notice there are no brackets after `strip`: you hand `help` the function itself and don't call it. Whoever wrote the function wrote that note, in triple quotes as its first line, the way chapter 135's script had one at its top.

Two cautions for FontLab's own objects. I expect `dir` to work on them, since it works on everything, but I haven't seen what it lists. And FontLab's objects were written in another language, so many will have short notes or none. For the helpers that Fly routes to, which are written in Python, the notes are there. I read them to write this book.

## Step 2: Read what somebody else wrote

Chapter 135 was a reading lesson: twenty lines by a stranger, taken a line at a time. That skill is now worth more to you than any single helper, because the fastest way to do something new in FontLab is to find a script that does something near it.

You have more to read than you may think. Everything Fly routes to is Python, in files on your disk, in the folder chapter 4 had you make. The `fontlab-fontlabapp` folder alone holds the code behind most of the helpers you've called since chapter 7. When a chapter said that `tell` wraps a helper, `run_standard_message_box`, the helper is in there, and you can open it.

Read as chapter 135 did. First the imports, which say what the script depends on. Then the bottom, which says where it starts. Then follow one call inward, and stop as soon as you know what you came to learn. You don't have to understand a file to borrow one idea from it.

## Step 3: Look before you build

Chapter 133's installer, chapter 136's fontParts and chapter 138's GrabLab all came from other people. Before you start on a line of the new list, spend ten minutes finding out whether part of it exists. These are the pieces I know of around Fly, by the names of their folders:

| Folder | What it is |
|---|---|
| `fontlab-fly` | The toolbag: short names for the packages below. |
| `fontlab-fontlabapp` | Helpers for fonts, windows and dialogs: `ap`. |
| `TypeRig` | Geometry and glyph tools, with its own panels: `tr`. |
| `fontlab-python-pens` | Pens: `fly.pens`. |
| (inside FontLab) | FontLab's own Qt, behind every window since chapter 121: `qt`. |
| `pythonqtside` | For code written for PySide: `qs`. This book doesn't use it. |
| `fontlab-glyport` | Runs scripts written for Glyphs: `gp`. |
| `fontlab-fontport` | fontParts objects on FontLab's fonts: `fp`. |
| `fontlab-python-plugmix` | Ready-made plugins, among them reporters like chapter 134's. |
| `fontlab-python-scriptmix` | A couple of hundred Scripts-menu scripts, sorted into folders. |
| `fontlab-python-examples` | Example scripts and lessons. |
| `fontlab-remopy` | FontLab driven from outside, as in chapter 137. |
| `fontlab-grablab` | Pictures of windows and panels, as in chapter 138. |
| `vfjLib` | Reads and writes FontLab's VFJ files without FontLab. |

I have to be straight about this table. You downloaded Fly and its seven neighbors in chapter 4. When I wrote this, several of the other names weren't yet published where anybody can download them, and I can't tell you which are as you read it. If one isn't where you found Fly, ask on the forum from step 4, and don't trust a download of the same name from somewhere else.

For Mira's third line, start in `fontlab-python-scriptmix`. Among a couple of hundred scripts, somebody may have needed labels in two languages before her.

## Step 4: Ask a person

When the object, the code and the folders haven't answered, ask people. FontLab has a forum at forum.fontlab.com with a section for scripting, and the people who wrote the tools in the table read it.

A question gets answered when it's cheap to answer. Chapter 38 taught you to read a traceback; now you write for somebody who'll read yours. Send four things:

1. What you wanted, in one sentence.
2. The smallest script that shows the trouble. Cut yours down until removing one more line makes the trouble go away. Half the time you find the answer while cutting.
3. What happened: the last lines of the traceback, copied, never retyped.
4. Your FontLab version, and whether Fly is installed.

Oskar's rule for the studio is shorter: "Don't ask me until you can show me ten lines."

## The whole script

Steps 1 and 2 in a form you can keep in the Scripts menu:

```python
#FLM: What's In It
# Lists what an object offers: the names you can put after its dot.
# It reads and prints, and changes nothing.
from fly import fl


def public(thing):
    return [name for name in dir(thing) if not name.startswith("_")]


def matching(thing, word):
    return [name for name in public(thing) if word.lower() in name.lower()]


def show(thing, word=""):
    names = matching(thing, word)
    print(f"{type(thing).__name__}: {len(names)} of {len(public(thing))} names")
    for name in names:
        kind = "does" if callable(getattr(thing, name, None)) else "is"
        print(f"  {kind:<6}{name}")


def main():
    glyph = fl.CurrentGlyph()
    if glyph is None:
        print("Open a glyph first.")
        return
    show(glyph, "width")


main()
```

Save it as `whats_in.py`.

`public` is `dir` without the underscore names. `matching` keeps the names that contain a word, in either case. `show` prints them with one word in front: `does` for a name you call with brackets, `is` for a drawer you read. `callable` and `getattr` are chapter 123's and chapter 95's. `word=""` is a parameter with a start value, as in chapter 34, and since an empty string is inside every string, leaving it out shows everything.

## Run it

On a string and a number, in plain Python, `show("Plum", "strip")` and `show(596.0)` print:

```text
str: 3 of 47 names
  does  lstrip
  does  rstrip
  does  strip
float: 7 of 7 names
  does  as_integer_ratio
  does  conjugate
  does  fromhex
  does  hex
  is    imag
  does  is_integer
  is    real
```

That's real. The script as saved asks the current glyph about "width", and here I can only say what I expect: a first line that starts with the kind of object a glyph is, then a handful of names with `width` among them. Run it, then change `"width"` to `"layer"`, then to `""`.

Read the long list slowly. You'll meet names from all through this book, and many more that it never used. Each of those is something a glyph can tell you or do that I didn't have room for. Some of them are the start of a line on your own list.

## Break it on purpose

Ask for the note on a name that isn't there:

```python
help("Plum".nope)
```

```text
AttributeError: 'str' object has no attribute 'nope'
```

`help` never ran. Python has to fetch `"Plum".nope` before it can hand it over, and the fetch fails. It's chapter 6's error, and you get it for a wrong guess. `whats_in.py` exists so that you don't have to guess.

Now the other mistake, the one that gives no error:

```python
print("Plum".upper)
```

```text
<built-in method upper of str object at 0x10487ce30>
```

That's a function, printed without being called. The number at the end will differ on your machine. Whenever you see angle brackets where you expected a value, you've left off the `()`.

And one caution that has no error message at all. `dir` tells you a name exists. It doesn't tell you whether calling it is safe. Among a glyph's names are some that change the glyph, and a few, as chapter 110 found, that make loose objects FontLab doesn't want held. Before you call a name you found by asking, read its note, look for a script that uses it, and try it on a copy of the font. That has been the rule since chapter 14, and it matters more now that nobody is checking the names for you.

## What you learned

`dir` lists what an object offers and `help` prints the note its author left. A leading underscore means "not for you". The code behind the helpers is on your disk and can be read the way chapter 135 read a stranger's script. Before building, look at what exists. Before asking, cut the trouble down to ten lines. A name you found yourself is tried on a copy first.

Across the whole book, you learned to hand a computer the part of your work that needs no talent, and to check what it did.

## Try it yourself

1. Run `show` on `fl.CurrentFont()`, with `"kern"` as the word. Compare what you find with what chapters 69 to 80 used.
2. Pick one name from a glyph's list that this book never used. Find its note with `help`. Then search the folders from step 3 for a script that calls it.
3. Take a sheet of paper. Write down the job in your own week that takes an afternoon, needs no talent and comes back every time something changes. Then write the questions the script has to answer, as chapter 20 did, before you write a line of code.

## The sheet

Oskar reads Mira's five lines twice. He takes a pencil and writes three words next to the first one. They aren't the three words from July.

*Ask the font.*

Then he pins the sheet to the wall, where the old one was, and goes to make coffee.
