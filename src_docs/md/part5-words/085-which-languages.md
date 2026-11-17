---
this_file: src_docs/md/part5-words/085-which-languages.md
---

# 85. Which languages can it write?

Friday of week sixteen. The publisher has sold the cookbook to a house in Istanbul, and an email arrives with one line in it: "Does Plum do Turkish?"

Ines thinks so. Mira thinks so too, and then remembers that Turkish has two letters `i`, one with a dot and one without, in both cases, and can't say from memory whether Plum has all four.

In chapter 25 you answered this question for German with two sets and a minus sign. The letters were typed into the script. That was fine for one language on one afternoon. Halfmoon gets this email every month, each time about another language, and the person who knows what Czech needs isn't the person who edits scripts. The letters belong in a file that anybody can open, and the script should read whatever the file holds.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed. The font must be saved, because the script looks for its data file in the folder where the font lives.
- `halfmoon.py` with `tell`.
- A plain text editor to make the data file.

I couldn't run the code in FontLab 9. Reading the file, the sets and the report are plain Python, and I ran them against the code points in Plum's source file. The only FontLab parts are `font.path` and `glyph.unicodes`, which earlier chapters use the same way.

## Step 1: The file

Make a text file called `languages.txt` in the folder that holds `Plum-practice`, the folder where `smallcaps.txt` went in chapter 27. Save it as UTF-8, which is what a plain text editor does unless you tell it otherwise.

```text
# Letters each language needs beyond A to Z and a to z.
# One language to a line: name, colon, letters. Both cases written out.
French: ÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ àâæçéèêëîïôœùûüÿ
German: ÄÖÜẞ äöüß
Spanish: ÁÉÍÑÓÚÜ áéíñóúü ¿¡
Turkish: ÇĞİÖŞÜ çğıöşü
Polish: ĄĆĘŁŃÓŚŹŻ ąćęłńóśźż
Czech: ÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ áčďéěíňóřšťúůýž
```

You can copy the lines from this page. The format is my invention and it's small on purpose: a person can read it, fix it and add a line without knowing any Python. Lines that start with `#` are notes, as in the art director's file.

These six lines are a working list and not a ruling. Each holds the letters a language's own alphabet adds to the basic twenty-six. Borrowed words, quotation marks and currency signs aren't in it. If your client's Polish editor says a letter is missing from my line, the editor is right and you add it.

## Step 2: One line into two parts

Each line has a name, a colon and letters. `split` from chapter 9 cuts a string wherever it finds a separator:

```python
line = "Turkish: ÇĞİÖŞÜ çğıöşü"
name, letters = line.split(":", 1)
print(name)
print(letters)
```

```text
Turkish
 ÇĞİÖŞÜ çğıöşü
```

The `1` says "cut once". A line with a second colon further along would still give two parts, and the two boxes on the left would still fit.

Leave the colon out of a line in the file and the two boxes can't be filled:

```python
name, letters = "Welsh ŴŶ ŵŷ".split(":", 1)
```

```text
ValueError: not enough values to unpack (expected 2, got 1)
```

Python found one part and you asked for two. When somebody else edits the file, this is the message you'll get on the telephone, so it's worth knowing by sight. The fix is in the file, not in the script.

The letters still have spaces in them: one in front and one between the cases. A set makes short work of that. Turn the text into a set of characters and take the space out:

```python
extra = set(letters) - {" "}
print(len(extra))
```

```text
12
```

Twelve letters, six in each case.

## Step 3: The whole file into a dictionary

One language is a name and a set. Six languages are a dictionary from name to set. The reading loop is chapter 27's with the split added:

```python
def read_languages(path):
    languages = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            name, letters = line.split(":", 1)
            languages[name.strip()] = set(letters) - {" "}
    return languages
```

Blank lines and notes are skipped. Each other line becomes one entry.

Until now your dictionaries held numbers, strings and lists on the right. A set goes there as well. The right side of a dictionary takes anything.

## Step 4: What the font can type

The other half is the set of characters the font has. In chapter 25 you built it with a loop and `add`, one code point for each glyph. Since yesterday a glyph can have two, so read the whole list:

```python
have = {chr(code) for glyph in font.glyphs for code in glyph.unicodes}
print(len(have))
```

```text
237
```

That's a comprehension from chapter 37 in curly braces, which makes a set where square brackets make a list. It has two `for` parts, read left to right like two loops, one inside the other: for every glyph, for every code of that glyph, the character.

237 is Plum's 204, plus the 31 glyphs Part 3 built, each with a character of its own, plus the no-break space and the soft hyphen from chapter 84. If you closed the practice font without saving at the end of chapter 60, you have 206, and the last two lines of the report below will be longer than mine.

## Step 5: The report

For each language, the need is the basic alphabet joined with the extras. The gap is need minus have:

```python
def report(languages, have):
    for name, extra in languages.items():
        need = set(BASIC) | extra
        missing = sorted(need - have)
        if missing:
            print(f"{name:<9}lacks {len(missing):>2}: {' '.join(missing)}")
        else:
            print(f"{name:<9}complete ({len(need)} characters)")
```

Run the whole script, which is below:

```text
French   complete (84 characters)
German   lacks  1: ẞ
Spanish  complete (68 characters)
Turkish  complete (64 characters)
Polish   lacks  6: Ą ą Ę ę Ł ł
Czech    lacks  2: ď ť
```

