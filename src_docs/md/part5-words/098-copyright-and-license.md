---
this_file: src_docs/md/part5-words/098-copyright-and-license.md
---

# 98. Copyright and license

Wednesday of week nineteen. Ines forwards a paragraph from the publisher's contract. The delivered fonts must carry a copyright notice and a license statement "in the font data". She has the wording from the studio's lawyer, three sentences in an email, and she wants those three sentences in the fonts, letter for letter, in every release from now on.

Chapter 95's report has been saying `Copyright  <-- empty` since Friday. Today that line goes away.

Legal text is the one kind of text in a font that nobody at the studio is allowed to improve. So the script shouldn't hold it as a short string squeezed between quotation marks, where a person has to scroll sideways to proofread it. It should hold it the way the lawyer wrote it, line under line. Python has a string for that.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py`.

I couldn't run the code in FontLab 9. I ran the script in plain Python against a stand-in with Plum's legal fields, which are all empty except the designer's web address. The copyright field is one that Fly's guarded writer accepts. I haven't seen FontLab store the line.

One thing about the wording. In the story, Plum belongs to Halfmoon and the notice says so. Your practice font is GG Plum by Sora Sagano, released under CC0, which means its designer gave up the rights. A notice that claimed otherwise would be false, even in a practice copy, and false notices have a way of surviving into files that get passed on. The text in this chapter says what is true of the file on your disk.

## Step 1: A string with lines in it

Three quotation marks open a string that may run over several lines. Three more close it:

```python
COPYRIGHT = """
GG Plum by Sora Sagano.
Released under CC0 1.0 Universal: no rights reserved.
Practice copy for the Halfmoon book.
"""

print(COPYRIGHT)
```

```text

GG Plum by Sora Sagano.
Released under CC0 1.0 Universal: no rights reserved.
Practice copy for the Halfmoon book.

```

The text sits at the left edge of the script, as in the email. Ines can read it there without knowing any Python, and that's the reason to write it this way.

Look at the output, though. There's an empty line above the text and one below it.

## Step 2: The mistake

Mira hands the string to the writer as it is, in a dry run of her own, and looks at what she'd be storing:

```python
print(repr(COPYRIGHT))
print(len(COPYRIGHT))
```

```text
'\nGG Plum by Sora Sagano.\nReleased under CC0 1.0 Universal: no rights reserved.\nPractice copy for the Halfmoon book.\n'
116
```

`repr` shows the string as Python holds it, as it did in chapter 19. There are four `\n` in it. A triple-quoted string keeps every line break you typed, including the one straight after the opening quotes and the one before the closing quotes. What looked like three tidy lines is a string that starts and ends with a line break.

A copyright field is one line. Some programs show only the first line of it, and the first line here is empty. Chapter 95's check would also object: a line break counts as a space for `strip`, so `text_problems` would report `space at an end`.

The string is right for a person to read and wrong for a font to hold. Keep it, and convert it.

## Step 3: From lines to one line

`splitlines`, from chapter 87, cuts the text at its line breaks:

```python
print(COPYRIGHT.splitlines())
```

```text
['', 'GG Plum by Sora Sagano.', 'Released under CC0 1.0 Universal: no rights reserved.', 'Practice copy for the Halfmoon book.']
```

Four pieces, the first one empty. Strip each piece, drop the empty ones, and join the rest with single spaces:

```python
def one_line(text):
    lines = [line.strip() for line in text.splitlines()]
    return " ".join(line for line in lines if line)


print(repr(one_line(COPYRIGHT)))
print(len(one_line(COPYRIGHT)))
```

```text
'GG Plum by Sora Sagano. Released under CC0 1.0 Universal: no rights reserved. Practice copy for the Halfmoon book.'
114
```

`if line` is true for any string with something in it and false for the empty string, the same shortcut as `or ""` in chapter 95. The `strip` is there for the day the text moves. If you ever move the text into a function, your editor will indent it, and those spaces become part of every line. `one_line` removes them.

Why not `COPYRIGHT.replace("\n", " ")`? Try it. You get a space at each end and, if a line was indented, a run of spaces in the middle. Splitting and joining is the dependable way to tidy text. You'll use it again.

## Step 4: The fields a script can only read

Font Info has more legal fields than the copyright line: a trademark, a license text, a web address for the license, the designer's address, the manufacturer, and a four-letter vendor code. Fly's guarded writer accepts none of them. Ask it, and it answers `Unsupported Font Info field`, as it did for the PostScript name in chapter 95.

So the script reads them and tells you which are empty, and you fill those in by hand. A table again, and `getattr`:

```python
import fly.ap.core.scripting as scripting

READ_ONLY = {
    "trademark": "Trademark",
    "openTypeNameLicense": "License",
    "openTypeNameLicenseURL": "License URL",
    "openTypeNameDesignerURL": "Designer URL",
    "openTypeNameManufacturer": "Manufacturer",
    "openTypeOS2VendorID": "Vendor",
}

info = scripting.current_package().info
for key, label in READ_ONLY.items():
    value = getattr(info, key) or ""
    print(f"{label:<14}{value or '<-- empty'}")
```

```text
Trademark     <-- empty
License       <-- empty
License URL   <-- empty
Designer URL  http://www.dotcolon.net/
Manufacturer  <-- empty
Vendor        <-- empty
```

`value or '<-- empty'` prints the value if there is one and the marker if there isn't. You used the same turn with `or 'none'` in chapter 91.

These fields belong to the whole font, so there's no master to visit and no `finally`.

## The whole script

