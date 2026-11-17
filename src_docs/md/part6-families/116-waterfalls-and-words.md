---
this_file: src_docs/md/part6-families/116-waterfalls-and-words.md
---

# 116. Waterfalls and words

Monday of week twenty-three. The art director liked the glyph sheet. Her production editor has a different question. "The dictionary is set at 9 point. Does the Light hold up at 9? Send me text, not an alphabet."

Friday's page showed every glyph alone, and nobody reads a typeface that way. Today's page sets a word and a paragraph in each of the five styles, at a ladder of sizes from 9 point to 36. Type people call the ladder a waterfall.

That makes five styles, nine lines each, and every line is the same piece of HTML with three things changed. Building those with f-strings and plus signs, as chapter 115 did, would work, and you'd lose your place in the quote marks. Python has a tool for text with holes in it.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The export folder for version 1.002 with five OTF files in it.
- `proof_html.py` from chapter 115, to borrow from.

I couldn't run the code in FontLab 9, and I haven't seen the page in a browser with the real fonts. I ran the script in plain Python against a stand-in for the reader's font and a folder of dummy font files, and read the page it wrote as text.

## Step 1: A template

```python
from string import Template

LINE = Template("$style at ${size}pt")
print(LINE.substitute(style="Light", size=9))
print(LINE.substitute(style="Bold", size=36))
```

```text
Light at 9pt
Bold at 36pt
```

A `Template` is a string with named holes. A hole is a dollar sign and a name. `substitute` fills the holes from the names you give it and returns the finished text. The template itself doesn't change, so you can fill it as often as you like.

The braces in `${size}pt` mark where the name ends. Without them Python would look for a hole called `sizept`.

Why not an f-string? An f-string is filled once, at the line where it's written. A template is written in one place and filled in another, many times. And a template doesn't care about curly braces, so a style sheet can sit inside one as it is, with none of chapter 88's doubling.

## Step 2: Borrow three functions from chapter 115

This script needs three functions you already have: `key` from chapter 112, and `latest_export` and `font_file` from chapter 115. Copy them in, unchanged, so this script runs by itself. They need `Path`, so the script's imports gain this line:

```python
from pathlib import Path
```

And here are the three:

```python
def key(text):
    return "".join([c for c in text.lower() if c.isalnum()])


def latest_export(font, package):
    info = package.info
    ending = f"-v{info.versionMajor}.{info.versionMinor:03d}"
    exports = Path(font.path).parent / "exports"
    if not exports.exists():
        return None
    folders = [f for f in sorted(exports.iterdir()) if f.name.endswith(ending)]
    return folders[-1] if folders else None


def font_file(folder, family, style):
    for path in sorted(folder.rglob("*.otf")):
        if key(path.stem) == key(family + style):
            return path
    return None
```

That makes three copies of `key` in three scripts. Chapter 114 said a copy is two things to mend. It is, but each script still runs on its own, and `key` is one line that hasn't changed since chapter 112.

## Step 3: The mistake

Mira's first sample paragraph came from the publisher's own style guide:

```python
TEXT = ("The dictionary is set in two columns on a page of 148 × 210 mm. "
        "Headwords are bold; senses are numbered 1, 2, 3; quotations "
        "follow in a lighter weight, with the author's name and a date.")
```

She made the page, printed the PDF and looked it over at arm's length. It was handsome. She sent it.

The production editor circled one character ten times: the `×` between 148 and 210, in typewriter letters, in every paragraph. Plum has no multiplication sign. The alarm from chapter 115 did its job, and it did it in front of the client.

The page can only show the fault after the fact. The script can know beforehand, because the open font knows which characters it has:

```python
def absent(font, text):
    codes = {glyph.unicode for glyph in font.glyphs if glyph.unicode is not None}
    return sorted({c for c in text if ord(c) not in codes})
```

The first line is a set of every Unicode value in the font, built in the manner of chapter 37 with curly braces, which makes a set and not a list. The second walks the text one character at a time. `ord` is chapter 23's: the number behind a character. A character whose number isn't in the font goes into another set, so each is reported once however often it occurs.

