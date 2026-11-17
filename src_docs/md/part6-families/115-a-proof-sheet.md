---
this_file: src_docs/md/part6-families/115-a-proof-sheet.md
---

# 115. A proof sheet

Friday of week twenty-two. The font is version 1.002 now. Mira ran `bump_version.py` yesterday, exported the five styles again, and `export_family.py` said `10 wanted, 10 there, 0 missing.`

The publisher's art director writes: "Before I sign anything, send me a PDF with every glyph on it. Big. With the names."

FontLab can print glyph sheets, and for one font on one day that's the way to do it. Halfmoon will be asked for this sheet every time a font changes. So today a script writes the sheet as a web page. A browser shows it, and the browser's own **Print** command turns it into a PDF.

A point to settle first. The page doesn't show the font you have open in FontLab. It shows the exported file, the one the client will install. If the export went wrong, the page shows it going wrong, and that's what a proof is for.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, and `halfmoon.py`.
- An export folder for the current version with the OTF files in it, from chapters 111 and 112.
- A web browser.

I couldn't run the code in FontLab 9, and I haven't looked at the page in a browser with the real exported font. I ran the script in plain Python against a stand-in for the reader's font and an export folder of dummy files, and I read the page it wrote as text.

## Step 1: A page is text

A web page is a text file whose name ends in `.html`. You've written text files since chapter 26. Inside, the words are wrapped in tags, which are names in angle brackets. A tag opens, `<h1>`, and closes with a slash, `</h1>`:

```python
from pathlib import Path

lines = ["<!DOCTYPE html>",
         "<html>",
         "<body>",
         "<h1>Hello from Halfmoon</h1>",
         "</body>",
         "</html>"]
target = Path.home() / "hello.html"
with open(target, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(target)
```

Run it, find `hello.html` in your home folder, and drag it into a browser window. You get a heading in large type. `"\n".join(lines)` is the join you've used since chapter 25, with a line break as the glue.

That's the whole method. The script builds a list of lines, joins them and writes them. Everything else today is deciding what the lines say.

## Step 2: Tell the page which font

A page names its font in a block of rules called a style sheet. Here's the one the script will use, kept in a constant:

```python
CSS = """
@font-face { font-family: "Proof"; src: url("FONTFILE"); }
body { font-family: sans-serif; margin: 2em; }
.cell { display: inline-block; width: 6em; margin: 0.3em; text-align: center; }
.glyph { display: block; font-family: "Proof", monospace; font-size: 48px; }
.name, .code { display: block; font-size: 10px; color: #555; }
"""
```

The triple quotes are chapter 98's. This isn't Python inside them, it's the browser's language for looks, and you need to read only two lines of it.

The first says: there's a font I'll call "Proof", and its file is at `FONTFILE`. That word is a placeholder of mine. The script swaps it for the real address with chapter 30's `replace`. I could have used an f-string, but a style sheet is full of curly braces and every one would need doubling, as in chapter 88.

The fourth line says: anything marked `glyph` is set in "Proof" at 48 pixels, and if that fails, in `monospace`. The fallback is deliberate. A browser that can't load a font says nothing. It quietly uses another font, and you'd be looking at a handsome proof of the wrong typeface. Typewriter letters are an alarm you can't miss. They appear if the file didn't load, and also for any single character the font lacks.

The address is relative. The script writes the page into the export folder itself, so the font is at `otf/GGPlum-Regular.otf` from where the page sits. Send the whole folder and the page still works on the client's computer.

## Step 3: One cell for each glyph

Each glyph gets a small box: the character large, then its name and code.

```python
import html


def cell(glyph):
    character = html.escape(chr(glyph.unicode))
    return (f'<div class="cell"><span class="glyph">{character}</span>'
            f'<span class="name">{glyph.name}</span>'
            f'<span class="code">U+{glyph.unicode:04X}</span></div>')
```

`chr` and `:04X` are chapter 23's: a number to a character, and a number to four hexadecimal digits. The strings use single quotes outside because the HTML has double quotes inside. Two strings side by side in brackets are joined by Python into one.

`html.escape` is new. Two of Plum's glyphs are `less` and `ampersand`, and their characters, `<` and `&`, mean something to a browser: the start of a tag and the start of a code. `html.escape` rewrites them as `&lt;` and `&amp;`, which a browser shows as the plain characters. Every other character passes through as it is. Browsers are forgiving about a stray `<`, but a proof shouldn't depend on forgiveness.

## Step 4: The mistake

Mira's first version looped like this:

```python
cells = []
for glyph in font.glyphs:
    if glyph.unicode is not None:
        cells.append(cell(glyph))
print(f"{len(cells)} glyphs.")
```

```text
235 glyphs.
```

The `if` has to be there, since `chr(None)` is an error. She printed the page to a PDF and sent it.

The reply took ten minutes. "Where are the small caps?"

The font has 274 glyphs. The page showed 235. The other 39 have no Unicode value: the small capitals, the ligatures, the slashed zero, the numerators. A page shows characters, and those glyphs have no character of their own. A reader reaches them through features.

The script wasn't wrong about any glyph it showed. It left some out, printed a count that sounded complete, and nobody compared 235 with 274. You've met this before, in chapter 113's pattern that found 31 files of 40. A filter needs two counts: what passed and what didn't.

So the leftovers go on the page too, by name, under their own heading, and the script prints both numbers. Showing them as shapes means switching features on in the page, which is exercise 3.

## The whole script