```python
#FLM: Legal Fields
# Reports the legal fields of Font Info and writes the copyright line
# from the text at the top of this script.
import halfmoon
from fly import fl
import fly.ap.core.scripting as scripting

DRY_RUN = True

COPYRIGHT = """
GG Plum by Sora Sagano.
Released under CC0 1.0 Universal: no rights reserved.
Practice copy for the Halfmoon book.
"""

READ_ONLY = {
    "trademark": "Trademark",
    "openTypeNameLicense": "License",
    "openTypeNameLicenseURL": "License URL",
    "openTypeNameDesignerURL": "Designer URL",
    "openTypeNameManufacturer": "Manufacturer",
    "openTypeOS2VendorID": "Vendor",
}


def one_line(text):
    lines = [line.strip() for line in text.splitlines()]
    return " ".join(line for line in lines if line)


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    info = package.info
    empty = 0
    for key, label in READ_ONLY.items():
        value = getattr(info, key) or ""
        if value == "":
            empty += 1
        print(f"{label:<14}{value or '<-- empty'}")
    print(f"{empty} of {len(READ_ONLY)} fields are empty. Fill them in File > Font Info.")
    old = info.copyright or ""
    new = one_line(COPYRIGHT)
    if old == new:
        print("Copyright is already what this script says.")
        return
    print(f"Copyright now: {repr(old)}")
    print(f"Copyright new: {repr(new)}")
    print(f"{len(new)} characters.")
    if DRY_RUN:
        print("Dry run. Nothing was changed.")
        return
    result = scripting.write_font_info(package, [(None, "copyright", old, new)],
                                       undo_name="Set copyright")
    print(f"{result['changed']} field changed.")


main()
```

Save it as `legal_fields.py`. The dry run prints:

```text
Trademark     <-- empty
License       <-- empty
License URL   <-- empty
Designer URL  http://www.dotcolon.net/
Manufacturer  <-- empty
Vendor        <-- empty
5 of 6 fields are empty. Fill them in File > Font Info.
Copyright now: ''
Copyright new: 'GG Plum by Sora Sagano. Released under CC0 1.0 Universal: no rights reserved. Practice copy for the Halfmoon book.'
114 characters.
Dry run. Nothing was changed.
```

Read the new line against the three lines at the top of the script, word by word. This is the proofreading step, and no check can do it for you. Then set `DRY_RUN = False` and run. The last line becomes `1 field changed.` Run it once more:

The first line and the last now read:

```text
5 of 6 fields are empty. Fill them in File > Font Info.
Copyright is already what this script says.
```

Notes on the listing.

The script compares before it writes. If the font already holds the line, it says so and stops, which makes it safe to run before every release. You can't write the notice twice, and you find out when somebody has changed it.

The old and new values are printed with `repr`, quotation marks and all. For text that has to be right to the letter, that's the honest way to print: a space at the end or a stray line break would show.

The change has `None` for its master, as the version fields did yesterday. The copyright belongs to the whole font.

The text has no © sign. The sign is legal in a font, but I haven't seen what this field does with characters outside plain ASCII, so the sample stays inside it. If your studio's wording needs the sign, run chapter 95's `font_names.py` afterwards and look at what came back.

## Fill in the rest by hand

For the five empty fields, open **File > Font Info** and find the legal and credits pages. For the practice font, the truthful entries are short. The license is the CC0 statement, and its address is `https://creativecommons.org/publicdomain/zero/1.0/`. There's no trademark and no vendor code, and leaving those empty is correct. An empty field is only a fault when something belongs in it.

That's why the script prints `<-- empty` and doesn't count errors. It can see that a field is blank. It can't know whether blank is right.

## Break it on purpose

Indent the three lines of text inside the triple quotes by four spaces, as if an editor had done it, and run the dry run. The new line should be the same 114 characters, because `one_line` strips each piece.

Now replace the body of `one_line` with `return text.replace("\n", " ").strip()` and run again. Count the characters and look at the spaces between the sentences. Put the function back.

## What the script can't do

It can't write the license, the trademark or the vendor code. The pattern for writing fields beyond the six text fields the guarded writer takes exists, and nobody has proved for these fields that it stores, undoes and saves correctly. Legal text is the last place to be the first to find out.

It doesn't know the law. It copies a text from the top of a file into a field. Whether the text is the right one is a question for Ines and the lawyer.

And it holds the wording inside the script, which means each font family would need its own copy of the script. Tomorrow's chapter moves settings like this one out of the code and into a file.

## What you learned

A triple-quoted string keeps text on several lines as you typed it, including the line breaks after the opening quotes and before the closing ones. `splitlines`, `strip` and `" ".join` turn such a block into one clean line, where `replace` would leave stray spaces. `repr` and `len` show text as it is stored, which is how you proofread a string that has to be right to the letter. Fly's writer accepts the copyright line and refuses the other legal fields, so the script reports those and a person fills them in.

## Try it yourself

1. Print the copyright line wrapped to the Output panel: put a line break after every full stop that ends a sentence. `replace` is enough here. What keeps the full stop in `1.0` from being cut?
2. Add a check to the report: a web address should start with `https://`. You met `startswith` in chapter 9. Which of Plum's fields fails, and is that yours to change?
3. The year in a real notice goes stale. Build the line `Copyright 2026 Halfmoon Type.` with the year taken from `date.today().year`, print it, and don't write it to the practice font.

## Next

Three masters share one copyright line because they live in one font. A family delivered as several files has no such luck. Chapter 99 keeps the shared values in one settings file and checks every open font against it.
