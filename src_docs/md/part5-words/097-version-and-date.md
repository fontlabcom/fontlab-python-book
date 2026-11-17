---
this_file: src_docs/md/part5-words/097-version-and-date.md
---

# 97. Version and date

Tuesday of week nineteen. The typesetter in Istanbul writes again: the capital spacing in her headline still misses the Turkish İ. Mira fixed that in chapter 91, eight days ago. Which file is the typesetter using?

Nobody can say. The file she got on the Friday before the fix says Version 1.000. The file on Mira's disk, with the fix, the fractions and the repaired names, also says Version 1.000. Two different fonts carry the same label, and the only way to tell them apart is to open both and count glyphs.

"Every file that leaves the building gets a new number," Oskar says. "And we write down the day." He has a paper notebook for this, with gaps in it.

Today's script raises the version by one step, writes the version name to match, and adds a dated line to the font's note. The Python is small: whole numbers that roll over, and a format that pads a number with zeros.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py`.

I couldn't run the code in FontLab 9. I ran the script in plain Python against a stand-in that holds Plum's version fields and empty notes. The plan it builds has the same shape as the plan Fly's own version tool builds. I read that tool's source to see what the writer accepts. The dates below are from my run. Yours will be today's.

## Step 1: A version is two numbers and a name

Font Info keeps the version three times:

```python
import fly.ap.core.scripting as scripting

package = scripting.current_package()
info = package.info
print(info.versionMajor, info.versionMinor)
print(info.openTypeNameVersion)
```

```text
1 0
Version 1.000
```

The major number is the 1 before the point. The minor number is the part after it, a whole number from 0 to 999. The version name is what people see in a font menu or a file's properties. A script changes the two numbers, and then it has to rebuild the name, or the three will tell different stories.

## Step 2: The next number

Most releases raise the minor number by one. A big release raises the major number and starts the minor again at zero. And minor 999 has nowhere to go, so the step after 1.999 is 2.000:

```python
def next_version(major, minor, step):
    if step == "major":
        return major + 1, 0
    if minor == 999:
        return major + 1, 0
    return major, minor + 1


print(next_version(1, 0, "minor"))
print(next_version(1, 999, "minor"))
print(next_version(1, 37, "major"))
```

```text
(1, 1)
(2, 0)
(2, 0)
```

The function returns two numbers at once, as a tuple, the way `extremes` did yesterday. Three `return` lines, and Python leaves at the first one whose condition holds. You'll never reach 999 at Halfmoon's pace. The line is there because a function that takes any minor number should have an answer for every one.

## Step 3: The mistake

Mira builds the name with an f-string:

```python
major, minor = next_version(1, 0, "minor")
print(f"Version {major}.{minor}")
```

```text
Version 1.1
```

It looks right, and it's wrong by a factor of a hundred. Read as a decimal number, 1.1 is 1.100: minor 100, not minor 1. The next release would print 1.2, then 1.3, and the tenth would print 1.10, which sorts before 1.2 in every file list. The convention is three digits after the point, with zeros in front.

You've used the part after the colon in an f-string to set a width, since chapter 12. A zero in front of the width pads with zeros where spaces would go, and `d` says the value is a whole number:

```python
def version_name(major, minor):
    return f"Version {major}.{minor:03d}"


print(version_name(1, 1))
print(version_name(1, 42))
print(version_name(2, 0))
```

```text
Version 1.001
Version 1.042
Version 2.000
```

Now the name has a fixed shape, and that pays twice. Names sort in release order. And the script can test whether a font's name and numbers agree before it touches anything: build the name from the numbers, and compare.

## Step 4: The day

You met `date.today()` in chapter 18. It prints as year, month, day, and `isoformat()` gives that same text as a string you can glue to others:

```python
from datetime import date

line = f"{date.today().isoformat()}: {version_name(1, 1)}"
print(line)
```

```text
2026-11-17: Version 1.001
```

Year first is on purpose. Dates written this way sort correctly as plain text, and nobody has to wonder whether 11/12 is in November or December.

Where does the line go? Font Info has a field for the date a font was made, and I found no proven way to write it from a script. Fly's own version tool leaves it alone and adds a line to the font's **note** instead, a free text field for the people who work on the font. The note is kept per master, so the line goes into every master's note, after whatever is already there:

```python
def note_changes(package, line):
    changes = []
    original = package.master
    try:
        for master in package.masters:
            package.setMaster(master)
            old = package.info.note or ""
            new = old + "\n" + line if old else line
            changes.append((master, "note", old, new))
    finally:
        package.setMaster(original)
    return changes
```

`"\n"` is the line break from chapter 26. An empty note gets the line alone. A note with text in it gets a line break first, so each release sits on its own line. The function writes nothing. It builds the list of changes, four-part tuples as in chapter 96, and hands them back.

## The whole script

```python
#FLM: Bump Version
# Raises the font's version by one step, writes the version name to match,
# and adds a dated line to each master's note.
from datetime import date

import halfmoon
from fly import fl
import fly.ap.core.scripting as scripting

DRY_RUN = True
STEP = "minor"


def next_version(major, minor, step):
    if step == "major":
        return major + 1, 0
    if minor == 999:
        return major + 1, 0
    return major, minor + 1


def version_name(major, minor):
    return f"Version {major}.{minor:03d}"


