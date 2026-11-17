---
this_file: src_docs/md/part6-families/118-fonttools-says-hello.md
---

# 118. A second opinion from fontTools

Wednesday of week twenty-three. The publisher's IT department runs every incoming font through a checking tool. Its report on Plum reaches Mira with one line marked: "237 characters. Your glyph sheet says 235. Which is it?"

Every number this book has printed came from FontLab, about the font as it sits in FontLab. The publisher doesn't have that font. They have five OTF files, and a file is what FontLab's export made of the font, which is a different thing. Mira has never looked inside one.

There's a Python package that reads font files with no font editor involved. It's called fontTools, and most of the type trade's checking tools are built on it, very likely the publisher's too. Today you open the exported files with it and hold what they say against what the open font says.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, and `halfmoon.py` with chapter 116's `latest_export`.
- The export folder for version 1.002 with five OTF files in it.

I couldn't run the code in FontLab 9, and I don't have files that FontLab exported. I built five small OTF files with fontTools itself, with the reader's glyph names, characters and features, and ran the script on those in plain Python. So the fontTools calls below ran for real. What FontLab's export puts in a file is the part I haven't seen.

## Step 1: Which fontTools

This is the first package in the book that Fly doesn't hand you, so the import needs a thought.

FontLab 9 ships a copy of fontTools for its own use, under the name `fontlab_private.fontTools`. A copy you install yourself goes by the plain name `fontTools`. The scripts I've read from FontLab's own people try one and fall back to the other, and so will yours:

```python
try:
    from fontTools.ttLib import TTFont
except ImportError:
    from fontlab_private.fontTools.ttLib import TTFont

print(TTFont)
```

```text
<class 'fontTools.ttLib.ttFont.TTFont'>
```

`try` and `except` are chapter 19's, and `ImportError` is the error chapter 4 showed you when a name couldn't be imported. Put together they say: use your own copy if there is one, and FontLab's if not. If you see `fontlab_private` in the printed line, you're on FontLab's copy, and that's fine for everything in this chapter.

!!! note "Installing your own"
    FontLab's copy is an older one, kept for FontLab, and "private" is a fair warning that it may change. A newer copy goes into the `site-packages` folder where `halfmoon.py` lives (chapter 33), and the usual tool for that is `pip`, run in a terminal with its `--target` option pointing at that folder. I haven't done this with FontLab 9, so I'm not printing a command I can't vouch for. Nothing here needs it.

## Step 2: Open a file

```python
from pathlib import Path

path = Path("/Users/mira/Halfmoon/exports/2026-12-10-v1.002/otf/GGPlum-Regular.otf")
with TTFont(path) as ttfont:
    print(sorted(ttfont.keys()))
```

```text
['CFF ', 'GPOS', 'GSUB', 'GlyphOrder', 'OS/2', 'cmap', 'head', 'hhea', 'hmtx', 'maxp', 'name', 'post']
```

Use your own path. `with` is chapter 26's: the file is open for the indented lines and closed after them.

A font file is a set of tables, each with a four-character name, and this is the list. Your file will have more of them than my small ones do. The ones worth knowing today:

- `name` holds the texts: family name, style name, version, copyright.
- `cmap` is the map from characters to glyphs. It's the file's form of every glyph's Unicode values.
- `CFF ` holds the outlines of an OTF as the curves you drew. A TTF has `glyf` in its place.
- `hmtx` holds the widths.
- `GSUB` holds the features that swap glyphs, such as `liga` and `smcp`. `GPOS` holds the ones that move them, such as `kern`.
- `GlyphOrder` isn't a table. It's fontTools' own list of the glyph names.

Ask a few questions:

```python
with TTFont(path) as ttfont:
    print(ttfont["name"].getDebugName(5))
    print(len(ttfont.getGlyphOrder()))
    print(len(ttfont.getBestCmap()))
    print(ttfont["head"].unitsPerEm)
```

```text
Version 1.002
274
237
1000
```

Square brackets with a table's name give you the table. In the `name` table every text has a number, and 5 is the version. `getBestCmap` returns a dict from character number to glyph name, and its length is the IT department's 237.