Mira writes back to the publisher before lunch: yes, Plum does Turkish, all four `i` letters included.

The German line is worth a second look. `ẞ` is the capital sharp s, a letter German spelling admitted in 2017. Plenty of fonts lack it and German has been set without it for centuries. Whether "lacks 1" means "can't write German" is a judgment, and the script doesn't make it. It reports what's missing from the list it was given.

Polish and Czech are nearly there, which is Part 3's work showing. Polish lacks the four letters with an ogonek, which Mira hasn't drawn for the practice font, and the `Ł` and `ł`, whose stroke isn't an accent at all. Czech lacks `ď` and `ť`. They take the apostrophe-like caron that stopped Mira at the `ľ` in chapter 57. Without Part 3's glyphs the two lines would read `lacks 16` and `lacks 18`.

## The whole script

```python
#FLM: Language Report
# Reads languages.txt from the font's folder and says, for each language,
# which of its characters the current font can't type.
from pathlib import Path

import halfmoon
from fly import fl

BASIC = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
FILE_NAME = "languages.txt"


def read_languages(path):
    languages = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            name, letters = line.split(":", 1)
            languages[name.strip()] = set(letters) - {" "}
    return languages


def report(languages, have):
    for name, extra in languages.items():
        need = set(BASIC) | extra
        missing = sorted(need - have)
        if missing:
            print(f"{name:<9}lacks {len(missing):>2}: {' '.join(missing)}")
        else:
            print(f"{name:<9}complete ({len(need)} characters)")


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    path = Path(font.path).parent / FILE_NAME
    if not path.exists():
        halfmoon.tell(f"I can't find {FILE_NAME} next to the font.")
        return
    languages = read_languages(path)
    have = {chr(code) for glyph in font.glyphs for code in glyph.unicodes}
    report(languages, have)


main()
```

Save it as `language_report.py`.

Notes on the listing.

The script changes nothing in the font, so it has no dry run and no Undo step. You can run it on any font at any time.

`path.exists()` asks whether the file is there before `open` tries it. Without the test, a missing file gives `FileNotFoundError` and a traceback, which is accurate and no help to Ines. The message box tells her what to do.

`sorted(need - have)` turns the set into a list in a fixed order. A set has no order of its own, and a report that shuffles its letters from run to run is hard to compare with last month's.

`BASIC` is a string, not a set, and `set(BASIC)` converts it where it's used. It could be built once at the top. Fifty-two characters, six times: nobody will notice.

## Break it on purpose

The file writes both cases out. That looks like wasted typing. Chapter 25 got the capitals for free with `upper()`. Try it on Turkish:

```python
small = "çğıöşü"
print(small.upper())
```

```text
ÇĞIÖŞÜ
```

Look at the third letter. The small dotless `ı` became a plain capital `I`, which is right: in Turkish the dotless pair is `I` and `ı`. The trouble is the letter that isn't there. Turkish also has a dotted capital, `İ`, whose small partner is the plain `i`. Python's `upper()` follows the rule that fits most languages and turns `i` into `I`, so no amount of uppercasing a Turkish alphabet will ever produce `İ`.

A need built that way never asks for `İ`. Hold it against a font that lacks the letter:

```python
need = set(small) | set(small.upper())
pretend = have - {"İ"}
print(sorted(need - pretend))
```

```text
[]
```

Nothing missing, says the script, about a font that can't set the word İstanbul. A wrong "complete" is worse than a wrong "lacks", because nobody checks good news.

German has the same trap from the other side: `"ß".upper()` gives `SS`, two letters, and never `ẞ`.

So the file spells out every letter, and the script doesn't derive one case from the other.

## What the report can't tell you

Having a glyph for every letter is where language support starts. The glyphs also have to be drawn right, spaced, and kerned against their neighbors. A font can pass this report with an `ğ` whose breve crashes into the line above.

The file is short. Fly has a similar set of lists built in, eight of them, and there's no larger collection in any of the packages I could read. For a serious answer about a language you don't speak, ask somebody who reads it, and put what they tell you in the file.

## What you learned

Data that changes, or that other people look after, belongs in a file and not in the script. A line of text becomes structured data with a `split`, a `strip` and one conversion, here to a set. A dictionary can hold sets, and a comprehension in curly braces builds one. Letter case isn't the same in every language, so a script shouldn't work out one case from the other when a person can write both down.

## Try it yourself

1. Add a line for Welsh: `ÂÊÎÔÛŴŶ âêîôûŵŷ`. Run the report. Then add the grave and dieresis letters you can find in Plum from chapter 82's "eight not in the table" and see whether the count of characters goes up while the font stays complete.
2. Give the report a second kind of line: a font that lacks more than four letters of a language probably never meant to support it. Print `not attempted` for those, and the full list only for the near misses. Which of the six languages change their line?
3. Turn the question round. For one language, print what the font has that neither `BASIC` nor that language's extras need, as chapter 25 did with `have - need`. Most of it will be figures and punctuation. Use `c.isalpha()` in a comprehension to keep only the letters. It's a method every string has, and it answers `True` when the string is made of letters and nothing else. What's left tells you which other languages Sora Sagano had in mind.

## Next

The Font window shows the Greek import in the order it arrived, which is no order at all. Chapter 86 sorts glyphs by more than one thing at a time: kind first, then name.