With the `×` in the text:

```text
The font has no glyph for: × (U+00D7). Change the text.
```

Now there's a decision. The script could draw the page anyway, or it could stop. It stops. A proof with a stranger's letters in it wastes the reader's attention on something that isn't the typeface. Mira changes the sign to the word "by". Whether Plum should have a multiplication sign is a fair question for another day, and exercise 3 keeps a note of it.

## The whole script

```python
#FLM: Proof Text
# Writes a web page that sets words and a paragraph in every exported
# style, at a ladder of sizes. Changes nothing in the font.
import html
from pathlib import Path
from string import Template

import fly.ap.core.scripting as scripting
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


# Chapter 39's tell, written out again so this script runs by itself.
def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


STYLES = ["Light", "Regular", "Medium", "SemiBold", "Bold"]
SIZES = [9, 10, 12, 14, 18, 24, 36]
READING = [9, 11]
WORDS = "Hamburgefonstiv 0123456789"
TEXT = ("The dictionary is set in two columns on a page of 148 by 210 mm. "
        "Headwords are bold; senses are numbered 1, 2, 3; quotations "
        "follow in a lighter weight, with the author's name and a date.")
PAGE_NAME = "proof-text.html"

FACE = Template('@font-face { font-family: "$family"; src: url("$address"); }')
LINE = Template('<p style="font-family: \'$family\', monospace; '
                'font-size: ${size}pt; margin: 0.2em 0">$text</p>')
PAGE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>$title</title>
<style>
$faces
body { font-family: sans-serif; margin: 2em; max-width: 40em; }
h2 { font-size: 10pt; color: #555; margin-top: 3em; }
</style>
</head>
<body>
<h1>$title</h1>
$blocks
</body>
</html>
""")


def key(text):
    return "".join([c for c in text.lower() if c.isalnum()])


def latest_export(font, package):
    info = package.info
    ending = f"-v{info.versionMajor}.{info.versionMinor:03d}"
    exports = Path(font.path).parent / "exports"
    if not exports.exists():
        return None
    folders = [f for f in sorted(exports.iterdir()) if f.name.endswith(ending)]
    return folders[-1] if folders else None


def font_file(folder, family, style):
    for path in sorted(folder.rglob("*.otf")):
        if key(path.stem) == key(family + style):
            return path
    return None


def absent(font, text):
    codes = {glyph.unicode for glyph in font.glyphs if glyph.unicode is not None}
    return sorted({c for c in text if ord(c) not in codes})


def block(style, family):
    lines = [f"<h2>{style}</h2>"]
    for size in SIZES:
        lines.append(LINE.substitute(family=family, size=size,
                                     text=html.escape(WORDS)))
    for size in READING:
        lines.append(LINE.substitute(family=family, size=size,
                                     text=html.escape(TEXT)))
    return "\n".join(lines)


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    lacking = absent(font, WORDS + TEXT)
    if lacking:
        listed = ", ".join([f"{c} (U+{ord(c):04X})" for c in lacking])
        tell(f"The font has no glyph for: {listed}. Change the text.")
        return
    folder = latest_export(font, package)
    if folder is None:
        tell("No export folder for this version. Export first.")
        return
    faces = []
    blocks = []
    for style in STYLES:
        source = font_file(folder, package.info.familyName, style)
        if source is None:
            print(f"No {style} .otf in {folder.name}. Left out.")
            continue
        family = f"Proof {style}"
        address = source.relative_to(folder).as_posix()
        faces.append(FACE.substitute(family=family, address=address))
        blocks.append(block(style, family))
    title = f"{package.info.familyName}, {folder.name}"
    text = PAGE.substitute(title=html.escape(title), faces="\n".join(faces),
                           blocks="\n".join(blocks))
    target = folder / PAGE_NAME
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)
    lines = len(blocks) * (len(SIZES) + len(READING))
    print(f"{len(blocks)} styles, {lines} lines of text.")
    print(f"Wrote {target}")


main()
```

