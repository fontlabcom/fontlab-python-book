---
this_file: src_docs/md/part5-words/095-the-font-has-a-name.md
---

# 95. The font has a name

Friday of week eighteen. The typesetter in Istanbul installs the three weights and writes back within the hour. Light and Bold sit in the font menu where she expects them. The Regular is listed apart from the other two, and her layout program calls it by a slightly different name.

Oskar takes the sheet from chapter 1 off the wall. Two lines are still open. He taps the first: family name and version in every weight. "Names," he says. "A font has about six of them, and they have to agree."

The names live in Font Info. Some belong to the whole font and some to each master. Today you read them all, in every master, and check them against a few rules. You change nothing yet. The tool of the day is a dictionary that lists the fields you care about, so that one loop can read them all.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The `tell` function from [chapter 39](../part2-a-toolbox/039-ask-the-user.md). The script below defines it again, so it runs by itself.

I couldn't run the code in FontLab 9. The field names come from the stub that describes FontLab's objects, and the values I print are the ones in Plum's source file. I ran the script in plain Python against a stand-in that holds those values. Reading a master's own names by switching to that master is how Fly's tools do it for the style name. For the full name and the PostScript name I'm assuming the same holds, and I haven't seen it.

## Step 1: One field, then many

You've read from `font.info` since chapter 11. The package has the same drawer:

```python
import fly.ap.core.scripting as scripting

package = scripting.current_package()
info = package.info
print(info.familyName)
print(info.openTypeNameDesigner)
```

```text
GG Plum
Sora Sagano
```

Two fields take two lines. Six fields would take six, and the report would need a label for each. Put the fields in a dictionary, with the attribute name as the key and the label as the value:

```python
FONT_WIDE = {
    "familyName": "Family",
    "openTypeNameDesigner": "Designer",
    "openTypeNameVersion": "Version name",
}
```

The keys are strings now, and `info."familyName"` isn't Python. The function that fetches an attribute by its name in a string is `getattr`:

```python
for key, label in FONT_WIDE.items():
    print(f"{label:<16}{getattr(info, key)}")
```

```text
Family          GG Plum
Designer        Sora Sagano
Version name    Version 1.000
```

`getattr(info, "familyName")` and `info.familyName` are the same question. The first form lets a table decide what to ask. Add a row to the table and the report grows by a line, with no new code.

## Step 2: The mistake

The rules for a name are string rules: not empty, no space at either end, no two spaces in a row. Mira adds a fourth row to the table, `"copyright": "Copyright"`, and a first check:

```python
for key, label in FONT_WIDE.items():
    value = getattr(info, key)
    if value != value.strip():
        print(label, "has a space at an end")
```

```text
AttributeError: 'NoneType' object has no attribute 'strip'
```

Plum has no copyright line. A text field that nobody has filled in reads as `None`, and `None` has no `strip`. Three fields worked, so the loop looked finished. The fourth was the first empty one.

Fly's own tools write `getattr(package.info, key) or ""`. You met `or` between two values in chapter 91: when the left side is empty or `None`, the right side is used. After that every value is a string, and "empty" is one more thing for the check to report:

```python
def read_fields(info, table):
    return {key: getattr(info, key) or "" for key in table}
```

This is a dictionary built in one line, the way chapter 37 built lists, with braces and a colon in place of the brackets: for each key in the table, the key and its value from the font.

## Step 3: Names that belong to a master

Family, designer and version are the same for the whole font. The style name isn't: Light, Regular and Bold each have their own. So do the full name and the PostScript name, which is the one programs use behind the scenes.

To read a master's names, make that master the current one, then ask:

```python
package.setMaster("Bold")
print(package.info.styleName)
```

That changes what the user sees. The font was showing Regular, and now it shows Bold. A report that leaves the font on another master than it found is rude, and it's confusing when a tool does that behind your back. Remember where you were and go back:

```python
original = package.master
for master in package.masters:
    package.setMaster(master)
    print(master, package.info.styleName)
package.setMaster(original)
```

There's a hole in this. If any line inside the loop raises an error, Python stops there, and the last line never runs. The font stays on whichever master the loop had reached. Python has a form for "do this afterward, no matter what":