def note_changes(package, line):
    changes = []
    original = package.master
    try:
        for master in package.masters:
            package.setMaster(master)
            old = package.info.note or ""
            new = old + "\n" + line if old else line
            changes.append((master, "note", old, new))
    finally:
        package.setMaster(original)
    return changes


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    info = package.info
    major = int(info.versionMajor)
    minor = int(info.versionMinor)
    old_name = info.openTypeNameVersion or ""
    if old_name != version_name(major, minor):
        print(f"The numbers say {version_name(major, minor)}, the name says {repr(old_name)}.")
        print("Make them agree in Font Info first. Nothing was changed.")
        return
    new_major, new_minor = next_version(major, minor, STEP)
    new_name = version_name(new_major, new_minor)
    line = f"{date.today().isoformat()}: {new_name}"
    changes = [
        (None, "versionMajor", info.versionMajor, new_major),
        (None, "versionMinor", info.versionMinor, new_minor),
        (None, "openTypeNameVersion", old_name, new_name),
    ] + note_changes(package, line)
    print(f"{old_name} -> {new_name}")
    print(f"Note line for {len(package.masters)} masters: {line}")
    if DRY_RUN:
        print("Dry run. Nothing was changed.")
        return
    result = scripting.write_font_info(package, changes, undo_name="Bump version")
    print(f"{result['changed']} fields changed.")


main()
```

Save it as `bump_version.py`. The dry run prints:

```text
Version 1.000 -> Version 1.001
Note line for 3 masters: 2026-11-17: Version 1.001
Dry run. Nothing was changed.
```

Set `DRY_RUN = False` and run it once:

```text
Version 1.000 -> Version 1.001
Note line for 3 masters: 2026-11-17: Version 1.001
6 fields changed.
```

Notes on the listing.

The three version fields have `None` where a master's name would go. They belong to the whole font. The three note changes name their master. All six go to the writer in one call, so they succeed or fail together and make one step in **Edit > Undo**. A font with a new number and the old name would be worse than a font nobody touched.

`int(...)` is around the two numbers because a number field may come back as `1.0`, and `:03d` refuses anything that isn't a whole number. The changes still carry the values as the font gave them, since the writer compares them with what it reads itself.

The check before the work is the fixed shape paying off. If someone typed `Version 1.0` into Font Info by hand, the script says so and stops. It could overwrite the name. It doesn't, because a name that disagrees with the numbers means a person did something the script doesn't understand.

Run it a second time on another day, and the Bold's note holds two lines:

```text
2026-11-17: Version 1.001
2026-11-20: Version 1.002
```

That's Oskar's notebook, kept inside the font, and nobody can forget to fill it in. To read it without a script, open **File > Font Info** and look for the note field of a master. When the typesetter next asks which file she has, the answer is in the file: she reads the version name in her font menu, and Mira reads the note to see what day that was and looks up what changed since.

## Break it on purpose

Set `DRY_RUN = True` again, so nothing is written. Change `STEP` to `"Minor"`, with a capital, and run. The script reports 1.002, or whatever comes next for you, and no error. `"Minor"` isn't `"major"`, so the first `if` is skipped, and everything that isn't `"major"` counts as a minor step. A typing slip passed for a valid choice.

Now try `STEP = "mayor"`. Same thing: a minor step, where you meant a major one. That's the dangerous direction. Make the function strict, with two new lines at its top:

```python
def next_version(major, minor, step):
    if step not in ("major", "minor"):
        raise ValueError(f"STEP must be 'major' or 'minor', not {repr(step)}")
    if step == "major":
        return major + 1, 0
    if minor == 999:
        return major + 1, 0
    return major, minor + 1
```

You've read `ValueError` at the bottom of Fly's refusals since chapter 88. Lines like this one raised them, and this is the first time you write one yourself. `raise` stops the script the way Python's own errors do, with your sentence at the bottom of the traceback. Use it when going on would mean guessing. Run again with `"mayor"`, read your own error message, and set `STEP` back to `"minor"`.

## What the script can't do

It can't know that a file left the building. It raises the number when you run it, and running it is still a decision. Part 6 builds the Friday export as one script, and that script is the right place to call this one, so the number and the export can't drift apart.

It doesn't touch the creation date in Font Info, for the reason given in step 4.

And one thing I haven't seen: whether undoing the six changes takes one **Edit > Undo** or several. Try it on the practice copy and write down what you find. If the note and the numbers come apart, run `font_names.py` from chapter 95 and correct the version by hand.

## What you learned

A font's version lives in two whole numbers and a name, and a script that changes one has to change all three in the same call. `{minor:03d}` pads a whole number with zeros to three digits, which keeps version names in a fixed shape that sorts and can be checked. `date.today().isoformat()` gives the day as year, month and day, and a dated line in each master's note is a release log that travels with the font. `raise ValueError(...)` lets your own function refuse a value that it would otherwise have to guess about.

## Try it yourself

1. Call `next_version` with minor 998, 999 and 0, for both steps, and check the six answers against what you expect before you run them.
2. Write `parse_version(name)`, which takes `"Version 1.042"` and returns `(1, 42)`. Use `split`. What should it do with `"1.042"`, without the word?
3. Print the Regular's note as a numbered list of releases, newest first. `splitlines` from chapter 87 gives the lines, and `reversed(lines)` hands a list over back to front.

## Next

The font says which release it is. It still doesn't say whose it is: Plum has no copyright line, as chapter 95's report keeps pointing out. Chapter 98 writes one that spans several lines, and looks at the legal fields a script can only read.