```python
#FLM: Proof HTML
# Writes a web page that shows every glyph of one exported font file.
# Reads the open font for names and codes. Changes nothing in the font.
import html
from pathlib import Path

import fly.ap.core.scripting as scripting
import halfmoon
from fly import fl

STYLE = "Regular"
PAGE_NAME = "proof-glyphs.html"

CSS = """
@font-face { font-family: "Proof"; src: url("FONTFILE"); }
body { font-family: sans-serif; margin: 2em; }
.cell { display: inline-block; width: 6em; margin: 0.3em; text-align: center; }
.glyph { display: block; font-family: "Proof", monospace; font-size: 48px; }
.name, .code { display: block; font-size: 10px; color: #555; }
"""


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


def cell(glyph):
    character = html.escape(chr(glyph.unicode))
    return (f'<div class="cell"><span class="glyph">{character}</span>'
            f'<span class="name">{glyph.name}</span>'
            f'<span class="code">U+{glyph.unicode:04X}</span></div>')


def page(title, address, cells, leftovers):
    lines = ["<!DOCTYPE html>", '<html lang="en">', "<head>",
             '<meta charset="utf-8">', f"<title>{html.escape(title)}</title>",
             "<style>" + CSS.replace("FONTFILE", address) + "</style>",
             "</head>", "<body>", f"<h1>{html.escape(title)}</h1>"]
    lines += cells
    lines.append(f"<h2>No character of their own: {len(leftovers)}</h2>")
    lines.append("<p>" + " ".join(leftovers) + "</p>")
    lines += ["</body>", "</html>"]
    return "\n".join(lines) + "\n"


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    folder = latest_export(font, package)
    if folder is None:
        halfmoon.tell("No export folder for this version. Export first.")
        return
    source = font_file(folder, package.info.familyName, STYLE)
    if source is None:
        halfmoon.tell(f"No {STYLE} .otf in {folder.name}.")
        return
    cells = []
    leftovers = []
    for glyph in font.glyphs:
        if glyph.unicode is None:
            leftovers.append(glyph.name)
        else:
            cells.append(cell(glyph))
    address = source.relative_to(folder).as_posix()
    text = page(f"{source.stem}, {folder.name}", address, cells, leftovers)
    target = folder / PAGE_NAME
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Proof of {address}")
    print(f"{len(cells)} glyphs with a character, {len(leftovers)} without.")
    print(f"Wrote {target}")


main()
```

Save it as `proof_html.py` and run it:

```text
Proof of otf/GGPlum-Regular.otf
235 glyphs with a character, 39 without.
Wrote /Users/mira/Halfmoon/exports/2026-12-10-v1.002/proof-glyphs.html
```

Your counts, file names and path will be your own. Drag the page into a browser. What you should see, and what I haven't seen: a heading, then rows of boxes, each with a large character in Plum and two small grey lines beneath it, then a second heading and a paragraph of names. To make the PDF, use the browser's **Print** command and choose to save as PDF.

Notes on the listing.

`latest_export` doesn't use today's date. The export was made yesterday, so chapter 111's folder for today doesn't exist. It gathers the folders whose names end in this version and takes the last. The names begin with the date written year first, so sorted order is date order. `folders[-1]` is the last item, by chapter 10's counting from the end.

`font_file` reuses chapter 112's `key`, which squeezes a name down to its letters and digits, so `GGPlum-Regular` and `GG Plum` plus `Regular` meet. I've copied `key` into this script, and chapter 114 said a copy is two things to mend. That's fair. If a third script wants it, it belongs in `halfmoon.py`.

`as_posix()` writes a path with forward slashes whatever the computer. Web addresses always use forward slashes, and on Windows a plain `str` of the path wouldn't.

`<meta charset="utf-8">` tells the browser how the file's bytes spell characters. It matches the `encoding="utf-8"` in `open`. Leave either out and `é` may arrive as two characters of nonsense.

`lines += cells` adds every item of one list to another. It's chapter 114's `+` for lists, written short.

The `space` glyph gets a box with nothing visible in it. That's a true picture of a space.

## Break it on purpose

Change `STYLE` to `"Semi Bold"`, with a gap in the middle, and run. The first line reads `Proof of otf/GGPlum-SemiBold.otf`. `key` threw the gap away on both sides of the comparison, so the spelling didn't matter.

Now change it to `"Black"`, a weight Plum doesn't have:

```text
No Black .otf in 2026-12-10-v1.002.
```

The script stopped before writing anything. Set `STYLE` back to `"Regular"`.

One more, and for this one I can only tell you what should happen. In the `page` function change `"FONTFILE"` to `"FONTFIL"`, so the swap finds nothing and the page asks for a font file that isn't there. Run, and reload the page. By the rules of style sheets every large character should now be in typewriter letters. That's the alarm from Step 2. If your page looks like that when you haven't broken anything, the browser couldn't load the font, and the first thing to check is that the page is still inside the export folder. Put the name back.

## What you learned

A web page is a text file of tags, so a script can write one with a list of lines, a join and chapter 26's `open`. `html.escape` makes any text safe to put between tags, and a relative address written with `as_posix()` keeps a page and its font together when the folder moves. A proof must show the exported file and must make a failure to load it obvious, which is why the fallback font is an ugly one. A filter that drops items needs both counts printed, or 204 of 258 looks like everything.

## Try it yourself

1. Add the family's version to the page's heading, read from `package.info` as in `latest_export`.
2. Make a second page for the Bold by turning `STYLE` and `PAGE_NAME` into arguments of a function, and call it for every style in a list.
3. A browser switches a feature on with a rule such as `font-feature-settings: "smcp";`. For each leftover whose name ends in `.sc`, add a cell that shows the letter before the dot with that rule in a `style="..."` attribute on the `span`. I haven't tested this. It works only if the features were compiled before the export, which chapter 93 left to a button.

## Next

Every glyph is on a page, one by one. Nobody reads a typeface one glyph at a time. Chapter 116 sets words and paragraphs at a ladder of sizes, and builds the page from a template.