```python
original = package.master
try:
    for master in package.masters:
        package.setMaster(master)
        print(master, package.info.styleName)
finally:
    package.setMaster(original)
```

You know `try` from chapter 19, where `except` caught an error. `finally` catches nothing. The error still stops the script and still prints its traceback. But on the way out, Python runs the `finally` lines first. Use it whenever a script borrows something it must hand back.

## Step 4: The house rules

How should the other names follow from family and style? Oskar's rules for Halfmoon:

- The full name is the family, a space, the style: `GG Plum Bold`.
- The PostScript name is the family without spaces, a hyphen, the style without spaces: `GGPlum-Bold`.

```python
def house_names(family, style):
    return {
        "postscriptFullName": f"{family} {style}",
        "postscriptFontName": family.replace(" ", "") + "-" + style.replace(" ", ""),
    }


print(house_names("GG Plum", "Bold"))
```

```text
{'postscriptFullName': 'GG Plum Bold', 'postscriptFontName': 'GGPlum-Bold'}
```

These are one foundry's rules. Other foundries leave "Regular" out of the full name, and a font made that way isn't broken. What matters is that the three weights of one family follow the same rule.

A PostScript name also has rules that aren't a matter of taste. It may hold only plain ASCII characters, no spaces, none of the ten bracket-like characters, and at most 63 characters in all. `isascii` asks a string whether all of it is ASCII:

```python
PS_LIMIT = 63
PS_FORBIDDEN = "[](){}<>/% "


def ps_problems(name):
    problems = []
    if len(name) > PS_LIMIT:
        problems.append(f"{len(name)} characters, limit {PS_LIMIT}")
    bad = [c for c in name if c in PS_FORBIDDEN or not c.isascii()]
    if bad:
        problems.append("not allowed: " + " ".join(repr(c) for c in bad))
    return problems


print(ps_problems("GGPlum-Bold"))
print(ps_problems("GG Plum-Café"))
```

```text
[]
["not allowed: ' ' 'é'"]
```

`repr` from chapter 19 puts quotes around each character, which is the only way to make a space visible in a report.

## The whole script

```python
#FLM: Font Names
# Prints the names in Font Info, font-wide and for each master,
# and checks them against the house rules. Changes nothing.
from fly import fl, qt
import fly.ap.core.scripting as scripting
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


FONT_WIDE = {
    "familyName": "Family",
    "openTypeNameDesigner": "Designer",
    "openTypeNameVersion": "Version name",
    "copyright": "Copyright",
}
PER_MASTER = {
    "styleName": "Style",
    "postscriptFullName": "Full name",
    "postscriptFontName": "PostScript name",
}
PS_LIMIT = 63
PS_FORBIDDEN = "[](){}<>/% "


def read_fields(info, table):
    return {key: getattr(info, key) or "" for key in table}


def house_names(family, style):
    return {
        "postscriptFullName": f"{family} {style}",
        "postscriptFontName": family.replace(" ", "") + "-" + style.replace(" ", ""),
    }


def text_problems(value):
    problems = []
    if value == "":
        problems.append("empty")
    if value != value.strip():
        problems.append("space at an end")
    if "  " in value:
        problems.append("two spaces in a row")
    return problems


def ps_problems(name):
    problems = []
    if len(name) > PS_LIMIT:
        problems.append(f"{len(name)} characters, limit {PS_LIMIT}")
    bad = [c for c in name if c in PS_FORBIDDEN or not c.isascii()]
    if bad:
        problems.append("not allowed: " + " ".join(repr(c) for c in bad))
    return problems


def show(label, value, problems):
    note = "   <-- " + ", ".join(problems) if problems else ""
    print(f"  {label:<16}{value}{note}")
    return len(problems)


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    count = 0
    print("Whole font")
    wide = read_fields(package.info, FONT_WIDE)
    for key, label in FONT_WIDE.items():
        count += show(label, wide[key], text_problems(wide[key]))

    original = package.master
    try:
        for master in package.masters:
            package.setMaster(master)
            names = read_fields(package.info, PER_MASTER)
            house = house_names(wide["familyName"], names["styleName"])
            print(master)
            for key, label in PER_MASTER.items():
                problems = text_problems(names[key])
                if key == "postscriptFontName":
                    problems = problems + ps_problems(names[key])
                if key in house and names[key] != house[key]:
                    problems.append(f"house rule says {house[key]}")
                count += show(label, names[key], problems)
    finally:
        package.setMaster(original)
    print(f"{count} things to look at.")


main()
```