## Step 3: The mistake

Mira's first script compared each file's characters with the font's. For the font's side she took the line from chapter 116:

```python
codes = {glyph.unicode for glyph in font.glyphs if glyph.unicode is not None}
```

and the script said, for every one of the five files:

```text
GGPlum-Bold.otf       Version 1.002   274 glyphs  237 characters   9 features
  in the file only: U+00A0 U+00AD
```

It reported two characters in the file that the font doesn't have. That would be alarming, since an export shouldn't invent characters.

It didn't invent them. U+00A0 is the no-break space and U+00AD is the soft hyphen. You gave them to `space` and `hyphen` yourself in chapter 84, as second values. `glyph.unicode` is the first value only, and chapter 84 said to use `glyph.unicodes`, the list, when all of them matter.

So both counts were right. Plum has 235 glyphs that carry a character, and 237 characters, because two glyphs carry two each. The glyph sheet counted glyphs and the checking tool counted characters. Mira can write that back in one sentence.

The script's alarm was false, and the fault was in the script. When a file and a font disagree, there are three suspects: the export, the font, and the code that compared them. Look at the comparing code first, since it's the newest of the three and the least tested. The cure:

```python
def font_codes(font):
    codes = set()
    for glyph in font.glyphs:
        for code in glyph.unicodes:
            codes.add(code)
    return codes
```

## The whole script

```python
#FLM: Inspect Export
# Opens every exported .otf of the current version with fontTools and
# holds what the file says against the open font. Changes nothing.
import fly.ap.core.scripting as scripting
import halfmoon
from fly import fl

try:
    from fontTools.ttLib import TTFont
except ImportError:
    from fontlab_private.fontTools.ttLib import TTFont


def features(ttfont):
    tags = set()
    for tag in ["GSUB", "GPOS"]:
        if tag in ttfont:
            for record in ttfont[tag].table.FeatureList.FeatureRecord:
                tags.add(record.FeatureTag)
    return sorted(tags)


def read_file(path):
    with TTFont(path) as ttfont:
        return {"version": ttfont["name"].getDebugName(5),
                "glyphs": len(ttfont.getGlyphOrder()),
                "codes": set(ttfont.getBestCmap()),
                "curves": "CFF " in ttfont,
                "features": features(ttfont)}


def font_codes(font):
    codes = set()
    for glyph in font.glyphs:
        for code in glyph.unicodes:
            codes.add(code)
    return codes


def code_list(codes):
    return " ".join([f"U+{code:04X}" for code in sorted(codes)])


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    folder = halfmoon.latest_export(font, package)
    if folder is None:
        halfmoon.tell("No export folder for this version. Export first.")
        return
    info = package.info
    wanted = f"Version {info.versionMajor}.{info.versionMinor:03d}"
    codes = font_codes(font)
    problems = 0
    shown = None
    files = sorted(folder.rglob("*.otf"))
    for path in files:
        try:
            said = read_file(path)
        except Exception as problem:
            print(f"{path.name}: DID NOT OPEN: {type(problem).__name__}: {problem}")
            problems += 1
            continue
        print(f"{path.name:<22}{said['version']:<15}{said['glyphs']:>4} glyphs"
              f"{len(said['codes']):>5} characters{len(said['features']):>4} features")
        shown = said["features"]
        if wanted not in said["version"]:
            print(f"  says {said['version']}, the font says {wanted}")
            problems += 1
        if not said["curves"]:
            print("  has no CFF table")
            problems += 1
        if codes - said["codes"]:
            print(f"  lost on the way out: {code_list(codes - said['codes'])}")
            problems += 1
        if said["codes"] - codes:
            print(f"  in the file only: {code_list(said['codes'] - codes)}")
            problems += 1
    print(f"{len(files)} files, {problems} problems.")
    if shown is not None:
        print("Features in the last file:", " ".join(shown))


main()
```

Save it as `inspect_export.py` and run it:

