---
this_file: src_docs/md/part1-first-words/017-comments-and-names.md
---

# 17. Notes to yourself

Tomas is laying out a table for the publisher's catalog and his columns are narrow. He wants to know which glyphs in Plum are wider than 700 units, because those are the ones that will push his numbers out of line.

Mira knows she wrote that script. She wrote it some time ago, late, between two other things. She finds it in the `scripting-book` folder under the name `w2.py`, opens it, and looks at it for a while.

```python
from fly import fl
f = fl.CurrentFont()
c = 0
for g in f.glyphs:
    if g.width > 700:
        c = c + 1
        print(g.name, g.width)
print(c)
```

It runs. It prints 22 glyphs and the number 22. But is 700 the number Tomas asked for, or one she tried on the way to another number? What was `c` for? Why is the file called `w2`? Was there a `w1`?

Nothing in the script is wrong. Python reads it without complaint. The reader it fails is Mira, eight days later.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- The eight lines above. Type them into a new script and save it as `w2.py`, so you have Mira's problem in front of you.

## Step 1: Lines that Python skips

Add one line at the top of the script, starting with the sign `#`:

```python
# Lists the glyphs that are wider than 700 units.
from fly import fl
f = fl.CurrentFont()
```

Run it. The output is the same as before: the same 22 glyphs, the same 22 at the end.

Python saw the `#` and stopped reading that line. Everything from the `#` to the end of the line is a **comment**: a note for people. You can write anything there, in any language, with any punctuation, and Python won't look at it.

A comment doesn't need a line of its own. It can sit at the end of a line of code, and Python reads the code and skips the rest:

```python
    if g.width > 700:  # Tomas's column limit, in font units
```

Now take the `#` away from your first line and run the script.

```text
    Lists the glyphs that are wider than 700 units.
          ^^^
SyntaxError: invalid syntax
```

Without the sign, Python tries to read your English as Python and gives up at the second word. That's the whole job of the `#`: it's a fence, like the quotes around a piece of text, except that it has no closing half. The end of the line closes it. Put it back.

## Step 2: Switch a line off

There's a second use for the sign, and you'll use it every day. Put a `#` in front of a line of code, and that line stops running. Nothing is deleted. Take the sign away and the line is back.

Mira only wants the count today, not the list. She could delete the `print` inside the loop, and then type it again tomorrow when she wants the list. Or:

```python
for g in f.glyphs:
    if g.width > 700:
        c = c + 1
        # print(g.name, g.width)
print(c)
```

```text
22
```

Programmers call this "commenting out" a line. It's how you try a script with and without one of its parts. When a script misbehaves and you can't see why, switch off lines one at a time until it behaves, and you've found the line to look at.

One habit to go with it: when you're done trying, either switch the line back on or delete it. A script with a dozen switched-off lines in it is as hard to read as one with no notes at all. Take the `#` away from the `print` now.

## Step 3: Names that explain themselves

Look at the labels on Mira's boxes: `f`, `c`, `g`. They saved her a few keystrokes last week and cost her five minutes today.

You chose good labels in the earlier chapters without thinking about it, because I chose them for you: `font`, `glyph`, `count`. Change the short ones here. There are three, and each appears more than once, so go slowly and change every one:

```python
# Lists the glyphs that are wider than 700 units.
from fly import fl
font = fl.CurrentFont()
wide_count = 0
for glyph in font.glyphs:
    if glyph.width > 700:
        wide_count = wide_count + 1
        print(glyph.name, glyph.width)
print(wide_count)
```

Run it, and check that you still get 22. If you get a `NameError`, you missed one. The message names the label Python couldn't find, and that's the one you changed in some places and not in others.

Read the loop out loud now. *For glyph in font glyphs: if glyph width is more than 700, wide count becomes wide count plus one.* It's close to a sentence. That's the test for a name: read the line aloud and listen for whether it says what it does.

A few customs that Python people follow, and that this book follows:

- Lowercase letters, with an underscore where a space would go: `wide_count`, not `WideCount` or `widecount`.
- A name says what's in the box, not what kind of thing it is. `wide_count` is better than `number`.
- One thing gets a singular name and a list of things gets a plural one. That's why the loop reads `for glyph in font.glyphs`.
- Short names are fine when the box lives for one or two lines. Long-lived boxes get real names.

## Step 4: Pull the number out

The number 700 appears once in the script, in the middle of a line, with nothing to say what it is. Tomorrow Tomas will change his mind and ask for 800. Mira will have to find the number, and be sure she found the right one.

Give the number a name and move it to the top. The import line stays where it is; change the lines below it:

```python
LIMIT = 700  # font units

font = fl.CurrentFont()
wide_count = 0
for glyph in font.glyphs:
    if glyph.width > LIMIT:
        wide_count = wide_count + 1
        print(glyph.name, glyph.width)
print(wide_count)
```

