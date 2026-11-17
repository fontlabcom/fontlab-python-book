---
this_file: src_docs/md/part2-a-toolbox/027-read-a-list-from-a-file.md
---

# 27. Read a list from a file

Monday of the fifth week. Over the weekend the publisher's art director decided which small caps the first book needs, and she's sent Ines a text file. Ines forwards it with one line: *Which of these do we have?*

Mira opens `smallcaps.txt`. It's a list of glyph names, one to a line. There are some blank lines in it, and two lines that start with `#`, where the art director has left herself notes.

She could type the names into a Python list, quotes and commas and all. For ten names that's five minutes. But the art director has said this is the first batch. There'll be a second file, and a third, and each time Mira would be retyping somebody else's list and adding her own typos to it.

The names are already in a file. Last chapter the script wrote one. Today it reads one.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- A plain text file to read. Make it now: open a text editor, type the lines below, and save the file as `smallcaps.txt` in your `scripting-book` folder, next to the font. On a Mac, TextEdit needs **Format > Make Plain Text** first.

```text
# Small caps for Plum, first batch
a.sc
b.sc
c.sc
d.sc
e.sc
f.sc
g.sc
h.sc

# figures
zero.sc
one.sc  
```

Leave the blank line in. And put two spaces after `one.sc`, where nobody will see them. Real files that people send you have such things in them, and the script has to cope.

## Step 1: Read the whole thing

Opening a file to read looks like opening it to write, with one piece missing:

```python
from pathlib import Path

from fly import fl

font = fl.CurrentFont()
list_file = Path(font.path).parent / "smallcaps.txt"

with open(list_file, encoding="utf-8") as f:
    text = f.read()

print(text)
```

The Output panel shows the file, line for line, as you typed it.

The `"w"` is gone. Leave the second thing out and `open` assumes you've come to read, which is the safe guess, since reading can't damage anything. `f.read()` takes everything in the file and hands it over as one string. The `with` block closes the file as before.

Notice where `print(text)` sits: outside the block, after the file is closed. That works because the text is in the box labeled `text` by then. You don't need the file open any longer than it takes to get the words out of it.

One string holding thirteen lines isn't much use yet. Ask how long it is:

```python
print(len(text))
```

```text
103
```

A hundred and three characters. Count the letters you typed and you'll come up short, because some of those characters are ones you can't see: the line endings, one at the end of every line, and the two spaces after `one.sc`. Last chapter you typed the line ending as `\n` when you wrote a file. Here it is coming back.

## Step 2: One line at a time

You want a list of names, and the file has one name to a line. Python lets you loop over an open file as if it were a list of lines:

```python
wanted = []
with open(list_file, encoding="utf-8") as f:
    for line in f:
        wanted.append(line)

print(len(wanted))
print(wanted[:3])
```

```text
13
['# Small caps for Plum, first batch\n', 'a.sc\n', 'b.sc\n']
```

Thirteen items, one for each line in the file. Now look hard at the second line of output, because the trouble for the rest of the chapter is in it. Each string ends in `\n`. When Python hands you a line from a file, it hands you all of it, the line ending included.

Printing a list shows you its strings in their raw form, quotes and backslashes and all. That's why I printed the list and not the lines one by one. When something read from a file misbehaves, print it inside a list and look for what's hiding at the ends.

## Step 3: The name that isn't there

Does it matter? Ask the font about the second line of the file. You know from chapter 6 that `font[name]` gives you the glyph, or `None` when there's no glyph by that name. I couldn't run this one in FontLab, so take the `None` below as what I expect from chapter 6. And you know `a.sc` is in the font, because Mira added it in chapter 8.

```python
name = wanted[1]
print(name)
print(font[name])
```

```text
a.sc

None
```

Printed, the name looks right. There's an empty line under it, which is your only hint. And the font says it has no such glyph.

The font is correct. It has a glyph named `a.sc`, four characters. You asked for `a.sc\n`, five characters. To a person those are the same name. To a computer they're as different as `a.sc` and `a.scx`. Nothing complains. The name with an invisible line end on it isn't in the font, and that's all you're told. You get a quiet wrong answer: every name in the art director's list would be reported missing.