Save it as `proof_text.py` and run it:

```text
5 styles, 45 lines of text.
Wrote /Users/mira/Halfmoon/exports/2026-12-10-v1.002/proof-text.html
```

Open the page in a browser. What you should find, and what I haven't seen: five grey headings, and under each a word growing from small to large, then the paragraph twice.

Notes on the listing.

There are three templates, and each is one level of the page. `FACE` is one font rule. `LINE` is one line of type. `PAGE` is the whole page, with two holes, `$faces` and `$blocks`, that take many lines joined into one string. The page is built from the inside out: lines into blocks, blocks into the page. Look at `PAGE` and you can see the shape of the finished file, which chapter 115's list of little strings never let you do.

Each style gets a family name of its own, `Proof Light`, `Proof Bold` and so on, and its own `@font-face` rule. That's the plainest way to be sure which file a line is set in. `LINE` uses single quotes around the family name because the whole `style="..."` is in double quotes. The backslashes before them are there because the Python string itself is in single quotes. `\'` puts a quote mark in the text without ending the string.

A style whose file is missing is left out with a printed line, and the loop goes on, as chapter 113's did for a font that wouldn't open. The last line of output counts the styles that made it. If it says 4, read upward.

`html.escape` is applied to the sample text and the title, the things a person types. The template doesn't do it for you.

`absent` asks the open font, and the page shows the exported one. They should hold the same characters. If they don't, the typewriter letters are still there as the second line of defence.

## Reading the page

The sizes are in points, and a point on a screen isn't a point on paper. A browser's "9pt" depends on the screen and the zoom. For the production editor's question, print the page, or save the PDF and print that at full size, and read the 9 point paragraph on paper at the distance you'd hold a dictionary.

Then look at these things. In the waterfall, find the smallest size at which the Light's thin strokes still look continuous. In the paragraphs, compare the Light with the Regular at 9 point: the figures, the semicolons, the apostrophe in "author's". Check that Medium and SemiBold sit visibly between their neighbours. Chapter 106 worked their shapes out by arithmetic, and this is the first time anyone has read them.

The script can't answer the editor's question. It gives you a page on which a person can.

## Break it on purpose

In `block`, misspell a name in the first `substitute`: write `sise=size`. Run:

```text
KeyError: 'size'
```

`substitute` insists that every hole is filled. The template has a hole called `size`, nothing by that name arrived, and Python refuses to write a page with `${size}` printed in the middle of it. Put the name right.

Templates have a gentler method, `safe_substitute`, which leaves unfilled holes as they are. For a proof that goes to a client it's the wrong tool, since it turns a loud error into a quiet blemish.

One more. A dollar sign followed by a digit isn't a hole and isn't allowed either: `Template("costs $9").substitute()` stops with an error that begins `ValueError: Invalid placeholder in string`. In the template itself, write a real dollar as `$$`. In the text you pass in, a dollar is only a character, and you can write prices freely.

## What you learned

A `Template` is text with `$name` holes that `substitute` fills, and it can be filled many times, which suits a page made of repeating blocks. Templates nest by joining the small filled pieces and passing the result into a hole of the larger one. A script should check its sample text against the font's characters before it draws anything, because a missing character on a proof is seen by the client first. Sizes on a screen are not sizes on paper, so a question about 9 point is answered with a printed page and a pair of eyes.

## Try it yourself

1. Add a line of capitals and a line of figures with punctuation to each block, each from its own constant.
2. Put the sample text in a file, `proof-text.txt`, beside the font, and read it with chapter 26's `open` when the file exists. Keep `TEXT` as the fallback.
3. Have the script write the characters it found absent to `wanted-glyphs.txt`, one to a line with the code, before it stops. Over a few months that file becomes a list of what clients needed and Plum didn't have.

## Next

The client has seen the glyphs and read the text. Their next message is shorter: "What changed since the version you sent last week?" Chapter 117 opens two versions of a font and lists the differences.