`LIMIT` is a box like any other. The capitals are a custom, not a rule of the language: they tell the next reader "this is a setting, it's decided once at the top and the script doesn't change it afterwards". When you open a script and see a few lines of capitals near the top, you know where the knobs are. Settings like this are the one thing a function may read without a slot, as `is_wide` will do in the finished script.

Change 700 to 800 and run.

```text
AE 852.0
M 840.0
OE 989.0
W 859.0
Wacute 859.0
Wcircumflex 859.0
Wdieresis 859.0
Wgrave 859.0
oe 824.0
emdash 1000.0
at 848.0
11
```

Eleven. One number changed, in a place you could find with your eyes shut. Set it back to 700.

Remember that Python cares about capitals. `LIMIT`, `Limit` and `limit` are three different labels. If you write the box as `LIMIT` and ask for `limit` further down, you get the `NameError` you met in chapter 3.

## Step 5: A header, some air and a template

Three more changes and the script is finished.

**A header.** The first lines of a script are the first thing you see when you open it, so that's where the answers to Mira's questions go: what the script is called, what it does and who wanted it. Two or three comment lines are enough.

**Air.** Python ignores empty lines, and people don't. Put one between the parts of a script the way you'd put space between paragraphs: the imports, the settings, the functions, the work.

**The function.** In chapter 16 you learned to give a step a name with `def`. The test in the middle of the loop is a step, and it deserves one.

Here's the whole thing. I've also used what chapter 12 taught about lining up columns, and given the last line some words.

```python
# wide_glyphs.py
# Lists every glyph in the current font that is wider than LIMIT,
# then says how many there are. Written for Tomas's column check.

from fly import fl

# Settings. Change these, leave the rest alone.
LIMIT = 700  # font units


def is_wide(glyph):
    return glyph.width > LIMIT


font = fl.CurrentFont()
wide_count = 0

for glyph in font.glyphs:
    if is_wide(glyph):
        wide_count = wide_count + 1
        print(f"{glyph.name:<14}{glyph.width:>6.0f}")

print(f"{wide_count} glyphs are wider than {LIMIT}")
```

The output ends like this:

```text
emdash          1000
percent          798
at               848
22 glyphs are wider than 700
```

Save it as `wide_glyphs.py`. The file name is the last piece of naming, and the same rule holds: it says what the script does. Then delete `w2.py`. Mira does, with some feeling.

Compare the two versions. They do the same work. The first is eight lines and the second is about twenty, and the second is the shorter read.

Look at the shape of it once more, because every script from here on has the same one:

1. A header: name, purpose, who it's for.
2. The imports.
3. The settings, in capitals.
4. The functions.
5. The work.

Make yourself a blank copy of that shape. Take `wide_glyphs.py`, cut it down to the five parts with a comment line in each, and save it as `template.py`. When you start a new script, open the template, save it under the new name, and fill it in. Starting from a shape is quicker than starting from an empty panel, and the header gets written while you still know what the script is for.

## Step 6: A title for the menu

There's one comment that FontLab itself reads. If the very first line of a script starts with `#FLM:` followed by a space, FontLab takes the rest of that line as the script's title when it lists the script in its **Scripts** menu.

Add it above the header:

```python
#FLM: Wide Glyphs
# wide_glyphs.py
# Lists every glyph in the current font that is wider than LIMIT,
```

To Python this is one more comment, and the script runs as before. You won't see the title anywhere yet, because the script isn't in the menu. Putting it there is the next chapter's job. Without the line, FontLab makes a title out of the file name, which is one more reason to name files well.

Add the same line to `template.py`, with a title you'll remember to change.

??? info "Going deeper: how much to comment"
    Write a comment where the code can't speak for itself: why 700, who asked, what a number's unit is, which chapter of the style guide a rule comes from. Don't write one that repeats the code. `count = count + 1  # add one to count` tells the reader nothing and has to be kept up to date. Good names do most of the explaining, and comments do the rest.

## What you learned

A `#` starts a comment, which Python skips to the end of the line, so you can leave notes for the next reader and switch a line off without deleting it. Names carry most of a script's meaning: lowercase words joined by underscores for boxes and functions, capitals for the settings at the top, and a file name that says what the script does. A script laid out as header, imports, settings, functions and work can be read by someone who has never seen it, and that someone is usually you.

## Try it yourself

1. Open `list_names.py` from chapter 7 and give it the full treatment: header, air, a `#FLM:` title. It has no settings and no functions. Decide whether it needs them, and leave the empty parts out if it doesn't.
2. Add a second setting to `wide_glyphs.py`, `SHOW_LIST = True`, and change the script so that it prints the list only `if SHOW_LIST:`. Set it to `False` and check that you get only the last line. You've replaced the `#` trick from step 2 with a knob.
3. Find the worst name in any script you've written for this book so far. Change it everywhere it appears, run the script, and read the changed lines aloud.

## Next

Chapter 18 moves a script out of the Scripting panel and into FontLab's **Scripts** menu, where it's two clicks away every Friday.