Text has a method for this, `strip`. It hands back the string with everything invisible trimmed off both ends: line endings, spaces and tabs.

```python
print([name.strip()])
print(font[name.strip()])
```

```text
['a.sc']
<fgGlyph 'a.sc'>
```

`strip` only trims the ends. A space in the middle of a string stays where it is. And like `upper` in chapter 25, it doesn't change the string in the box. It hands you a new one, and it's up to you to keep it.

So strip every line you read from a file, as a habit.

## Step 4: Skip what isn't a name

Strip each line on the way into the list and print the result:

```python
wanted = []
with open(list_file, encoding="utf-8") as f:
    for line in f:
        wanted.append(line.strip())

print(wanted)
```

```text
['# Small caps for Plum, first batch', 'a.sc', 'b.sc', 'c.sc', 'd.sc', 'e.sc', 'f.sc', 'g.sc', 'h.sc', '', '# figures', 'zero.sc', 'one.sc']
```

Better. The line endings are gone, and so are the two spaces after `one.sc`. Three items still aren't glyph names. Two are the art director's notes. One is `''`, two quote marks with nothing between them: that's the blank line, which was nothing but a line ending, and stripped down to an empty string.

You need an `if` that lets names through and keeps the rest out. Both tests are ones you have. An empty string equals `""`. A note starts with `#`, and `startswith` is from chapter 9.

```python
wanted = []
with open(list_file, encoding="utf-8") as f:
    for line in f:
        name = line.strip()
        if name != "" and not name.startswith("#"):
            wanted.append(name)

print(len(wanted), "names")
print(wanted)
```

```text
10 names
['a.sc', 'b.sc', 'c.sc', 'd.sc', 'e.sc', 'f.sc', 'g.sc', 'h.sc', 'zero.sc', 'one.sc']
```

Ten names, clean. Read the `if` line aloud: "if the name isn't empty and doesn't start with a hash". Strip first, then test. A line of spaces is blank only after you've stripped it.

Using `#` for notes isn't a rule of text files. It's a habit the art director picked up somewhere, and it happens to be Python's own comment mark. When you write a script that reads lists, you decide what counts as a note. Whatever you decide, say so in a comment at the top of the script, so the next person knows what they may put in the file.

## Step 5: Which do we have?

Now Ines's question. For each wanted name, is there a glyph? You could ask the font ten times with `font[name]`. I'd sooner build the bag of all glyph names once, as in chapter 25, and ask the bag. It keeps the question in plain sight:

```python
in_font = set()
for glyph in font.glyphs:
    in_font.add(glyph.name)

have = []
missing = []
for name in wanted:
    if name in in_font:
        have.append(name)
    else:
        missing.append(name)

print(f"Asked for: {len(wanted)}")
print(f"In the font: {len(have)}: {' '.join(have)}")
print(f"Still to make: {len(missing)}: {' '.join(missing)}")
```

```text
Asked for: 10
In the font: 3: a.sc b.sc c.sc
Still to make: 7: d.sc e.sc f.sc g.sc h.sc zero.sc one.sc
```

I kept `have` and `missing` as lists and not sets on purpose. The art director wrote her names in an order that means something to her, letters first and figures after. Lists keep that order. A set would shuffle it.

There's a second question hiding here, and it's worth one more line. "In the font" means a glyph by that name exists. Mira made `a.sc`, `b.sc` and `c.sc` as empty glyphs, with nothing drawn in them. A glyph that exists and a glyph that's finished aren't the same, and you have the test for empty from chapter 8. Exercise 2 asks you to put the two together.

## Step 6: The file that isn't there

One more mistake before you save. Change the file name in the script to `smalcaps.txt`, with one l, and run it.

```text
FileNotFoundError: [Errno 2] No such file or directory: '/Users/mira/Documents/scripting-book/smalcaps.txt'
```

Last chapter this error meant a missing folder. Here it means what it says. Read the path in the message letter by letter. It's the exact address Python tried, and nine times out of ten the mistake is visible in it: a misspelled name, a file saved as `smallcaps.txt.rtf` by an editor that wasn't in plain-text mode, or a file that's sitting in Downloads and not next to the font.