Save it as `font_names.py`. If Plum's names reach the script the way they stand in the source file, it prints:

```text
Whole font
  Family          GG Plum
  Designer        Sora Sagano
  Version name    Version 1.000
  Copyright          <-- empty
Light
  Style           Light
  Full name       GG Plum Light
  PostScript name GGPlum-Light
Regular
  Style           Regular
  Full name       GG Plum   <-- house rule says GG Plum Regular
  PostScript name GGPlum   <-- house rule says GGPlum-Regular
Bold
  Style           Bold
  Full name       GG Plum Bold
  PostScript name GGPlum-Bold
3 things to look at.
```

There's the typesetter's Regular. Light and Bold carry their style in both names. The Regular carries it in neither, so a program that sorts by PostScript name files `GGPlum` away from `GGPlum-Bold`. The family name is the same in every weight, as it must be, since the font keeps only one. The weights disagree in the names built from it.

Notes on the listing.

The two tables are the script's memory of what to read. `FONT_WIDE` and `PER_MASTER` are kept apart because the two kinds are read differently, once or once per master.

`show` prints one line and returns the number of problems on it, so `main` can keep a count.

The script says "things to look at" and doesn't say "errors". An empty copyright line is a gap that chapter 98 fills. The Regular's names follow an older habit. A person decides what to change.

## Break it on purpose

Misspell a key in `PER_MASTER`: `"styleNmae"`. Put the font on Regular and run the script. The whole-font part prints, then:

```text
AttributeError: 'fgFontInfo' object has no attribute 'styleNmae'
```

The wording of the object's name may differ on your screen. Now look at the font. It should still be on Regular, though the script had switched to Light when it fell over. The `finally` lines ran on the way out.

To see what they saved you from, turn the two `finally` lines into comments, replace them with `except ZeroDivisionError:` and `pass` so the `try` stays legal, and run again. Same error, and the font is left on Light. Put the `finally` back and correct the key.

## What the script can't do

It doesn't write. Fly's guarded writer, `write_font_info`, accepts the family name, the style name, the designer, the copyright and the version name. It refuses the full name and the PostScript name with `Unsupported Font Info field`. I found no proven way to set those two from a script, so the Regular's names are a job for the Font Info window: open **File > Font Info**, find the names of the Regular master, and type what the report says. Then run the report again and expect one thing to look at, the copyright.

FontLab can also build these names from family and style on its own. Where that button is, and what it makes of "Regular", is a question for FontLab's manual and five minutes of trying.

## What you learned

A dictionary of field names and labels lets one loop read as many fields as the table has rows, and `getattr` fetches an attribute whose name is in a string. An unfilled text field reads as `None`, and `or ""` turns it into a string before any string method touches it. `try` with `finally` runs its last lines whether or not an error happens, which is how a script hands back what it borrowed. Some of a font's names belong to the whole font and some to each master, and a report has to visit each master to see them.

## Try it yourself

1. Add `"openTypeNameDesignerURL": "Designer URL"` to `FONT_WIDE`. What does Plum have there?
2. Some programs still cut PostScript names at 29 characters. Add a second, softer check to `ps_problems` that says `longer than 29` without calling it forbidden. Test it with a made-up name.
3. Write `same_everywhere(package, key)`, which visits every master, collects `getattr(package.info, key) or ""` in a set, and returns `True` when the set has one member. Use `try` and `finally`. Try it with `"familyName"` and with `"styleName"`.

## Next

The names are read and one of them is on its way to being repaired. Font Info also holds numbers, and three of them decide whether the top of an Å gets cut off on a web page. Chapter 96 reads the vertical metrics and sets one.