```text
GGPlum-Bold.otf       Version 1.002   274 glyphs  237 characters   9 features
GGPlum-Light.otf      Version 1.002   274 glyphs  237 characters   9 features
GGPlum-Medium.otf     Version 1.002   274 glyphs  237 characters   9 features
GGPlum-Regular.otf    Version 1.002   274 glyphs  237 characters   9 features
GGPlum-SemiBold.otf   Version 1.002   274 glyphs  237 characters   9 features
5 files, 0 problems.
Features in the last file: cpsp dnom frac kern liga numr smcp ss01 zero
```

That's what my stand-in files gave. Yours are real exports, and I expect the first run to show you something I couldn't foresee. Read every line it prints as a question about the export, not as a verdict.

Notes on the listing.

`read_file` opens a file, takes five facts and closes it. Nothing from fontTools leaves the function. What comes out is a plain dict of text, numbers, a set and a list, which the rest of the script can use with the file long shut.

`features` is the one place that digs. Inside the `GSUB` and `GPOS` tables the features sit in a list of records, each with a `FeatureTag`. The same tag can occur several times, once for each script and language, which is why the tags go into a set. I counted nine: the eight features you wrote in Part 5, and `kern`. You never wrote a `kern` feature. An export builds it from the kerning pairs, so I've assumed FontLab's does. If your line shows eight, the kerning didn't reach the file, and that's worth a morning.

The two differences between sets are chapter 117's, pointing in two directions. A character the font has and the file doesn't was lost on the way out. A character only the file has came from somewhere, and you now know to suspect your own script first.

`wanted not in said["version"]` uses `in` and not `==`, because some exports put more after the number, a build date or the name of the tool.

The loop keeps going when a file won't open, with chapter 100's `except Exception` and a line that says so. One bad file shouldn't hide the other four.

The script doesn't compare the glyph count with the font's. I don't know whether FontLab adds or drops glyphs at export, so there the script prints and leaves the judging to you.

## Break it on purpose

In `read_file`, take the space out of the table name, so it reads `"CFF" in ttfont`. Run:

```text
GGPlum-Bold.otf       Version 1.002   274 glyphs  237 characters   9 features
  has no CFF table
```

and the same for every file, ending in `5 files, 5 problems.` Table names have four characters, always. `CFF` has three letters, so its fourth character is a space, and the space is part of the name. Python doesn't complain about `"CFF" in ttfont`. It's a fair question with the answer no. Ask for the table itself, `ttfont["CFF"]`, and you get `KeyError: 'CFF'`. Put the space back.

Now make a text file with three or four letters in it, name it `GGPlum-Test.otf`, and put it in the `otf` folder. Run:

```text
GGPlum-Test.otf: DID NOT OPEN: TTLibError: Not a TrueType or OpenType font (not enough data)
```

The wording is from my copy of fontTools, and FontLab's older one may phrase it differently. A longer text file gets a different reason in the brackets, `bad sfntVersion`, because fontTools then has enough to read the first four characters and dislike them. The file name says OTF and the contents don't, and fontTools goes by the contents. The count at the end reads `6 files, 1 problems.` Delete the test file before you forget it's there, or Friday's build will ship it.

## What you learned

A font file is a set of tables with four-character names, and fontTools opens it as something like a dict of them: `name` for the texts, `cmap` for the characters, `CFF ` for the outlines, `GSUB` and `GPOS` for the features. A package Fly doesn't provide is imported with `try` and `except ImportError`, so the script works with your own copy or FontLab's. The exported file is a second witness to what the font holds, and it counts characters where FontLab's glyph list counts glyphs. When the file and the font disagree, check the code that compared them before blaming either.

## Try it yourself

1. Print the family name and the style name of each file. They're texts 1 and 2 in the `name` table. Does each file's style name match the last part of its file name?
2. `ttfont["hmtx"]["zero"]` gives a pair, the width and the left sidebearing. Print the width of `zero` in each of the five files and hold the three masters' values against chapter 104's table.
3. The folder has a `ttf` subfolder too. Make the script look at both kinds, and expect `glyf` where an OTF has `CFF `.

## Next

There's a script to check, one to make the folder, two to proof, one to compare and one to inspect. On Friday somebody has to remember to run them, in the right order. Chapter 119 writes the script that remembers, and Oskar's sheet loses its last line.