Fix the name, and save the script as `read_glyph_list.py`. Here's the whole thing:

```python
# Reads a list of glyph names from a text file next to the font.
# One name per line. Blank lines and lines starting with # are skipped.
from pathlib import Path

from fly import fl

font = fl.CurrentFont()
list_file = Path(font.path).parent / "smallcaps.txt"

wanted = []
with open(list_file, encoding="utf-8") as f:
    for line in f:
        name = line.strip()
        if name != "" and not name.startswith("#"):
            wanted.append(name)

in_font = set()
for glyph in font.glyphs:
    in_font.add(glyph.name)

have = []
missing = []
for name in wanted:
    if name in in_font:
        have.append(name)
    else:
        missing.append(name)

print(f"Asked for: {len(wanted)}")
print(f"In the font: {len(have)}: {' '.join(have)}")
print(f"Still to make: {len(missing)}: {' '.join(missing)}")
```

Mira sends the three lines to Ines. Ines reads "still to make: 7" and asks whether the script could make them. It could. But making glyphs is a change to the font, and changes need more care than questions do. That care starts in chapter 29.

## A language in a file

Chapter 25 said the next language would be a file somebody sends you. Here it is. The rights person has added Slovak, and Ines has typed its special letters into `slovak.txt`, one line:

```text
áäčďéíĺľňóôŕšťúýž
```

Reading it takes what you learned in step 1 and step 3: read the whole file, strip it. Then it's chapter 25 again.

```python
have_characters = set()
for glyph in font.glyphs:
    if glyph.unicode is not None:
        have_characters.add(chr(glyph.unicode))

with open(Path(font.path).parent / "slovak.txt", encoding="utf-8") as f:
    letters = f.read().strip()

need = set(letters) | set(letters.upper())
missing = need - have_characters
missing_text = " ".join(sorted(missing))
print(f"Slovak: {len(need)} needed, {len(missing)} missing: {missing_text}")
```

```text
Slovak: 34 needed, 18 missing: Č č Ď ď Ĺ ĺ Ľ ľ Ň ň Ŕ ŕ Š š Ť ť Ž ž
```

The first four lines fill the bag of characters as `missing_chars.py` did. That script called the bag `have`. I've renamed it here because this chapter already uses `have` for something else. Two boxes can't share a label. Add the lines at the end of `read_glyph_list.py`, where `font` and `Path` are already known, or try them on their own with the two imports on top.

`f.read().strip()` is two steps in one line. Read it left to right: read the file, then strip what came back. The dot after the closing parenthesis works on whatever the first call handed over.

Take `encoding="utf-8"` away and this is the file that suffers. A file of plain glyph names holds nothing but a to z, dots and digits, and reads the same under almost any rule. A file of Slovak letters doesn't. Read with the wrong rule, each ľ comes back as two characters of nonsense, and the script reports missing letters that no language has.

## What you learned

`open(address, encoding="utf-8")` with no `"w"` opens a file for reading, `f.read()` gives you all of it as one string, and `for line in f:` gives you one line at a time. Every line arrives with its line ending attached, so strip it before you compare it with anything. After that, an `if` decides which lines are data and which are blanks or notes.

## Try it yourself

1. Add the line `A.sc` to `smallcaps.txt` and run the script. Then add `a.sc` a second time. What does the report say in each case? Change the script so that a name listed twice is reported once. A set can help, but check what it does to the order.
2. Split "in the font" in two: glyphs that exist and are still empty, and glyphs that exist and have something in them. Use the test for empty from chapter 8. For the art director's list, all three existing glyphs should land in the first group.
3. Put chapters 26 and 27 together. Read `smallcaps.txt`, and write the names that are still to make into `smallcaps-todo.txt` in the `reports` folder, one name to a line. Then point `read_glyph_list.py` at the file you wrote. A list your script wrote should be a list your script can read.

## Next

Tomas is back in chapter 28. He's tired of pasting text into his spreadsheet and getting everything in one column.
